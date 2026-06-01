# =============================================================
# middleware/custom_middleware.py
#
# FIX 3.1: Replaced print() with logging.info()
#   print() output only goes to stdout and is lost in production.
#   logging.info() integrates with Python's logging system —
#   output goes to log files, monitoring tools, and cloud loggers.
# =============================================================

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware



class TimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        print(f"Request:{request.url.path} processed in {duration:.5f} secs")
        return response

