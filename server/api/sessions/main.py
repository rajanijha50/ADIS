# handle everything related to sessions
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/sessions/create")
async def create_new_session(request):
    """Creates a new session"""
    pass

@router.get("/api/sessions/list")
async def list_sessions(request):
    """Lists all the sessions"""
    pass

@router.get("/api/sessions/messages")
async def get_messages(request):
    """Gets all the messages from a session"""
    pass

@router.delete("/api/sessions/delete")
async def delete_session(request):
    """Deletes a session"""
    pass