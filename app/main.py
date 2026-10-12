"""
Smart Student Management System (SSMS) - Enterprise Core Monolith Application Entry Point.
"""
import os
import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_database
from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.courses import router as courses_router
from app.api.faculty import router as faculty_router
from app.api.grades import router as grades_router
from app.api.billing import router as billing_router
from app.api.transcripts import router as transcripts_router
from app.api.admin import router as admin_router

app = FastAPI(
    title="Smart Student Management System (SSMS)",
    version="1.0.0",
    description="Enterprise modular monolith modernizing student lifecycle, courses, grading, tuition, and compliance."
)

# Enable CORS for cross-origin frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(faculty_router)
app.include_router(grades_router)
app.include_router(billing_router)
app.include_router(transcripts_router)
app.include_router(admin_router)


@app.on_event("startup")
def on_startup():
    """Initialize SQLite/PostgreSQL schema and baseline seeds on boot."""
    init_database()


@app.get("/health", tags=["system"])
def health_check():
    """Container health and readiness probe."""
    return {
        "status": "ok",
        "service": "ssms-api",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


# Mount Static Files & Frontend Harness
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    pages_dir = os.path.join(public_dir, "pages")
    if os.path.exists(pages_dir):
        app.mount("/pages", StaticFiles(directory=pages_dir), name="pages")
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
