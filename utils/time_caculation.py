import re
import math 
from xml.etree.ElementTree import Element

from utils.constants import TimeUnit
import logging

logger = logging.getLogger("cts_logger." + __name__)

class TimeHandler:
    @staticmethod
    def parse_duration(duration_str : str) -> int:
        """Chuyển chuỗi như '2h 3m 56s' hoặc '1234ms' thành tổng số giây (kiểu int)."""
        h = m = s = ms = 0
        duration_str = duration_str.strip().lower()
        matches = re.findall(r'(\d+)\s*(h|m|s|ms)', duration_str)
        for value, unit in matches:
            value = int(value)
            if unit == 'h':
                h += value
            elif unit == 'm':
                m += value
            elif unit == 's':
                s += value
            elif unit == 'ms':
                ms += value
        total_seconds = h * 3600 + m * 60 + s + ms / 1000
        return total_seconds

    @staticmethod
    def format_duration(total_seconds):
        """Định dạng lại tổng số giây thành chuỗi 'Xh Ym Zs'."""
        total_seconds = int(round(total_seconds))
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

    @staticmethod
    def sum_durations(*arg):
        """Tính tổng các chuỗi thời gian."""
        total_seconds = sum(TimeHandler.parse_duration(d) for d in arg)
        return TimeHandler.format_duration(total_seconds)

    @staticmethod
    def get_execution_time_from_module(module: Element, time_unit) -> str:
        execution_time = module.get("runtime")
        assert execution_time is not None, "Can not get runtime of module"
        execution_time = int(execution_time) 

        if time_unit == TimeUnit.HMS.value:
            execution_time = TimeHandler.format_duration(math.ceil(execution_time/1000)) 
            logger.debug(f"Execution Time: {execution_time}")
        elif time_unit == TimeUnit.S.value:
            execution_time = str(math.ceil(execution_time/1000)) + "s"
            logger.debug(f"Execution Time: {execution_time} {time_unit}")
        elif time_unit == TimeUnit.MS.value:
            execution_time = str(execution_time) + "ms"
            logger.debug(f"Execution Time: {execution_time} {time_unit}")
            
        return execution_time