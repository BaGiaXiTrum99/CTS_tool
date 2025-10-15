import logging
import time
import subprocess
import threading

from utils.process_handler import ProcessHandler
from utils.running_commands import Commands
from src.avd_handler.avd_handler import CTS_PROCESS_NAME
from src.cts_handler.cts_handler import END_STRING,CTS_RUNNER_PREFIX

WAIT_PROCESS_TIMEOUT = 10000
WAIT_ADB_REBOOT_TIME = 45
ADB_LOST_CONNECTION_MSG = "error: no devices/emulators found"
logger = logging.getLogger("cts_logger." + __name__)

class CTSCmdFileHandler:
    def __init__(self, android_cts_path : str, cmd_file_path : str , device_type : str, restart : bool):
        self.android_cts_path = android_cts_path
        self.cts_tradefed = self.android_cts_path + '/tools/cts-tradefed'
        self.cmd_file_path = cmd_file_path
        self.device_type = device_type
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
        time.sleep(2)
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

    def __terminate_program(self):
        self.__send_cts_command("exit")
        self.__kill_cts_tradefed()
        logger.info(f"{CTS_RUNNER_PREFIX} CTS execution finished.")

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

    def __read_cmd_file(self) -> list:
        with open(self.cmd_file_path,'r') as f:
            cmd_list = f.readlines()
        return [cmd.strip() for cmd in cmd_list if cmd.strip() != ""]

    def run_cts_by_cmdfile(self):
        logger.info(f"{CTS_RUNNER_PREFIX} Initialize Thread CTS")
        self.cts_tf_proc = self.__open_tradefed_session()

        # Bắt đầu thread đọc output sau khi proc được khởi tạo
        logger.info(f"{CTS_RUNNER_PREFIX} Start thread reading output")
        output_thread = threading.Thread(target=self.__read_output, name="CTSOutputThread", daemon= True)
        output_thread.start()

        # Bắt đầu thread đọc error sau khi proc được khởi tạo
        logger.info(f"{CTS_RUNNER_PREFIX} Start thread reading error")
        error_thread = threading.Thread(target=self.__read_error, name="CTSErrorThread", daemon= True)
        error_thread.start()

        cmd_list = self.__read_cmd_file()
        for cmd in cmd_list:
            self.command_done.clear()
            if self.restart:
                logger.info(f"{CTS_RUNNER_PREFIX} We wait {WAIT_ADB_REBOOT_TIME} secs for restarting device")
                _,stderr = Commands.execute_short_cmd("adb reboot")
                if ADB_LOST_CONNECTION_MSG in stderr:
                    break
                time.sleep(WAIT_ADB_REBOOT_TIME)
            self.__send_cts_command(cmd)
            if self.command_done.is_set() == False:
                self.command_done.wait(timeout=WAIT_PROCESS_TIMEOUT)

        self.__terminate_program()



