import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Logger setup
logger = logging.getLogger("smart_attendance_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
   "%(asctime)s | %(levelname)s |  %(filename)s |  %(lineno)d |  %(funcName)s |  %(message)s"

)

# Rotating File Handler
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10*1024*1024, backupCount=5
)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Logger initialized")
