# src/middlewares/timer.py
import time
from fastapi import Request


async def response_time_middleware(request: Request, call_next):
    # perf_counter es más preciso que time.time() para medir duraciones
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{duration:.4f} s"
    return response
