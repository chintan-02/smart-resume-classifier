from time import perf_counter

from fastapi import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analyze, health
from src.monitoring import format_latency_ms, generate_request_id, get_logger, log_event


logger = get_logger(__name__)

app = FastAPI(
    title="ResumeIQ API",
    description="Backend API foundation for ResumeIQ resume intelligence workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)


@app.on_event("startup")
def log_startup() -> None:
    log_event(logger, "api_startup", "ResumeIQ API startup complete.")


@app.middleware("http")
async def add_monitoring_headers(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id
    start_time = perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency_ms = format_latency_ms(perf_counter() - start_time)
        if "response" in locals():
            response.headers["x-request-id"] = request_id
            response.headers["x-process-time-ms"] = str(latency_ms)
        log_event(
            logger,
            "api_request",
            "FastAPI request completed.",
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": latency_ms,
            },
        )


@app.get("/")
def root() -> dict:
    return {
        "app": "ResumeIQ API",
        "status": "running",
        "message": "Backend foundation is active.",
    }
