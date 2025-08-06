import re
from typing import List
import logging
from utils.time_caculation import TimeHandler

logger = logging.getLogger("cts_logger." + __name__)

class SummaryParser:
    def __init__(self, path: str, abi: str = "x86_64") -> None:
        self.summary_path = f"{path}/invocation_summary.txt"
        self.abi = abi    
        self.__data = self.__read_summary_file()
        self.__consumed_time_chunk = self.__extract_chunk(
            "=============== Consumed Time ==============\n",
            "Total aggregated tests run time"
        )
        self.__preparation_time_chunk = self.__extract_chunk(
            "============== Modules Preparation Times ==============\n",
            "Total preparation time"
        )

    def __read_summary_file(self) -> List[str]:
        with open(self.summary_path, 'r') as f:
            logger.info(f"Reading data from {f.name}")
            return f.readlines()

    def __extract_chunk(self, start_marker: str, end_marker: str) -> List[str]:
        logger.info(f"Extracting chunk")
        start_idx = end_idx = None
        for idx, line in enumerate(self.__data):
            if line == start_marker:
                start_idx = idx + 1
            elif end_marker in line and start_idx is not None:
                end_idx = idx
                break
        if start_idx is None or end_idx is None:
            logger.warning(f"Could not find chunk between '{start_marker.strip()}' and '{end_marker}'")
            return []
        logger.debug(f"Chunk found from line {start_idx} to {end_idx}")
        return self.__data[start_idx:end_idx]

    def __parse_consumed_times(self) -> dict:
        result = {}
        for line in self.__consumed_time_chunk:
            clean_line = line.strip().replace(f"{self.abi} ", "")
            if ": " in clean_line:
                name, time = clean_line.split(": ", 1)
                result[name] = time.strip()
        return result

    def __parse_preparation_times(self) -> dict:
        result = {}
        for line in self.__preparation_time_chunk:
            clean_line = line.strip().replace(f"{self.abi} ", "")
            if " => " in clean_line:
                try:
                    name, time_str = clean_line.split(" => ", 1)
                    times = list(map(int, re.findall(r"\d+", time_str)))
                    total_millis = sum(times)
                    result[name] = f"{total_millis // 1000}s"
                except Exception as e:
                    logger.warning(f"Failed to parse line: {line} - {e}")   
        return result

    def get_module_execution_time_info(self) -> List[List[str]]:
        consumed = self.__parse_consumed_times()
        logger.debug(f"Modules with consumed time: {consumed}")
        
        preparation = self.__parse_preparation_times()
        logger.debug(f"Modules with preparation time: {preparation}")

        module_execution_time_info = []
        for module, consumed_time in consumed.items():
            if module in preparation:
                total_time = TimeHandler.sum_durations(consumed_time, preparation[module])
                module_execution_time_info.append([module, total_time])
        
        logger.info(f"Final Execution Time per module: {module_execution_time_info}")
        logger.info("Finished parsing module Execution Time info.")
        return module_execution_time_info
    