import logging

def get_logger(name="cts_logger", log_file="logs/cts.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Nếu logger đã được tạo và có handler → dùng luôn
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger