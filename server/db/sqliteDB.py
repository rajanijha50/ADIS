from pathlib import Path
import sqlite3
import json
from db.utils import now

# db path
current_dir = Path(__file__).parent
DB_PATH = current_dir / "adis_sqlite.db"


# connection helper
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # to enforce FK constraints
    conn.row_factory = sqlite3.Row            # to return dict-like rows
    return conn

# schema creation: using email as the unique identifier. all tables reference it as a foreign key.
def create_tables(conn: sqlite3.Connection):

    # 1 users table: user details
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL ,
            email       TEXT    NOT NULL UNIQUE,
            contact     TEXT,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2 user_preferences table: stores LLM provider settings and assistant behaviour preferences.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            pref_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT    NOT NULL,
            llm_provider  TEXT    NOT NULL DEFAULT 'groq',
            llm_model     TEXT    NOT NULL DEFAULT 'llama-3.3-70b-versatile',
            api_key       TEXT,
            tone          TEXT    NOT NULL DEFAULT 'formal',
            language      TEXT    NOT NULL DEFAULT 'en',
            max_tokens    INTEGER NOT NULL DEFAULT 1024,
            temperature   REAL    NOT NULL DEFAULT 0.7,
            system_prompt TEXT,
            updated_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)

    # 3 user_memory table: universal key-value store for persistent facts about the user.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            memory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT    NOT NULL,
            key         TEXT    NOT NULL,
            value       TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)

    # auto-update updated_at whenever a user_memory row is modified
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_user_memory_updated_at
        AFTER UPDATE ON user_memory
        FOR EACH ROW
        BEGIN
            UPDATE user_memory
            SET updated_at = CURRENT_TIMESTAMP
            WHERE memory_id = OLD.memory_id;
        END
    """)

    # 4 sessions table: tracks conversation sessions.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT    NOT NULL,
            title         TEXT    NOT NULL DEFAULT 'Untitled',
            summary       TEXT,
            message_count INTEGER NOT NULL DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ended_at      TEXT,
            is_active     INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)

    # 5 messages table: stores individual messages details for each session.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'user',
            content     TEXT    NOT NULL,
            intent      TEXT,
            input_type  TEXT    NOT NULL DEFAULT 'text',
            tokens_used INTEGER,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    print("[OK] All tables created.")


# HELPER FUNCTIONS:


# user preferences helpers
def upsert_user_preferences(conn: sqlite3.Connection, email: str, **kwargs) -> None:
    """
    Insert or update preferences for a user."""
    existing = conn.execute(
        "SELECT pref_id FROM user_preferences WHERE email = ?", (email,)
    ).fetchone()

    if existing:
        if not kwargs:
            return
        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        set_clause += ", updated_at = ?"
        values = list(kwargs.values()) + [now(), email]
        conn.execute(
            f"UPDATE user_preferences SET {set_clause} WHERE email = ?", values
        )
    else:
        conn.execute(
            """
            INSERT INTO user_preferences
                (email, llm_provider, llm_model, api_key, tone, language,
                 max_tokens, temperature, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email,
                kwargs.get("llm_provider", "groq"),
                kwargs.get("llm_model", "llama-3.3-70b-versatile"),
                kwargs.get("api_key", None),
                kwargs.get("tone", "formal"),
                kwargs.get("language", "en"),
                kwargs.get("max_tokens", 1024),
                kwargs.get("temperature", 0.7),
                now(),
            ),
        )
    conn.commit()

def get_user_preferences(conn: sqlite3.Connection, email: str) -> dict:
    """Return user preferences as a plain dict. Returns defaults if none set."""
    row = conn.execute(
        "SELECT * FROM user_preferences WHERE email = ?", (email,)
    ).fetchone()
    if row:
        return dict(row)
    return {
        "llm_provider": "groq",
        "llm_model": "llama-3.3-70b-versatile",
        "api_key": None,
        "tone": "formal",
        "language": "en",
        "max_tokens": 1024,
        "temperature": 0.7,
    }

