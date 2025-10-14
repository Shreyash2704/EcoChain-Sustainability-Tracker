"""
Logging configuration for EcoChain Sustainability Tracker.
Provides structured logging setup with different handlers and formatters.
"""

import logging
import logging.config
import sys
from typing import Optional
from pathlib import Path

from core.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
    """
    log_level = log_level or settings.log_level
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": [],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": [],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": [],
                "propagate": False,
            },
            "uagents": {
                "level": "INFO",
                "handlers": [],
                "propagate": False,
            }
        }
    }
    
    # Add console handler
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "default",
            "stream": sys.stdout,
        }
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("console")
    
    # Add file handler if specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_startup_info() -> None:
    """Log application startup information."""
    logger = get_logger(__name__)
    logger.info("=" * 50)
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"FastAPI host: {settings.host}:{settings.port}")
    logger.info(f"Bureau port: {settings.bureau_port}")
    logger.info("=" * 50)


def log_shutdown_info() -> None:
    """Log application shutdown information."""
    logger = get_logger(__name__)
    logger.info("=" * 50)
    logger.info(f"Shutting down {settings.app_name}")
    logger.info("=" * 50)


# Initialize logging on module import
setup_logging()
