import psutil
import logging

logger = logging.getLogger("cts_logger." + __name__)

class ProcessHandler:
    @staticmethod
    def find_process_by_name(process_name : str):
        """
        Tìm tiến trình theo tên và trả về PID đầu tiên tìm thấy.

        Args:
            process_name: Tên tiến trình cần tìm.

        Returns:
            PID của tiến trình nếu tìm thấy, None nếu không.
        """
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                name = proc.info.get('name', '')
                if name and process_name in name:
                    logger.info(f"Found process: name={name}, pid={proc.pid}")
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                logger.debug(f"No need to care about this process {proc}")
                continue
        logger.info(f"No process found with name: {process_name}")
        return None
    
    @staticmethod
    def kill_process_by_name(process_name: str, force: bool = False) -> int:
        """
        Find and kill all the processes with name process_name

        Args:
            process_name: Tên tiến trình cần kill.
            force: Nếu True thì dùng kill(), nếu False dùng terminate().

        Returns:
            Số tiến trình đã kill.
        """
        killed_pids = []
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info.get('name', '')
                if name and process_name in name:
                    killed_pids.append(proc.pid)
                    if force:
                        proc.kill()
                        logger.warning(f"Force killed process: {name} (PID {proc.pid})")
                    else:
                        proc.terminate()
                        logger.info(f"Terminated process: {name} (PID {proc.pid})")
                    logger.info(f"Killed process {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.debug(f"Could not kill process: {proc} - Reason: {e}")
        return killed_pids