import psutil
import logging

logger = logging.getLogger("cts_logger." + __name__)

class ProcessHandler:
    def finding_process(process_name : str):
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if process_name in proc.info['name']:
                    logger.info(f"Found process at {proc}")
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                logger.debug(f"No need to care about this process {proc}")
                continue
        return None