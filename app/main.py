from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import router as api_router

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="RestoBot - Intelligent Virtual Assistant for Restaurants API"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Run migration on startup
import subprocess
@app.on_event("startup")
def run_migrations():
    try:
        result = subprocess.run(["python", "migrate.py"], cwd="/app", capture_output=True, text=True)
        if result.returncode == 0:
            print("[Startup] Database migration completed.")
        else:
            print(f"[Startup] Migration failed: {result.stderr}")
    except Exception as e:
        print(f"[Startup] Migration error: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to RestoBot API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RestoBot API"}


@app.post("/webhook")
async def rasa_webhook(data: dict):
    """Webhook endpoint for Rasa actions"""
    return {
        "status": "received",
        "data": data,
        "message": "Webhook processed successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )