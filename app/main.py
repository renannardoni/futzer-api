import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import connect_to_mongo, close_mongo_connection
from .routes import auth, quadras
from .routes.upload import router as upload_router

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Futzer API",
    description="API para plataforma de aluguel de quadras esportivas",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Routes
app.include_router(auth.router, prefix="/api")
app.include_router(quadras.router, prefix="/api")
app.include_router(upload_router, prefix="/api")

# Static files (uploaded images)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    return {"message": "Futzer API - Running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
