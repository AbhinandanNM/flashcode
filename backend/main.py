from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import settings
from routers import auth, lessons, questions, code_execution, gamification, duels
import models  # Import models to register them with Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodeCrafts API",
    description="Educational programming platform API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(lessons.router)
app.include_router(questions.router)
app.include_router(code_execution.router)
app.include_router(gamification.router)
app.include_router(duels.router)

@app.get("/")
async def root():
    return {"message": "CodeCrafts API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}