from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.github_client import GitHubError, list_workflow_runs, trigger_workflow

router = APIRouter(tags=["workflows"])

WORKFLOW_FILES = ["pipeline.yml", "manual-run.yml", "healthcheck.yml", "cleanup.yml"]


class RunRequest(BaseModel):
    skip_send: bool = False
    dry_run: bool = False


@router.get("/workflows")
async def get_workflows() -> dict[str, list[Any]]:
    try:
        runs = {name: await list_workflow_runs(name, limit=5) for name in WORKFLOW_FILES}
    except GitHubError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return runs


@router.post("/run")
async def run_pipeline(body: RunRequest) -> dict[str, str]:
    try:
        await trigger_workflow(
            "manual-run.yml",
            {"skip_send": body.skip_send, "dry_run": body.dry_run},
        )
    except GitHubError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"status": "dispatched"}


@router.post("/send")
async def resend_digest() -> dict[str, str]:
    try:
        await trigger_workflow("manual-run.yml", {"resend_only": True})
    except GitHubError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"status": "dispatched"}
