from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()

@router.get("/")
def check():
    return { "message": "queue endpoint" }
