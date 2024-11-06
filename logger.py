import logging
import os

def setup_logger(name):
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create a common log file
    if not hasattr(setup_logger, 'file_handler'):
        setup_logger.file_handler = logging.FileHandler('discord_mud.log')
        setup_logger.file_handler.setFormatter(formatter)

    logger.addHandler(setup_logger.file_handler)

    return logger
