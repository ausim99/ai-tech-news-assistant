import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException

from services.github_client import get_json_file

router = APIRouter(prefix="/news", tags=["news"])

DHAKA = ZoneInfo("Asia/Dhaka")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _today() -> str:
    return datetime.now(DHAKA).strftime("%Y-%m-%d")


@router.get("/today")
async def get_today() -> Any:
    data = await get_json_file(f"data/daily/{_today()}.json")
    if data is None:
        raise HTTPException(status_code=404, detail="No digest generated for today yet")
    return data


@router.get("/date/{date}")
async def get_by_date(date: str) -> Any:
    if not DATE_RE.match(date):
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")
    data = await get_json_file(f"data/daily/{date}.json")
    if data is None:
        raise HTTPException(status_code=404, detail=f"No digest found for {date}")
    return data


@router.get("/history")
async def get_history() -> Any:
    data = await get_json_file("data/history.json")
    return data or []


@router.get("/category/{category}")
async def get_by_category(category: str) -> Any:
    data = await get_json_file(f"data/daily/{_today()}.json")
    if data is None:
        raise HTTPException(status_code=404, detail="No digest generated for today yet")

    items = data.get("items", []) if isinstance(data, dict) else []
    matched = [item for item in items if item.get("category", "").lower() == category.lower()]
    return matched
