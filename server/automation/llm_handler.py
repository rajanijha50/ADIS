from db.sqliteDB import upsert_memory
from db.sqliteDB import (
    get_connection,
    get_user_preferences,
    get_all_memory,
    get_session,
    get_recent_messages,
    get_messages_to_summarise,
    add_message,
    update_session_summary,
    delete_old_messages,
    create_session,
    get_active_session,
)
from automation.message_chatbot import handle_message_chatbot


# constants for LLM handler behavior
RECENT_MESSAGES_LIMIT = 20
SUMMARISE_THRESHOLD = 30
KEEP_AFTER_SUMMARISE = 10


# system prompt builder (Layer 1 + Layer 2)
def _build_system_prompt(conn, email: str, session_id: int, prefs: dict) -> str:
    """
    Assemble the system prompt from three sources:

    [A] Assistant persona + tone instructions  (always present)
    [B] User universal memory facts            (always present, from user_memory table)
    [C] Session rolling summary                (present only if a summary exists = Layer 2)

    Returns a single formatted string ready to pass as system_prompt.
    """

    # ── [A] Persona block ───────────────────
    tone_instructions = {
        "friendly":  "You are ADIS(Advanced desktop intelligence system), a friendly and warm voice assistant. Keep responses conversational and natural for speech output. Avoid markdown, bullet points, or any formatting — speak in plain sentences.",
        "formal":    "You are ADIS(Advanced desktop intelligence system), a professional voice assistant. Maintain a formal and precise tone. Avoid markdown formatting — respond in clear, structured sentences suitable for text-to-speech.",
        "concise":   "You are ADIS(Advanced desktop intelligence system), a concise voice assistant. Give the shortest accurate answer possible. Avoid markdown and any unnecessary elaboration. Every word should serve the spoken response.",
    }
    tone = prefs.get("tone", "friendly")
    persona_block = tone_instructions.get(tone, tone_instructions["friendly"])

    # ── [B] Universal memory block ──────────
    memory_rows = get_all_memory(conn, email)
    if memory_rows:
        memory_lines = "\n".join(f"  - {row['key']}: {row['value']}" for row in memory_rows)
        memory_block = f"\n\nWhat you know about the user:\n{memory_lines}"
    else:
        memory_block = ""

    # ── [C] Session summary block (Layer 2) ─
    session = get_session(conn, session_id)
    summary = session["summary"] if session else None

    if summary:
        summary_block = f"\n\nSummary of earlier conversation:\n{summary}"
    else:
        summary_block = ""

    return persona_block + memory_block + summary_block



#  LAYER 3 — Recent conversation turns
def _build_message_with_history(conn, session_id: int, current_message: str) -> str:
    recent = get_recent_messages(conn, session_id, limit=RECENT_MESSAGES_LIMIT)

    if not recent:
        # First message in the session — no history to prepend
        return current_message

    transcript_lines = []
    for msg in recent:
        label = "User" if msg["role"] == "user" else "Assistant"
        transcript_lines.append(f"{label}: {msg['content']}")

    transcript = "\n".join(transcript_lines)

    return (
        f"[Previous conversations]\n"
        f"{transcript}\n\n"
        f"[Current message]\n"
        f"User: {current_message}"
    )