# user memory helpers
def upsert_memory(conn: sqlite3.Connection, email: str, key: str, value: str) -> None:
    """
    Write a universal memory fact for the user.
    Updates the existing row if the key already exists.
    """
    existing = conn.execute(
        "SELECT memory_id FROM user_memory WHERE email = ? AND key = ?",
        (email, key),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE user_memory SET value = ? WHERE email = ? AND key = ?",
            (value, email, key),
        )
    else:
        conn.execute(
            "INSERT INTO user_memory (email, key, value, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (email, key, value, now(), now()),
        )
    conn.commit()

def get_all_memory(conn: sqlite3.Connection, email: str) -> list[dict]:
    """Return all universal memory facts for a user as a list of dicts."""
    rows = conn.execute(
        "SELECT key, value FROM user_memory WHERE email = ? ORDER BY key",
        (email,),
    ).fetchall()
    return [dict(row) for row in rows]

def delete_memory(conn: sqlite3.Connection, email: str, key: str) -> None:
    conn.execute(
        "DELETE FROM user_memory WHERE email = ? AND key = ?", (email, key)
    )
    conn.commit()

# user helpers
def create_user(conn: sqlite3.Connection, name: str, email: str) -> int:
    """Insert a new user. Returns the new user_id."""
    cur = conn.execute(
        "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)",
        (name, email, now()),
    )
    conn.commit()
    # create default preferences for the new user
    upsert_user_preferences(conn, email)
    return cur.lastrowid

