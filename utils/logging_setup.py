import logging
import os
import glob
from colorama import init, Fore, Style
from logging.handlers import RotatingFileHandler
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return color + message + Style.RESET_ALL

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
    color_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    app_logger.addHandler(console_handler)

    # File Handler
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # thư mục chứa file logger
    log_file = os.path.join(base_dir, "logs", "cts.log")   # logs/cts.log nằm trong CTS_Tool

    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Xóa cts.log và tất cả file backup như cts.log.1, cts.log.2,...
    log_pattern = os.path.join(log_dir, "cts.log*")
    for f in glob.glob(log_pattern):
        try:
            os.remove(f)
        except Exception as e:
            print(f"Warning: Could not delete log file {f}: {e}")

    file_handler = RotatingFileHandler(
        log_file, maxBytes=20 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    app_logger.addHandler(file_handler)

    # Quan trọng: Ngăn chặn logger gốc (root logger) xử lý lại các log
    # Nếu không, log có thể bị in ra hai lần
    app_logger.propagate = False