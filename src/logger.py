import os
import logging

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from src.config import app_config

log_dir = app_config.logs_path

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(
    log_dir, 
    datetime.now().strftime('%Y-%m-%d.log')
    )

handler = TimedRotatingFileHandler(
    log_file, 
    when='midnight', 
    interval=1,
)

handler.suffix = "%Y-%m-%d"
handler.extMatch = r"^\d{4}-\d{2}-\d{2}$"

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[handler]
    )

logger = logging.getLogger(__name__)