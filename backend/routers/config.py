from typing import Any

from fastapi import APIRouter

from services.github_client import get_json_file

router = APIRouter(tags=["config"])


@router.get("/config")
async def get_config() -> Any:
    data = await get_json_file("data/config.json")
    return data or {"sources": []}
