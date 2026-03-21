import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Returns a production-grade configured logger.
    Ensures that logs are formatted with timestamps, module names, and levels.
    """
    logger = logging.getLogger(name)
    
    # Prevent attaching multiple handlers if get_logger is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Route to stdout for standard Docker container logging
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Production JSON-like or strict string formatting
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | [%(name)s] | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        # Prevent double logging to the root logger
        logger.propagate = False
        
    return logger
