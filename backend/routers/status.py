from typing import Any

from fastapi import APIRouter, HTTPException

from services.github_client import GitHubError, get_json_file, list_workflow_runs

router = APIRouter(tags=["status"])


@router.get("/status")
async def get_status() -> dict[str, Any]:
    try:
        recent_runs = await list_workflow_runs("pipeline.yml", limit=1)
    except GitHubError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    last_run = recent_runs[0] if recent_runs else None
    analytics = await get_json_file("data/analytics.json") or {}

    return {
        "last_run": (
            {
                "status": last_run.get("status") if last_run else None,
                "conclusion": last_run.get("conclusion") if last_run else None,
                "started_at": last_run.get("run_started_at") if last_run else None,
                "url": last_run.get("html_url") if last_run else None,
            }
            if last_run
            else None
        ),
        "analytics": analytics,
    }
