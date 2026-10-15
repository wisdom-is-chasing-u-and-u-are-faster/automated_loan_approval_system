import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.init_db import init_database
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.applications import router as applications_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.models.schemas import HealthResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes SQLite/PostgreSQL schema and baseline seeds upon application boot."""
    init_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Automatic Loan Approval System (ALAS) High-Throughput REST Platform",
    lifespan=lifespan
)

# Enable CORS for enterprise API clients and browser frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse, tags=["Health Probe"])
def health_check():
    """Readiness probe for container orchestrators and load balancers."""
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat()
    )

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(applications_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

# Mount Static Frontend UI Directory
public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")
