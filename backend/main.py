from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

app = FastAPI(
    title="STRATOS-AI API",
    description="Explainable AI-Driven Management Decision-Support Framework for Strategic Resource Allocation in Software Projects",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "STRATOS-AI Decision Support Engine",
        "version": "1.0.0",
        "environment": "active"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "framework": "STRATOS-AI",
        "documentation": "/docs",
        "health": "/health"
    }
