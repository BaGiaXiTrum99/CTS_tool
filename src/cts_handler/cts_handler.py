import logging
import threading
import subprocess
import getpass
import time

from src.avd_handler.avd_handler import AVDHandler,CTS_PROCESS_NAME
from utils.process_handler import ProcessHandler
from utils.constants import CTSRetryType,DeviceType
from utils.running_commands import Commands

logger = logging.getLogger("cts_logger." + __name__)

WAIT_PROCESS_TIMEOUT = 60000
END_STRING = "=================== End ===================="
CTS_RUNNER_PREFIX = "[CTS_RUNNER]" 
WAIT_ADB_REBOOT_TIME = 45
ADB_LOST_CONNECTION_MSG = "error: no devices/emulators found"

class CTSHandler:
    def __init__(self,android_cts_path : str ,cmd : str ,retry_time : int ,retry_type : str , device_type : str, is_headless : bool, restart : bool):
        self.android_cts_path = android_cts_path
        self.cts_tradefed = self.android_cts_path + '/tools/cts-tradefed'
        self.cmd = cmd
        self.retry_time = retry_time
        self.retry_type = retry_type
        self.device_type = device_type
        self.cts_tf_proc = None
        self.is_headless = is_headless
        self.restart = restart
        self.command_done = threading.Event()

    def __open_tradefed_session(self):
        logger.info(f"{CTS_RUNNER_PREFIX} Start CTS-Tradefed")
        cts_tf_proc = subprocess.Popen(
            self.cts_tradefed,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # để giao tiếp bằng chuỗi
            bufsize=1   # dòng nào ra dòng đó
        )
        return cts_tf_proc

    def __send_cts_command(self, cmd):
        if self.cts_tf_proc.stdin and not self.cts_tf_proc.stdin.closed:
            time.sleep(2)
            logger.info(f"{CTS_RUNNER_PREFIX} Sending command: {cmd}")
            self.cts_tf_proc.stdin.write(cmd + "\n")
            self.cts_tf_proc.stdin.flush()
            time.sleep(2)
        else:
            logger.error(f"{CTS_RUNNER_PREFIX} stdin is closed. Cannot send: {cmd}")

    def __read_error(self):
        while True:
            line = self.cts_tf_proc.stderr.readline()
            if not line:
                break
            logger.error(f"{CTS_RUNNER_PREFIX} " + line.strip())

    def __kill_cts_tradefed(self):
        logger.info(f"{CTS_RUNNER_PREFIX} Kill CTS Tradefed if existed")
        ProcessHandler.kill_process_by_name(CTS_PROCESS_NAME)

    def __read_output(self):
        while True:
            line = self.cts_tf_proc.stdout.readline()
            if line == "":  # tradefed process đã kết thúc, pipe đóng
                logger.info(f"{CTS_RUNNER_PREFIX} Output pipe closed, ending output thread.")
                break
            clean_line = line.strip()
            # Bỏ dòng trống và dòng prompt
            if not clean_line or clean_line == "cts-console >":
                continue
            logger.debug(f"{CTS_RUNNER_PREFIX} " + line.strip())

            if END_STRING in line:
                logger.info(f"{CTS_RUNNER_PREFIX} Found signal end running CTS")
                self.command_done.set()

    def __retry_time_count(self,retry_time_count):
        logger.info(f"{CTS_RUNNER_PREFIX} Running retry session #{retry_time_count}")
        self.command_done.clear()
        if self.retry_type == CTSRetryType.DEFAULT.value:
            self.__send_cts_command(f"run retry --retry {retry_time_count}")
        else:
            self.__send_cts_command(f"run retry --retry {retry_time_count} --retry_type {self.retry_type}")            
        self.command_done.wait(timeout=WAIT_PROCESS_TIMEOUT)

    def __run_retry(self):
        if self.retry_time <= 0:
            logger.info(f"{CTS_RUNNER_PREFIX} No trigger rerun!")
        else:
            time.sleep(30)
            if "retry" in self.cmd:
                for retry_time_count in range(1,self.retry_time+1):
                    self.__retry_time_count(retry_time_count)
            else:
                for retry_time_count in range(0,self.retry_time):
                    self.__retry_time_count(retry_time_count)

    def __execute_cts_run_command_and_retry(self):
        self.cts_tf_proc = self.__open_tradefed_session()
        if self.restart:
            logger.info(f"{CTS_RUNNER_PREFIX} We wait {WAIT_ADB_REBOOT_TIME} secs for restarting device")
            time.sleep(WAIT_ADB_REBOOT_TIME)

        # Bắt đầu thread đọc output sau khi proc được khởi tạo
        logger.info(f"{CTS_RUNNER_PREFIX} Start thread reading output")
        output_thread = threading.Thread(target=self.__read_output, name="CTSOutputThread", daemon= True)
        output_thread.start()

        # Bắt đầu thread đọc error sau khi proc được khởi tạo
        logger.info(f"{CTS_RUNNER_PREFIX} Start thread reading error")
        error_thread = threading.Thread(target=self.__read_error, name="CTSErrorThread", daemon= True)
        error_thread.start()

        self.command_done.clear()
        self.__send_cts_command(self.cmd)
        self.command_done.wait(timeout=WAIT_PROCESS_TIMEOUT)

        self.__run_retry()
        if self.command_done.is_set() == False:
            self.command_done.wait(timeout=WAIT_PROCESS_TIMEOUT)
        self.__send_cts_command("exit")

        output_thread.join()
        error_thread.join()

    def monitoring_avd(self):
        self.avd = AVDHandler(
            name = "Automotive_1408p_landscape_with_Google_Play_1",
            emulator_path = '/home/'+getpass.getuser()+'/Android/Sdk/emulator/emulator',
            timeout = 3,
            is_headless = self.is_headless,
            restart_avd = self.restart
        )
        self.avd.keep_avd_alive()

    def run_cts(self):
        if self.device_type == DeviceType.AVD:
            logger.info(f"{CTS_RUNNER_PREFIX} Initialize Thread AVD")
            monitor_thread = threading.Thread(target=self.monitoring_avd, daemon=True)  # daemon để tự thoát khi main thread kết thúc
            monitor_thread.start()
        else:
            logger.info(f"{CTS_RUNNER_PREFIX} Checking DUT status")
            # Now check if boot completed
            proc = subprocess.run(
                ["adb", "shell", "getprop", "sys.boot_completed"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            if proc.returncode != 0:
                logger.error("%s Connection error: %s", CTS_RUNNER_PREFIX, proc.stderr.strip())
                raise RuntimeError("ADB command failed")

            logger.info(f"{CTS_RUNNER_PREFIX} Checking DUT status : OK")
            if self.restart:
                logger.info(f"{CTS_RUNNER_PREFIX} Restarting the device")
                subprocess.run(["adb", "reboot"], check=False)

        logger.info(f"{CTS_RUNNER_PREFIX} Initialize Thread CTS")
        cts_thread = threading.Thread(target=self.__execute_cts_run_command_and_retry)
        logger.info(f"{CTS_RUNNER_PREFIX} Start Thread CTS")
        cts_thread.start()
        
        cts_thread.join() 
        logger.info(f"{CTS_RUNNER_PREFIX} End Thread CTS and AVD")
        if cts_thread.is_alive():
            logger.error(f"{CTS_RUNNER_PREFIX} Timeout. CTS không thoát được.")
            self.__kill_cts_tradefed()
            self.avd.close_avd()

        logger.info(f"{CTS_RUNNER_PREFIX} CTS execution finished.")