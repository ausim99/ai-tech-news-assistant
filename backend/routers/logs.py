from typing import Any

from fastapi import APIRouter

from services.github_client import get_json_file

router = APIRouter(tags=["logs"])


@router.get("/logs")
async def get_logs() -> Any:
    data = await get_json_file("data/logs.json")
    return data or []
