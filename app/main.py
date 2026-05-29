from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import engine
from app.api import doctors, patients, appointments, auth     # ← add auth

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    async with engine.begin() as conn:
        print("Database connection: OK")
    yield
    await engine.dispose()
    print("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Internal hospital management system for staff",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(auth.router)              # ← add this
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
        "db": "connected",
    }