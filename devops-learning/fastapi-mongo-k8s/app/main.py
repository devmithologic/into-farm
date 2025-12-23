from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up...")
    await connect_to_mongo()
    print("✅ Connected to MongoDB")
    yield
    # Shutdown
    print("🛑 Shutting down...")
    await close_mongo_connection()
    print("✅ MongoDB connection closed")

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "FastAPI + MongoDB on Kubernetes",
        "status": "running",
        "app": settings.app_name
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/db-health")
async def db_health():
    try:
        db = await get_database()
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )