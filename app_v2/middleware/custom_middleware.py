import time
from fastapi import FastAPI,Request
from starlette.middleware.base import BaseHTTPMiddleware

class TimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        print(f"Request:{request.url.path} processed in {duration:.5f} secs")
        return response