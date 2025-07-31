import logging
import os

# Khởi tạo đối tượng logger chung, đặt tên là "cts_logger"
# Các module khác sẽ lấy logger này bằng cách gọi getLogger("cts_logger")
app_logger = logging.getLogger("cts_logger")
# Ban đầu không cần set level hay handlers ở đây.
# Việc cấu hình sẽ được làm trong main.py

def configure_logger(level_str: str, log_file: str = "logs/cts.log"):
    """
    Cấu hình logger chính của ứng dụng.
    Chỉ nên gọi một lần duy nhất.
    """
    # Tránh thêm handler nhiều lần nếu hàm này bị gọi lại
    if app_logger.handlers:
        return

    log_level_map = {
        "DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING,
        "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL
    }
    app_logger.setLevel(log_level_map.get(level_str.upper(), logging.INFO))

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)

    # File Handler
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    app_logger.addHandler(file_handler)

    # Quan trọng: Ngăn chặn logger gốc (root logger) xử lý lại các log
    # Nếu không, log có thể bị in ra hai lần
    app_logger.propagate = False