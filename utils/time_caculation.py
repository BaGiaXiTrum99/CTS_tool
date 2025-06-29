import enum
import re

def parse_duration(duration_str):
    """Chuyển chuỗi như '2h 3m 56s' thành tổng số giây."""
    h = m = s = 0
    duration_str = duration_str.strip().lower()
    matches = re.findall(r'(\d+)\s*(h|m|s|ms)', duration_str)
    for value, unit in matches:
        if unit == 'h':
            h += int(value)
        elif unit == 'm':
            m += int(value)
        elif unit == 's':
            s += int(value)
    return h * 3600 + m * 60 + s

def format_duration(total_seconds):
    """Định dạng lại tổng số giây thành chuỗi 'Xh Ym Zs'."""
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    result = []
    if h:
        result.append(f"{h}h")
    if m:
        result.append(f"{m}m")
    if s or not result:
        result.append(f"{s}s")
    return ' '.join(result)

def sum_durations(*arg):
    """Tính tổng các chuỗi thời gian."""
    total_seconds = sum(parse_duration(d) for d in arg)
    return format_duration(total_seconds)

class TimeUnit(enum.Enum):
    HMS = "h/m/s"
    MS  = "ms"
    S   = "s" 
