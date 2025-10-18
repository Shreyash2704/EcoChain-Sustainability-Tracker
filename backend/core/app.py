"""
Core application bootstrap for EcoChain Sustainability Tracker.
Handles FastAPI + uAgents Bureau initialization and startup.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uagents import Bureau

from core.config import settings, is_development
from core.logging import get_logger, log_startup_info, log_shutdown_info

logger = get_logger(__name__)


class EcoChainApp:
    """Main application class that manages FastAPI and uAgents Bureau."""
    
    def __init__(self):
        self.fastapi_app: FastAPI = None
        self.bureau: Bureau = None
        self._bureau_task: asyncio.Task = None
    
    def create_fastapi_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        logger.info("Creating FastAPI application...")
        
        # Create FastAPI app with lifespan management
        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            # Startup
            await self._startup()
            yield
            # Shutdown
            await self._shutdown()
        
        app = FastAPI(
            title=settings.app_name,
            description="EcoChain Sustainability Tracker API",
            version="1.0.0",
            debug=settings.debug,
            lifespan=lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add basic health check endpoint
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "app_name": settings.app_name,
                "environment": settings.environment,
                "bureau_running": self.bureau is not None
            }
        
        self.fastapi_app = app
        logger.info("FastAPI application created successfully")
        return app
    
    def create_bureau(self) -> Bureau:
        """Create and configure uAgents Bureau."""
        logger.info("Creating uAgents Bureau...")
        
        bureau = Bureau(port=settings.bureau_port)
        
        # Import and add agents
        try:
            from agents.user_agent import user_agent
            bureau.add(user_agent)
            logger.info("Added user_agent to Bureau")
        except ImportError as e:
            logger.warning(f"Could not import user_agent: {e}")
        
        try:
            from agents.verifier_agent import verifier_agent
            bureau.add(verifier_agent)
            logger.info("Added verifier_agent to Bureau")
        except ImportError as e:
            logger.warning(f"Could not import verifier_agent: {e}")
        
        try:
            from agents.reasoner_agent import reasoner_agent
            bureau.add(reasoner_agent)
            logger.info("Added reasoner_agent to Bureau")
        except ImportError as e:
            logger.warning(f"Could not import reasoner_agent: {e}")
        
        try:
            from agents.minting_agent import minting_agent
            bureau.add(minting_agent)
            logger.info("Added minting_agent to Bureau")
        except ImportError as e:
            logger.warning(f"Could not import minting_agent: {e}")
        
        # Add other agents as they become available
        # from agents.notification_agent import notification_agent
        
        self.bureau = bureau
        logger.info(f"uAgents Bureau created on port {settings.bureau_port}")
        return bureau
    
    async def _startup(self) -> None:
        """Application startup logic."""
        log_startup_info()
        
        # Start Bureau if not already running
        if self.bureau and not self._bureau_task:
            logger.info("Starting uAgents Bureau...")
            self._bureau_task = asyncio.create_task(self.bureau.run_async())
            logger.info("uAgents Bureau started")
    
    async def _shutdown(self) -> None:
        """Application shutdown logic."""
        log_shutdown_info()
        
        # Stop Bureau
        if self._bureau_task:
            logger.info("Stopping uAgents Bureau...")
            self._bureau_task.cancel()
            try:
                await self._bureau_task
            except asyncio.CancelledError:
                logger.info("uAgents Bureau stopped")
    
    async def run(self) -> None:
        """Run the application."""
        import uvicorn
        
        # Create FastAPI app
        app = self.create_fastapi_app()
        
        # Create Bureau
        self.create_bureau()
        
        # Run FastAPI with uvicorn
        logger.info(f"Starting server on {settings.host}:{settings.port}")
        config = uvicorn.Config(
            app=app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
            reload=is_development()
        )
        server = uvicorn.Server(config)
        await server.serve()


# Global app instance
app_instance = EcoChainApp()


def get_app() -> EcoChainApp:
    """Get the global application instance."""
    return app_instance


def create_app() -> FastAPI:
    """Create and return the FastAPI application."""
    return app_instance.create_fastapi_app()


def create_bureau() -> Bureau:
    """Create and return the uAgents Bureau."""
    return app_instance.create_bureau()


async def run_app() -> None:
    """Run the complete application."""
    await app_instance.run()


if __name__ == "__main__":
    # Run the application
    asyncio.run(run_app())
