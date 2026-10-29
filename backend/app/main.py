"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

import app.models  # noqa: F401
from app.core.rate_limit import RateLimitMiddleware
from app.core.audit_middleware import AuditMiddleware

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Platform for workplace safety management (D.Lgs. 81/08)",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Include routers
from app.api.auth import router as auth_router
from app.api.companies import router as companies_router
from app.api.workers import router as workers_router
from app.api.deadlines import router as deadlines_router
from app.api.documents import router as documents_router
from app.api.training import router as training_router
from app.api.medical import router as medical_router
from app.api.dpi import router as dpi_router
from app.api.attendance import router as attendance_router
from app.api.audit import router as audit_router

app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(workers_router)
app.include_router(deadlines_router)
app.include_router(documents_router)
app.include_router(training_router)
app.include_router(medical_router)
app.include_router(dpi_router)
app.include_router(attendance_router)
app.include_router(audit_router)

# CORS middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.get("/api", tags=["API"])
async def api_root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "api_v1": f"{settings.API_V1_STR}",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
