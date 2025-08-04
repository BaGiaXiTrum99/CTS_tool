import logging
import time
from datetime import datetime,timedelta

from utils.running_commands import Commands
from utils.process_handler import ProcessHandler

CTS_PROCESS_NAME = "cts-tradefed"
AVD_PROCESS_NAME = "qemu-system-x86_64"
logger = logging.getLogger("cts_logger." + __name__)

class AVDHandler:
    def __init__(self, name : str, emulator_path : str, timeout : int, is_headless : bool):
        self.name = name
        self.emulator_path = emulator_path
        self.max_runtime = timedelta(timeout)
        self.start_time = datetime.now()
        self.is_headless = is_headless.upper()

    def __start_avd(self):
        logger.info(f"[Watchdog] Starting AVD '{self.name}' with headless option {self.is_headless}")
        if self.is_headless == "TRUE":
            Commands.execute_timeout_cmd(f'{self.emulator_path} -avd "{self.name}" -no-snapshot -no-audio -wipe-data -no-window',timeout=None) 
        elif self.is_headless == "FALSE":
            Commands.execute_timeout_cmd(f'{self.emulator_path} -avd "{self.name}" -no-snapshot -wipe-data',timeout=None) 
        else: 
            logger.error(f"Not found the value {self.is_headless} of is_headless variable, please input 'False' or 'True' (insensitive)!!!")
            raise ValueError
        time.sleep(5)

    def __close_avd(self):
        logger.info(f"[Watchdog] Closing AVD '{self.name}' if existed")
        avd_pid = ProcessHandler.finding_process(AVD_PROCESS_NAME)
        if avd_pid is not None:
            logger.info(f"[Watchdog] Found AVD with PID {avd_pid} and killing it")
            cmd = f'kill {avd_pid}'
            Commands.execute_short_cmd(cmd)
            time.sleep(3)
        else:
            logger.info("[Watchdog] Not found any PID AVD running, exiting")

    def is_avd_running(self):
        avd_pid = ProcessHandler.finding_process(AVD_PROCESS_NAME)
        if avd_pid is not None:
            logger.info(f"[Watchdog] Found AVD running at process {avd_pid}")
            return True
        else:
            logger.error(f"[Watchdog] Not found any AVD is runnning")
            return False

    def is_cts_running(self):
        cts_pid = ProcessHandler.finding_process(CTS_PROCESS_NAME)
        if cts_pid is not None:
            logger.info(f"[Watchdog] Found cts_tf running at process {cts_pid}.")
            return True
        else:
            logger.error(f"[Watchdog] Not found any cts_tf is runnning.")
            return False
        
    def keep_avd_alive(self):
        logger.info(f"[Watchdog] Monitoring AVD '{self.name}' for {self.max_runtime.days} day(s)...")
        if self.is_cts_running():
            logger.info("[Watchdog] CTS is started. We start new avd for the fresh environment.")
            self.__close_avd()
        else:
            raise RuntimeError("[Watchdog] CTS is not started, please start before running.")
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
                logger.info("[Watchdog] AVD is not running. Restarting...")
                self.__start_avd()
            else:
                logger.debug("Sleeping 15 seconds...")
                time.sleep(15)
        logger.info("========= Finish running =========")
