import logging

from src.config import Config

def get_logger():
    logger = logging.getLogger("icloudback")
    return logger

def configure_logger(config: Config):
    logger = get_logger()
    logger.setLevel(config.logger_level)
    
    handler = logging.FileHandler(config.logger_filename)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = True
