"""Structured logging utilities for production observability."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

# Configure root logger for structured JSON output
def setup_structured_logging():
    """
    Setup structured JSON logging for production.
    
    Logs are output as JSON lines for easy parsing by log aggregators
    (e.g., ELK, Splunk, CloudWatch).
    """
    
    class JSONFormatter(logging.Formatter):
        """Format log records as JSON for structured logging."""
        
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            
            # Add extra context if available
            if hasattr(record, "request_id"):
                log_data["request_id"] = record.request_id
            if hasattr(record, "user_id"):
                log_data["user_id"] = record.user_id
            if hasattr(record, "endpoint"):
                log_data["endpoint"] = record.endpoint
            if hasattr(record, "status_code"):
                log_data["status_code"] = record.status_code
            if hasattr(record, "duration_ms"):
                log_data["duration_ms"] = record.duration_ms
                
            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)
    
    # Setup handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Configure jarvis logger
    jarvis_logger = logging.getLogger("jarvis")
    jarvis_logger.setLevel(logging.INFO)


def get_logger(name: str = "jarvis") -> logging.Logger:
    """Get a logger instance with optional context."""
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding structured fields to log records."""
    
    def __init__(self, logger: logging.Logger, **kwargs: Any):
        self.logger = logger
        self.context = kwargs
        self.old_factory = None
    
    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, *args):
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)
