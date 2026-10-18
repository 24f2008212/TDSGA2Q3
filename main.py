
import os
import time
import uuid

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-u2enef.example.com"
EMAIL = "24f2008212@ds.study.iitm.ac.in"


# Add request ID and processing-time headers to every response.
class RequestHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())

        response = await call_next(request)

        elapsed = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"

        return response


# Register CORS middleware with a strict origin allowlist.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(RequestHeadersMiddleware)


@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        numbers = [int(value.strip()) for value in values.split(",")]

        if not numbers:
            raise ValueError("At least one integer is required")

    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": "values must be comma-separated integers"},
        )

    total = sum(numbers)
    count = len(numbers)

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": round(total / count, 2),
    }


@app.get("/")
async def root():
    return {"status": "ok", "endpoint": "/stats"}
