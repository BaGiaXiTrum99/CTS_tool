import logging
import os
import shutil
import glob
from colorama import init, Fore, Style
from logging.handlers import RotatingFileHandler
from typing import Optional,Iterable
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

def _center_line(text: str, width: int) -> str:
    return text.center(width)

def build_banner_lines(
    title: str = "WELCOME",
    subtitle: Optional[str] = None,
    *,
    margin: int = 2,
    scale: int = 2,  # phóng to 2×
) -> list[str]:
    cols = shutil.get_terminal_size((100, 20)).columns
    cols = max(40, cols - margin * 2)

    lines = [title.strip()]
    if subtitle and subtitle.strip():
        for s in subtitle.splitlines():
            s = s.strip()
            if s:
                lines.append(s)

    pad_x = 4 * max(1, scale)        # ngang
    vpad = 1 * max(1, scale)         # dọc

    max_text = max(len(s) for s in lines)
    content_w = min(cols - 4, max(max_text, 10) + pad_x * 2)
    total_w = content_w + 4
    left_pad = " " * margin

    top_bottom = "=" * total_w
    out = [left_pad + top_bottom]
    for _ in range(vpad):
        out.append(left_pad + f"||{' ' * content_w}||")
    for s in lines:
        centered = _center_line(s, content_w)
        out.append(left_pad + f"||{centered}||")
    for _ in range(vpad):
        out.append(left_pad + f"||{' ' * content_w}||")
    out.append(left_pad + top_bottom)
    return out

def write_banner(logger: logging.Logger, banner_lines: Iterable[str]) -> None:
    """Ghi banner thẳng vào stream của mọi handler (console + file), bỏ qua formatter."""
    for h in logger.handlers:
        stream = getattr(h, "stream", None)
        if stream is None:
            continue
        for line in banner_lines:
            stream.write(line + "\n")
        try:
            stream.flush()
        except Exception:
            pass

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
        log_file, maxBytes=20 * 1024 * 1024, backupCount=10, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    app_logger.addHandler(file_handler)

    # Quan trọng: Ngăn chặn logger gốc (root logger) xử lý lại các log
    # Nếu không, log có thể bị in ra hai lần
    app_logger.propagate = False

    # Banner khi khởi động logger
    banner = build_banner_lines("WELCOME", subtitle="Logger is starting…", margin=2, scale=2)
    write_banner(app_logger, banner)