"""Vercel Python entrypoint: re-exports the FastAPI ASGI app."""

from backend.main import app

__all__ = ["app"]
