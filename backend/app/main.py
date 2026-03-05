"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine

# Import all models before creating tables
from app.models.deadline import Deadline
from app.models.document import Document
from app.models.medical import HealthProtocol, MedicalVisit
from app.models.training import Course, CourseEdition, CourseParticipation
from app.models.dpi import DPIItem, DPIAssignment
from app.models.attendance import Timbratura, AttendanceRecord
# Create all tables
Base.metadata.create_all(bind=engine)

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

app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(workers_router)
app.include_router(deadlines_router)
app.include_router(documents_router)
app.include_router(training_router)
app.include_router(medical_router)
app.include_router(dpi_router)
app.include_router(attendance_router)

# CORS middleware
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
