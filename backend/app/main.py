from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import os

# Import our modules
from .discord.client import DiscordMonitor
from .models.config import Settings

# Global discord client instance
discord_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load config and start Discord client
    global discord_client
    settings = Settings()  # Load settings from environment
    discord_client = DiscordMonitor(settings)
    await discord_client.start()
    
    yield
    
    # Shutdown: Close Discord client
    if discord_client:
        await discord_client.close()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .routers import api
app.include_router(api.router, prefix="/api")

# Serve static files in production
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend/build")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=f"{frontend_path}/static"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve index.html for all non-API routes
        if not full_path.startswith("api/"):
            return FileResponse(f"{frontend_path}/index.html")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7777, reload=True) 