import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base, SessionLocal
from .config import AUDIO_DIR
from .seed_data import seed_database_if_empty

# Import all routers
from .routes.auth_routes import router as auth_router
from .routes.farmer_routes import router as farmer_router
from .routes.scheme_routes import router as scheme_router
from .routes.loan_routes import router as loan_router
from .routes.crop_routes import router as crop_router
from .routes.fertilizer_routes import router as fertilizer_router
from .routes.weather_routes import router as weather_router
from .routes.market_routes import router as market_router
from .routes.chat_routes import router as chat_router
from .routes.speech_routes import router as speech_router
from .routes.admin_routes import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Seed initial verified government schemes and synthetic demo records
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Krishi Mitra API – ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ",
    description="AI-powered Agriculture Assistant for Karnataka Farmers (HackFusion 2.0)",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static audio streaming directory
app.mount("/static_audio", StaticFiles(directory=AUDIO_DIR), name="static_audio")

# Mount API Routers
app.include_router(auth_router)
app.include_router(farmer_router)
app.include_router(scheme_router)
app.include_router(loan_router)
app.include_router(crop_router)
app.include_router(fertilizer_router)
app.include_router(weather_router)
app.include_router(market_router)
app.include_router(chat_router)
app.include_router(speech_router)
app.include_router(admin_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Krishi Mitra Backend API",
        "version": "2.0.0",
        "language_support": ["kn", "en"],
        "speech_engine": "gTTS Kannada Neural & Web Speech"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
