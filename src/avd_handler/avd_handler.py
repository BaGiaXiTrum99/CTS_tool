import logging
import psutil
import time
from datetime import datetime,timedelta

from utils.running_commands import Commands

logger = logging.getLogger("cts_logger." + __name__)
CTS_PROCESS_NAME = "cts-tradefed"

class AVDHandler:
    def __init__(self, name : str, emulator_path : str, timeout : int, is_headless : bool):
        self.name = name
        self.emulator_path = emulator_path
        self.max_runtime = timedelta(timeout)
        self.start_time = datetime.now()
        self.is_headless = is_headless

    def __start_avd(self):
        logger.info(f"[Watchdog] Starting AVD '{self.name}'...")
        if self.is_headless == True:
            Commands.execute_timeout_cmd(f'{self.emulator_path} -avd "{self.name}" -no-snapshot -no-audio -wipe-data -no-window',timeout=None) 
        else:
            Commands.execute_timeout_cmd(f'{self.emulator_path} -avd "{self.name}" -no-snapshot -wipe-data',timeout=None) 
        time.sleep(5)

    def __close_avd(self):
        logger.info(f"[Watchdog] Closing AVD '{self.name}'...")
        avd_pid = self.__check_avd_PID()
        if avd_pid != "":
            logger.info(f"[Watchdog] Found AVD with PID {avd_pid} and killing it")
            cmd = f'kill {avd_pid}'
            Commands.execute_short_cmd(cmd)
        else:
            logger.info("[Watchdog] Not found any PID AVD running, exiting")

    def __check_avd_PID(self):
        cmd : str | list = 'pgrep -f emulator.*-avd'
        stdout, _ = Commands.execute_short_cmd(cmd)
        return stdout.strip()
    
    def is_avd_running(self):
        avd_pid = self.__check_avd_PID()

        # Nếu có output thì AVD đang chạy
        if avd_pid.strip():
            logger.info(f"[Watchdog] AVD running with PID: {avd_pid.strip()}")
            return True
        else:
            logger.info("[Watchdog] No AVD is running")
            return False

    def is_cts_running(self):
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if CTS_PROCESS_NAME in proc.info['name'] or \
                any(CTS_PROCESS_NAME in part for part in proc.info['cmdline']):
                    logger.debug(f"[Watchdog] Found CTS TF is running at proc: {proc}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False 

    def keep_avd_alive(self):
        logger.info(f"[Watchdog] Monitoring AVD '{self.name}' for {self.max_runtime.days} day(s)...")
        while True:
            if datetime.now() - self.start_time > self.max_runtime:
                logger.info("[Watchdog] Reached time limit. Exiting.")
                self.__close_avd()
                break
            elif not self.is_cts_running():
                logger.info("[Watchdog] CTS has exited. Stopping watchdog.")
                self.__close_avd()
                break
            elif not self.is_avd_running():
                logger.info("[Watchdog] AVD not running. Restarting...")
                self.__start_avd()
            else:
                logger.info("[Watchdog] AVD is running.")
                logger.debug("Sleeping 10 seconds")
                time.sleep(10)
        logger.info("========= Finish running =========")
