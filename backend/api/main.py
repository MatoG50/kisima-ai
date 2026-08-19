import os
import sys
from typing import List

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.api.routes.health import router as health_router
from backend.api.routes.pumps import router as pumps_router
from backend.api.routes.recommendations import router as recommendations_router
from backend.api.routes.ai import router as ai_router

def get_cors_origins() -> List[str]:
    cors_str = os.environ.get("API_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
    origins = [origin.strip() for origin in cors_str.split(",") if origin.strip()]
    return origins if origins else ["*"]

app = FastAPI(
    title="AI-Powered Pump & Solar Sizing REST API",
    version="1.0.0",
    description="Stage 6 Backend REST API with RAG + LLM Knowledge & Technical Explanation Layer.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler for Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err["loc"] if loc != "body"])
        errors.append(f"Field '{field}': {err['msg']}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "VALIDATION_ERROR",
            "message": "Invalid request payload or engineering input parameter.",
            "details": errors
        }
    )

# Custom Global Exception Handler to prevent raw stack trace exposure
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred in the backend REST API.",
            "error_type": exc.__class__.__name__
        }
    )

# Include Routers under /api/v1 prefix
app.include_router(health_router, prefix="/api/v1")
app.include_router(pumps_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
