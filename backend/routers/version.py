from fastapi import APIRouter

from src.version import get_version_info


router = APIRouter()


@router.get("/version")
def version_info() -> dict:
    return get_version_info()
