"""
Structured logging with Loguru.
Provides request ID tracking, JSON formatting, and rotation.
"""

import sys
import uuid
from pathlib import Path
from contextvars import ContextVar
from typing import Any, Dict

from loguru import logger

from src.config import settings


# Context variable for request ID (thread-safe)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: str | None = None) -> str:
    """
    Set request ID in context. Generates one if not provided.
    
    Args:
        request_id: Optional request ID. If None, generates a new UUID.
        
    Returns:
        The request ID that was set.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]  # Short UUID for readability
    request_id_var.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_var.set("")


def add_context(**kwargs: Any) -> Dict[str, Any]:
    """
    Add custom context to log record.
    
    Usage:
        logger.bind(**add_context(user_id="123", action="search")).info("User action")
    
    Args:
        **kwargs: Key-value pairs to add to log context
        
    Returns:
        Dict with request_id and custom context
    """
    context = {"request_id": get_request_id()}
    context.update(kwargs)
    return context


def format_record(record: Dict[str, Any]) -> str:
    """
    Custom formatter for log records.
    
    Development: Human-readable with colors
    Production: JSON for log aggregation
    """
    if settings.is_production:
        # JSON format for production (parsed by log aggregators)
        import json
        log_dict = {
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add request_id if present
        if "request_id" in record["extra"]:
            log_dict["request_id"] = record["extra"]["request_id"]
        
        # Add any other extra context
        for key, value in record["extra"].items():
            if key != "request_id":
                log_dict[key] = value
        
        return json.dumps(log_dict) + "\n"
    else:
        # Human-readable format for development
        extra_parts = []
        
        if "request_id" in record["extra"] and record["extra"]["request_id"]:
            extra_parts.append(f"[req:{record['extra']['request_id']}]")
        
        # Add other context
        other_context = {k: v for k, v in record["extra"].items() if k != "request_id"}
        if other_context:
            # Format each context item safely
            context_str = ", ".join(f"{k}={v}" for k, v in other_context.items())
            extra_parts.append(f"[{context_str}]")
        
        extra = " ".join(extra_parts)
        if extra:
            extra = " " + extra
        
        # Build format string without f-string to avoid conflicts
        format_str = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
            + extra + " - <level>{message}</level>\n"
        )
        
        return format_str


def setup_logger() -> None:
    """
    Configure logger with appropriate handlers and formatters.
    Called once at application startup.
    """
    # Remove default handler
    logger.remove()
    
    # Console handler (always enabled)
    logger.add(
        sys.stderr,
        format=format_record,
        level=settings.log_level,
        colorize=not settings.is_production,
        backtrace=settings.debug,
        diagnose=settings.debug,
    )
    
    # File handler with rotation
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.log_file,
        format=format_record,
        level=settings.log_level,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="5 days",  # Keep logs for 5 days
        compression="zip",  # Compress rotated logs
        backtrace=settings.debug,
        diagnose=settings.debug,
    )
    
    logger.info(
        "Logger initialized",
        environment=settings.environment,
        log_level=settings.log_level,
        log_file=settings.log_file,
    )


# Initialize logger on import
setup_logger()


# Example usage and testing
if __name__ == "__main__":
    print("Testing structured logger...\n")
    
    # Basic logging
    logger.info("Application started")
    logger.debug("Debug information")
    logger.warning("Warning message")
    
    # With request ID
    set_request_id()
    logger.bind(**add_context()).info("Processing request")
    logger.bind(**add_context(user_id="user123")).info("User authenticated")
    
    # With custom context
    logger.bind(**add_context(
        action="search",
        query="Tesla",
        duration_ms=145
    )).info("Search completed")
    
    # Error logging
    try:
        result = 1 / 0
    except Exception as e:
        logger.bind(**add_context()).exception("Error occurred")
    
    clear_request_id()
    logger.info("Request completed")
    
    print(f"\n✅ Logs written to: {settings.log_file}")
    print("✅ Logger configured successfully!")