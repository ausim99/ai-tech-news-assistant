"""Thin async client over the GitHub REST API.

Used by the dashboard backend to read committed JSON data straight from the
repo (no redeploy needed to see fresh data) and to trigger workflow runs.
"""

import json
from typing import Any

import httpx

from services.config import get_settings

GITHUB_API = "https://api.github.com"


class GitHubError(RuntimeError):
    """Raised when the GitHub API returns an error response."""


def _headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    settings = get_settings()
    headers = {"Accept": accept, "X-GitHub-Api-Version": "2022-11-28"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


async def get_json_file(path: str) -> Any:
    """Fetch a JSON file from the repo at the configured branch.

    Returns None if the file doesn't exist (404), so callers can treat
    "no data yet" as a normal case rather than an error.
    """
    settings = get_settings()
    url = f"{GITHUB_API}/repos/{settings.github_repo}/contents/{path}"
    params = {"ref": settings.github_branch}
    headers = _headers(accept="application/vnd.github.raw+json")

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=headers)

    if resp.status_code == 404:
        return None
    if resp.is_error:
        raise GitHubError(f"GET {path} failed: {resp.status_code} {resp.text}")

    return json.loads(resp.text)


async def trigger_workflow(workflow_file: str, inputs: dict[str, Any] | None = None) -> None:
    """Fire a workflow_dispatch event for the given workflow file (e.g. 'manual-run.yml')."""
    settings = get_settings()
    url = f"{GITHUB_API}/repos/{settings.github_repo}/actions/workflows/{workflow_file}/dispatches"
    payload = {"ref": settings.github_branch, "inputs": inputs or {}}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload, headers=_headers())

    if resp.is_error:
        raise GitHubError(f"dispatch {workflow_file} failed: {resp.status_code} {resp.text}")


async def list_workflow_runs(workflow_file: str, limit: int = 20) -> list[dict[str, Any]]:
    """Return the most recent runs for a given workflow file, newest first."""
    settings = get_settings()
    url = f"{GITHUB_API}/repos/{settings.github_repo}/actions/workflows/{workflow_file}/runs"
    params = {"per_page": limit}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params, headers=_headers())

    if resp.is_error:
        raise GitHubError(f"list runs for {workflow_file} failed: {resp.status_code} {resp.text}")

    return resp.json().get("workflow_runs", [])
