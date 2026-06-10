from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analyze, health


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


@app.get("/")
def root() -> dict:
    return {
        "app": "ResumeIQ API",
        "status": "running",
        "message": "Backend foundation is active.",
    }
