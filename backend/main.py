import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analyze, health


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

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
    logger.info("ResumeIQ API startup complete.")


@app.get("/")
def root() -> dict:
    return {
        "app": "ResumeIQ API",
        "status": "running",
        "message": "Backend foundation is active.",
    }
