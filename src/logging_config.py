import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config import settings

# Logs format
LOG_FORMAT = '%(asctime)s[%(levelname)s]: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Creating log directory if not exists
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

# Other constants
MB = 1024 * 1024


def get_console_handler() -> logging.StreamHandler:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    return console_handler


def get_file_handler(prefix: str, max_bytes=10 * MB, backup_count=1) -> RotatingFileHandler:
    '''
    :param prefix: Prefix for filename (e.g. `database` will be `database.log`)
    :param max_bytes: Max size (in bytes) for file with this logger
    :param backup_count: Max count of files with this logger
    '''
    file_handler = RotatingFileHandler(
        LOGS_DIR / f'{prefix}.log',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    return file_handler


def create_logger(logger_name: str, max_bytes: int | None = None, backup_count: int | None = None) -> None:
    '''
    Args:
        logger_name: Recomended to be string with name first and underscore next 
            (e.g. `database_logger` then file for this logger will be `database.log`)
        max_bytes: Max size (in bytes) for file with this logger
        backup_count: Max count of files with this logger
    '''
    logger = logging.getLogger(logger_name)
    logger.setLevel(settings.LOG_LEVEL)
    logger.handlers.clear()
    
    # Handler for console
    if settings.LOG_INTO_CONSOLE:
        console_handler = get_console_handler()
        logger.addHandler(console_handler)
        
    # Handler for files (with rotation)
    if settings.LOG_INTO_FILES:
        file_handler = get_file_handler(logger_name.split('_')[0], max_bytes or 10 * MB, backup_count or 1)
        logger.addHandler(file_handler)


def setup_logging():
    # Custom loggers
    create_logger('database_logger')
    create_logger('app_logger')
    create_logger('error_logger')
    create_logger('aws_logger')

    # Uvicorn loggers
    file_handler = get_file_handler('uvicorn')
    logging.getLogger('uvicorn').addHandler(file_handler)
    logging.getLogger('uvicorn.access').addHandler(file_handler)