# summarization
def _summarise_session(conn, session_id: int, email: str, prefs: dict) -> None:
    old_turns = get_messages_to_summarise(conn, session_id, keep_last=KEEP_AFTER_SUMMARISE)
    if not old_turns:
        return

    # Build a transcript of the turns to be summarised
    transcript_lines = []
    for msg in old_turns:
        label = "User" if msg["role"] == "user" else "Assistant"
        transcript_lines.append(f"{label}: {msg['content']}")
    transcript = "\n".join(transcript_lines)

    # Include the existing summary so context is never lost across multiple cycles
    existing_summary = get_session(conn, session_id)["summary"]
    if existing_summary:
        context_prefix = (
            f"Previous summary:\n{existing_summary}\n\n"
            f"New conversation turns to incorporate:\n"
        )
    else:
        context_prefix = "Conversation turns to summarise:\n"

    summarise_prompt = (
        f"{context_prefix}"
        f"{transcript}\n\n"
        f"Write a concise factual summary of the above, preserving all important "
        f"topics, decisions, facts, and user preferences mentioned. "
        f"Write in third person. Do not add any commentary."
    )

    summary_system = (
        "You are a memory summarisation assistant. "
        "Your job is to compress conversation history into a short, accurate summary "
        "that another AI can use as context. Be factual and concise."
    )

    new_summary = handle_message_chatbot(
        query=summarise_prompt,
        llm_provider=prefs["llm_provider"],
        llm_model=prefs["llm_model"],
        tone="concise",          # always concise for summaries
        language=prefs.get("language", "en"),
        max_tokens=512,          # summaries should be short
        temperature=0.3,         # low temperature = more factual
        system_prompt=summary_system,
    )

    update_session_summary(conn, session_id, new_summary)
    delete_old_messages(conn, session_id, keep_last=KEEP_AFTER_SUMMARISE)
    print(f"[llm_handler] Session {session_id} summarised. Old turns trimmed.")


# session management
def get_or_create_session(conn, email: str) -> int:
    """
    Return the active session_id for this user, or open a new one.
    Called by the dispatcher before the first message of a session.
    """
    active = get_active_session(conn, email)
    if active:
        return active["session_id"]
    session_id = create_session(conn, email, title="Untitled")
    print(f"[llm_handler] New session opened → session_id={session_id}")
    return session_id


# main handler
def handle_llm_query(
    user_input: str,
    email: str,
    session_id: int,
    input_type: str = "voice",
    intent: str = "general_query",
) -> str:
    conn = get_connection()

    try:
        # step 1: Load user preferences ───
        prefs = get_user_preferences(conn, email)
        print('\n\n✅ user pref from db: ', prefs)


        # step 2: Build system prompt (Layer 1 + Layer 2) ──
        system_prompt = _build_system_prompt(conn, email, session_id, prefs)
        print('\n\n✅ system prompt: ', system_prompt)

        # step 3: Build message with history (Layer 3 + current) ──
        full_message = _build_message_with_history(conn, session_id, user_input)
        print('\n\n✅ full message: ', full_message)

        # step 4: Call the LLM ─────────────
        response = handle_message_chatbot(
            query=full_message,
            llm_provider=prefs["llm_provider"],
            llm_model=prefs["llm_model"],
            tone=prefs["tone"],
            language=prefs["language"],
            max_tokens=prefs["max_tokens"],
            temperature=prefs["temperature"],
            system_prompt=system_prompt,
        )
        print('\n\n✅ final response in llm_handler: ', response)

        # step 5: Persist the new turn ─────
        add_message(
            conn, session_id,
            role="user",
            content=user_input,   # store the raw message, not the transcript
            intent=intent,
            input_type=input_type,
        )
        add_message(
            conn, session_id,
            role="assistant",
            content=response,
            input_type="text",      # assistant response is always text
        )

        # step 6: Summarise if needed ──────
        session = get_session(conn, session_id)
        if session and session["message_count"] > SUMMARISE_THRESHOLD:
            _summarise_session(conn, session_id, email, prefs)

        return response

    except Exception as e:
        print(f"[llm_handler] ERROR: {e}")
        return "I'm sorry, I ran into an issue processing your request."

    finally:
        conn.close()


# memory update handler
def handle_memory_update(conn, email: str, key: str, value: str) -> str:
    """
    Write a fact to universal memory. Called by the dispatcher when the user
    says something like 'remember that I prefer formal responses'.

    The dispatcher's entity extractor should parse the key/value
    before calling this.
    """
   
    upsert_memory(conn, email, key, value)
    return f"Got it — I'll remember that your {key} is {value}."

# handle_llm_query('bittujha914@gmail.com', 11, "What is the weather today?", intent="weather_query", input_type="voice")