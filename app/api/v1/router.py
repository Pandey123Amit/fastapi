from fastapi import APIRouter

from app.api.v1.endpoints import auth, courses, students

api_router = APIRouter()
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
api_router.include_router(
    students.router,
    prefix="/students",
    tags=["students"],
)
api_router.include_router(
    courses.router,
    prefix="/courses",
    tags=["courses"],
)
