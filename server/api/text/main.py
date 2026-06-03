from db.sqliteDB import update_session_title
from automation.message_chatbot import handle_message_chatbot
from db.sqliteDB import get_session
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from typing import Any
from db.sqliteDB import add_message, get_connection
from core.command_dispatcher import command_dispatcher
from automation.llm_handler import handle_llm_query

router = APIRouter()

class ChatCompletionRequest(BaseModel):
    email: str
    session: int = 0
    query: str

def helper(success: bool, message: str, data: Any = None):
    return {
        "success": success,
        "message": message,
        "data": data
    }

# def add_to_database(session_id: int, query: str, response: str, intent: str = None):
#     if not session_id or not query:
#         print("Missing required parameters for database insertion.")
#         return helper(False, "Missing required parameters for database insertion.")

#     try:
#         if intent and response:
#             conn = get_connection()
#             add_message(conn, session_id=session_id, role="user", content=query, intent=intent, input_type="text")
#             add_message(conn, session_id=session_id, role="assistant", content=response)
#         return helper(True, "Messages added to database successfully.", data = response)
#     except Exception as e:
#         print(f"Database insertion error: {e}")
#         return helper(False, f"Database insertion error: {str(e)}")


@router.post("/api/text/completion")
async def chat_completion(request: ChatCompletionRequest):
    print("request: ", request)
    try:
        if not request.session:
            return helper(False, "Session ID is required for LLM queries")

        conn = get_connection()
        session_data = get_session(conn, request.session)
        if session_data["message_count"] == 0:
            try:
                session_title = handle_message_chatbot(f'generate a short title for the first user input of a conversation: {request.query}')
                update_session_title(conn, request.session, session_title)
            except Exception as e:
                print(f"Error generating session title: {e}")
        
        dispatcher_response = command_dispatcher(request.query)
        print("Dispatcher response: ", dispatcher_response)
        if dispatcher_response.get("success") is False:
            return helper(False, "Command not recognized or failed to execute")

        intent = dispatcher_response.get("intent")
        if intent == "general_query":
            llm_response = handle_llm_query(
                user_input=request.query,
                email=request.email,
                session_id=request.session,
                input_type="text",
                intent="general_query"
            )
            return helper(True, "LLM query processed successfully.", data=llm_response)

        response_message = dispatcher_response.get("response")
        # add user input and assistant response to database
        add_message(conn, session_id=request.session, role="user", content=request.query, intent=intent, input_type="text")
        add_message(conn, session_id=request.session, role="assistant", content=response_message, input_type="text")
        return helper(True, "Command processed successfully.", data=response_message)

    except Exception as e:
        print(f"Text completion error: {e}")
        return helper(False, str(e))
        

