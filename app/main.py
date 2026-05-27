from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.api import doctors, patients, appointments

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Everything BEFORE yield runs on startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    # Phase 2 — DB connection pool will be created here
    # Phase 4 — SQS client will be initialized here
    yield
    # Everything AFTER yield runs on shutdown
    print("Shutting down...")
    # Phase 2 — DB connection pool will be closed here


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Internal hospital management system for staff",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Mount all routers
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        # Phase 2 — will add db: "connected" here
        # Phase 4 — will add sqs: "connected" here
    }