from fastapi import APIRouter

router = APIRouter()

@router.post('/api/voice/commands')
async def voice_command(query: str):
    """Handles the voice commands"""
    pass




