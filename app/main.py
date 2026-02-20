from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import connect_to_mongo, close_mongo_connection
from .routes import auth, quadras

app = FastAPI(
    title="Futzer API",
    description="API para plataforma de aluguel de quadras esportivas",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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

@app.get("/")
async def root():
    return {"message": "Futzer API - Running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
