import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Fix: log the real error server-side for debugging
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url,
            exc,
            exc_info=True,
        )
        # Fix: return a generic message to the client so internal details are never exposed
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."},
        )
