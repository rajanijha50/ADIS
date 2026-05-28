from fastapi.routing import APIRouter
router = APIRouter()

@router.get("/api/user/profile")
async def get_user_profile(preferences):
    """Gets the user profile"""
    pass

@router.get("/api/user/preferences")
async def get_user_preferences(preferences):
    """Gets the user preferences"""
    pass

@router.patch("/api/user/preferences")
async def update_user_preferences(preferences):
    """Modifies the user preferences"""
    pass

@router.patch("/api/user/profile")
async def update_user_profile(profile):
    """Modifies the user profile"""
    pass