"""
Core module for EcoChain Sustainability Tracker.
Provides application bootstrap, configuration, and logging functionality.
"""

from core.app import EcoChainApp, get_app, create_app, create_bureau, run_app
from core.config import Settings, get_settings, is_development, is_production, settings
from core.logging import setup_logging, get_logger, log_startup_info, log_shutdown_info

__all__ = [
    # App
    "EcoChainApp",
    "get_app", 
    "create_app",
    "create_bureau",
    "run_app",
    
    # Config
    "Settings",
    "get_settings",
    "is_development",
    "is_production", 
    "settings",
    
    # Logging
    "setup_logging",
    "get_logger",
    "log_startup_info",
    "log_shutdown_info",
]
