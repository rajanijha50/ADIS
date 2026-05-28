from fastapi import APIRouter

router = APIRouter()

@router.post("/api/text/completion")
async def text_completion(request):
    """Handles the text inputs"""
    pass
        



