from fastapi import APIRouter
from pydantic import BaseModel
from db.sqliteDB import get_connection, create_session, get_all_sessions, get_recent_messages, delete_session

router = APIRouter()
class SessionEmailRequest(BaseModel):
    email: str

class SessionIdRequest(BaseModel):
    session_id: int

def helper(success: bool, message: str, data=None):
    return {
        "success": success,
        "message": message,
        "data": data
    }

@router.post("/api/session/create")
async def create_session_endpoint(request: SessionEmailRequest):
    """Creates a new session"""
    try:
        conn = get_connection()
        session_id = create_session(conn, email=request.email)
        return helper(True, "new session created", session_id)
    except Exception as e:
        print(f"Error in Sessions: {e}")
        return helper(False, "error creating session", str(e))

@router.get("/api/session/list/{email}")
async def list_sessions_endpoint(email: str):
    """Lists all the sessions"""
    try:
        conn = get_connection()
        session_list = get_all_sessions(conn, email=email)
        return helper(True, "sessions retrieved", session_list)
    except Exception as e:
        print(f"Error in Sessions: {e}")
        return helper(False, "error listing sessions", str(e))

@router.get("/api/session/{session_id}/messages")
async def get_messages_endpoint(session_id: int):
    """Gets all the messages from a session"""
    try:
        conn = get_connection()
        messages = get_recent_messages(conn, session_id=session_id)
        return helper(True, "messages retrieved", messages)
    except Exception as e:
        print(f"Error in Sessions: {e}")
        return helper(False, "error getting messages", str(e))

@router.delete("/api/session/delete")
async def delete_session_endpoint(request: SessionIdRequest):
    """Deletes a session"""
    try:
        conn = get_connection()
        # call the DB delete_session with positional arg to avoid keyword name mismatch
        delete_session(conn, request.session_id)
        return helper(True, "session deleted", None)
    except Exception as e:
        print(f"Error in Sessions: {e}")
        return helper(False, "error deleting session", str(e))