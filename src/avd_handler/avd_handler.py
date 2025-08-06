import logging
import time
from datetime import datetime,timedelta

from utils.running_commands import Commands
from utils.process_handler import ProcessHandler

CTS_PROCESS_NAME = "cts-tradefed"
AVD_PROCESS_NAME = "qemu-system-x86_64"
WATCHDOG_PREFIX = "[Watchdog]"

logger = logging.getLogger("cts_logger." + __name__)

class AVDHandler:
    def __init__(self, name : str, emulator_path : str, timeout : int, is_headless : bool, restart_avd : bool, sleep_interval: int = 15):
        self.name = name
        self.emulator_path = emulator_path
        self.max_runtime = timedelta(timeout)
        self.start_time = datetime.now()
        self.is_headless = is_headless
        self.restart_avd = restart_avd
        self.sleep_interval = sleep_interval

    def start_avd(self):
        logger.info(f"{WATCHDOG_PREFIX} Starting AVD '{self.name}' with headless option {self.is_headless}")
        if self.is_headless:
            Commands.execute_timeout_cmd(f'{self.emulator_path} -avd "{self.name}" -no-snapshot -no-audio -wipe-data -no-window',timeout=None) 
        else:
            Commands.execute_timeout_cmd(f'{self.emulator_path} -avd "{self.name}" -no-snapshot -wipe-data',timeout=None) 
        time.sleep(10)

    def close_avd(self):
        logger.info(f"{WATCHDOG_PREFIX} Closing AVD '{self.name}' if existed")
        ProcessHandler.kill_process_by_name(AVD_PROCESS_NAME)

    def is_avd_running(self):
        avd_pid = ProcessHandler.find_process_by_name(AVD_PROCESS_NAME)
        if avd_pid is not None:
            logger.info(f"{WATCHDOG_PREFIX} Found AVD running at process {avd_pid}")
            return True
        else:
            logger.error(f"{WATCHDOG_PREFIX} Not found any AVD is runnning")
            return False

    def is_cts_running(self):
        cts_pid = ProcessHandler.find_process_by_name(CTS_PROCESS_NAME)
        if cts_pid is not None:
            logger.info(f"{WATCHDOG_PREFIX} Found cts_tf running at process {cts_pid}.")
            return True
        else:
            logger.error(f"{WATCHDOG_PREFIX} Not found any cts_tf is runnning.")
            return False
        
    def keep_avd_alive(self):
        logger.info(f"{WATCHDOG_PREFIX} Monitoring AVD '{self.name}' for {self.max_runtime.total_seconds()} seconds...")
        if self.is_cts_running():
            if self.restart_avd:
                logger.info(f"{WATCHDOG_PREFIX} CTS is started. We start new avd for the fresh environment.")
                self.close_avd()
                self.start_avd()
            else:
                logger.info(f"{WATCHDOG_PREFIX} restart_avd is set to False for debugging, not closing AVD")
        else:
            raise RuntimeError(f"{WATCHDOG_PREFIX} CTS is not started, please start before running.")
        try:
            while True:
                if datetime.now() - self.start_time > self.max_runtime:
                    logger.info(f"{WATCHDOG_PREFIX} Reached time limit. Exiting.")
                    self.close_avd()
                    break
                elif not self.is_cts_running():
                    logger.info(f"{WATCHDOG_PREFIX} CTS has exited. Stopping watchdog.")
                    self.close_avd()
                    break
                elif not self.is_avd_running():
                    logger.info(f"{WATCHDOG_PREFIX} AVD is not running. Restarting...")
                    self.start_avd()
                else:
                    logger.debug(f"Sleeping {self.sleep_interval} seconds...")
                    time.sleep(self.sleep_interval)
        except KeyboardInterrupt:
            logger.warning(f"{WATCHDOG_PREFIX} Received interrupt signal. Cleaning up...")
            self.close_avd()
            logger.info("========= Finish running =========")
        except Exception as e:
            logger.exception(f"{WATCHDOG_PREFIX} Unexpected exception occurred:")
            self.close_avd()
            raise
