from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from models.database import init_db
from routes.api import router

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Medical Study App API",
    description="Backend API for medical study document management and progress tracking",
    version="1.0.0"
)

# Enable CORS for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your Electron app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {"message": "Medical Study App API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
