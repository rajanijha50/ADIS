from automation.llm_handler import handle_llm_query
from automation.message_chatbot import handle_message_chatbot
from fastapi import APIRouter, Response
from pydantic import BaseModel
import base64
from typing import Any
from core.command_dispatcher import command_dispatcher
from voice.tts import synthesize_to_bytes
from voice.stt import listen_to_user, listen_to_user2
from db.sqliteDB import add_message, get_connection, get_session, update_session_title

router = APIRouter()

class VoiceCompletionRequest(BaseModel):
    email: str
    session: int = 0
    # query: str

def helper(success: bool, message: str, data: Any = None):
    return {
        "success": success,
        "message": message,
        "data": data
    }

async def helper_with_audio(success: bool, text: str, response_message: Any = None):
    
    if response_message is None:
        response_message = text
    audio_bytes = await synthesize_to_bytes(response_message)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return {
        "success": success,
        "text": text,
        "audio_b64": audio_b64
    }

@router.post('/api/voice/completion')
async def voice_completion(request: VoiceCompletionRequest):
    if not request.session or not request.email:
        return await helper_with_audio(False, "Session ID and Email are required")

    query = listen_to_user2()
    if not query:
        return await helper_with_audio(False, "I couldn't hear that. Could you please repeat?")

    print("\nQuery: ", query)
    try:
        conn = get_connection()
        session_data = get_session(conn, request.session)
        if session_data["message_count"] == 0:
            try:
                session_title = handle_message_chatbot(f'generate a short title for the first user input of a conversation: {query}')
                update_session_title(conn, request.session, session_title)
            except Exception as e:
                print(f"Error generating session title: {e}")
        
        dispatcher_response = command_dispatcher(query)
        print("Dispatcher response: ", dispatcher_response)
        if dispatcher_response.get("success") is False:
            return await helper_with_audio(False, "Command not recognized or failed to execute")

        response_message = dispatcher_response.get("response")
        intent = dispatcher_response.get("intent")
        if dispatcher_response.get("intent") == "general_query":
            llm_response = handle_llm_query(
                user_input=query,
                email=request.email,
                session_id=request.session,
                input_type="voice",
                intent="general_query"
            )
            # no need to store it. llm_handler already stores the user message and assistant response in the database
            return await helper_with_audio(True, llm_response, llm_response)

        # Store user message
        add_message(conn, session_id=request.session, role="user", content=query, intent=intent, input_type="voice")
        # Store assistant response
        add_message(conn, session_id=request.session, role="assistant", content=response_message, input_type="voice")
        print(f"Intent: {intent}, Response message: {response_message}")

        return await helper_with_audio(True, response_message, response_message)

    except Exception as e:
        print(f"Voice completion error: {e}")
        return await helper_with_audio(False, str(e))


