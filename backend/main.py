
"""CareerLens FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analysis import router as analysis_router

app = FastAPI(
    title="CareerLens API",
    description=(
        "Resume building, job compatibility, "
        "and skill-gap analysis."
    ),
    version="1.0.0",
)

# Allow the local React development server to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "CareerLens API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(analysis_router)
