"""
Production logging configuration.
Filters out sensitive identifiers, credentials, and raw employee records.
"""

import logging
import sys
import re

SENSITIVE_PATTERNS = [
    re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'\s&]+)', re.IGNORECASE),
    re.compile(r'token["\']?\s*[:=]\s*["\']?([^"\'\s&]+)', re.IGNORECASE),
    re.compile(r'authorization["\']?\s*[:=]\s*["\']?Bearer\s+([^"\'\s&]+)', re.IGNORECASE),
    re.compile(r'EMP\d{4,6}', re.IGNORECASE), # Employee IDs
]

class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub(r'***REDACTED***', msg)
        return msg

def setup_logging():
    logger = logging.getLogger("hr_privacy")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = RedactingFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logging()