def get_user(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()

def update_user(conn: sqlite3.Connection, email: str, name: str, contact: str) -> None:
    """
    Update user fields."""
    conn.execute(
        "UPDATE users SET name = ?, contact = ? WHERE email = ?", (name, contact, email)
    )
    conn.commit()

# session and messages helpers
def create_session(conn: sqlite3.Connection, email: str, title: str = "Untitled") -> int:
    """Open a new session. Returns the new session_id."""
    cur = conn.execute(
        "INSERT INTO sessions (email, title, created_at) VALUES (?, ?, ?)",
        (email, title, now()),
    )
    conn.commit()
    return cur.lastrowid

def get_all_sessions(conn: sqlite3.Connection, email: str) -> list[dict]:
    """Return all sessions for a user as a list of dicts."""
    rows = conn.execute(
        "SELECT session_id, title, created_at FROM sessions WHERE email = ? ORDER BY created_at DESC",
        (email,),
    ).fetchall()
    return [dict(row) for row in rows]

def get_session(conn: sqlite3.Connection, session_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
    ).fetchone()

def update_session_title(conn: sqlite3.Connection, session_id: int, title: str) -> None:
    """Update the title of a session."""
    title = title.replace('"','').replace("'",'').replace("-",'').replace('*','')
    conn.execute(
        "UPDATE sessions SET title = ? WHERE session_id = ?", (title, session_id)
    )
    conn.commit()

def update_session_summary(conn: sqlite3.Connection, session_id: int, summary: str) -> None:
    """Persist the rolling summary after a summarisation cycle."""
    conn.execute(
        "UPDATE sessions SET summary = ? WHERE session_id = ?",
        (summary, session_id),
    )
    conn.commit()

def get_active_session(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    """Return the most recent active session for a user, if any."""
    return conn.execute(
        """
        SELECT * FROM sessions
        WHERE email = ? AND is_active = 1
        ORDER BY created_at DESC LIMIT 1
        """,
        (email,),
    ).fetchone()

def delete_session(conn: sqlite3.Connection, session_id: int) -> None:
    """
    Delete all messages for a specific session along with the session itself.
    """
    conn.execute(
        "DELETE FROM messages WHERE session_id = ?",
        (session_id,),
    )
    conn.execute(
        "DELETE FROM sessions WHERE session_id = ?",
        (session_id,),
    )
    conn.commit()


# message helpers
def add_message(
    conn: sqlite3.Connection,
    session_id: int,
    role: str,
    content: str,
    intent: str = None,
    input_type: str = "voice",
    tokens_used: int = None,
) -> int:
    """
    Insert one message and increment the session's message_count.
    Returns the new message_id.
    """
    cur = conn.execute(
        """
        INSERT INTO messages
            (session_id, role, content, intent, input_type, tokens_used, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, role, content, intent, input_type, tokens_used, now()),
    )
    conn.execute(
        "UPDATE sessions SET message_count = message_count + 1 WHERE session_id = ?",
        (session_id,),
    )
    conn.commit()
    return cur.lastrowid

def get_recent_messages(
    conn: sqlite3.Connection, session_id: int, limit: int = 20
) -> list[dict]:
    """
    Return the most recent `limit` messages for a session, oldest first.
    These form Layer 3 (verbatim recent context) in the LLM prompt.
    """
    rows = conn.execute(
        """
        SELECT message_id, role, content, created_at FROM messages
        WHERE session_id = ?
        ORDER BY message_id DESC
        LIMIT ?
        """,
        (session_id, limit),
    ).fetchall()
    # Reverse so oldest is first — correct order for LLM messages[]
    return [dict(row) for row in reversed(rows)]

def get_messages_to_summarise(
    conn: sqlite3.Connection, session_id: int, keep_last: int = 10
) -> list[dict]:
    """
    Return all messages EXCEPT the most recent `keep_last`.
    These are the old turns that will be compressed into a summary.
    """
    total = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,)
    ).fetchone()[0]

    to_summarise_count = total - keep_last
    if to_summarise_count <= 0:
        return []

    rows = conn.execute(
        """
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT ?
        """,
        (session_id, to_summarise_count),
    ).fetchall()
    return [dict(row) for row in rows]

def delete_old_messages(
    conn: sqlite3.Connection, session_id: int, keep_last: int = 10
) -> None:
    """
    Delete all messages except the most recent `keep_last` for a session.
    Called after summarisation to trim the table.
    """
    conn.execute(
        """
        DELETE FROM messages
        WHERE session_id = ?
          AND message_id NOT IN (
              SELECT message_id FROM messages
              WHERE session_id = ?
              ORDER BY created_at DESC
              LIMIT ?
          )
        """,
        (session_id, session_id, keep_last),
    )
    conn.commit()


# seed random dev data for testing and local development
def seed_dev_data():
    """
    Creates the schema and inserts one test user with preferences,
    a couple of memory facts, one session, and two messages.
    Safe to run multiple times — skips if user already exists.
    """
    conn = get_connection()
    create_tables(conn)

    # Check if test user already exists
    existing = conn.execute(
        "SELECT user_id FROM users WHERE email = ?", ("bittujha9142@gmail.com",)
    ).fetchone()

    if not existing:
        uid = create_user(conn, name="Baburao", email="bittujha9142@gmail.com")
        print(f"[OK] Test user created → user_id={uid}")

        upsert_user_preferences(
            conn, "bittujha9142@gmail.com",
            llm_provider="groq",
            llm_model="llama-3.3-70b-versatile",
            tone="formal",
            temperature=0.7,
            max_tokens=1024,
            system_prompt="You are a helpful AI assistant.",
        )
        print("[OK] Preferences set.")

        upsert_memory(conn, "bittujha9142@gmail.com", "occupation", "student developer")
        upsert_memory(conn, "bittujha9142@gmail.com", "project", "voice-based desktop assistant called ADIS")
        upsert_memory(conn, "bittujha9142@gmail.com", "preference", "prefers concise answers")
        print("[OK] User memory seeded.")

        sid = create_session(conn, "bittujha9142@gmail.com", title="Random Session")
        print(f"[OK] Session created → session_id={sid}")

        add_message(conn, sid, role="user",      content="Hello ADIS!", intent="general_query")
        add_message(conn, sid, role="assistant", content="Hi Baburao! How can I help you today?")
        print("[OK] Messages inserted.")
    else:
        print("[i] Test user already exists — skipping seed.")

    conn.close()



