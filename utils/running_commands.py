import subprocess
import time 
import logging

logger = logging.getLogger("cts_logger." + __name__)

class Commands:
    @staticmethod
    def execute_short_cmd(cmd):
        logger.info(f"Running command with short time: {cmd}")
        process = subprocess.Popen(
            cmd,
            shell=isinstance(cmd,str),
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True  # Decode bytes to str
        )       

        stdout , stderr = process.communicate()
        logger.info(f"Closing process for command {cmd}")
        logger.debug(f"Output : {stdout}")
        logger.debug(f"Error : {stderr}")
        return stdout , stderr

    @staticmethod
    def execute_timeout_cmd(cmd , timeout : int|None = 60):
        logger.info(f"Running command with timeout: {cmd}")
        logger.info(f"Timeout set {timeout}")
        start_time = time.time()
        process = subprocess.Popen(
            cmd,
            shell=True,
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True  # Decode bytes to str
        )
        if timeout is None:
            try:
                logger.info("Not setting timeout for running, we wait 60 seconds for some outputs")
                process.wait(60)
            except subprocess.TimeoutExpired as e:
                logger.info("Timeout for output reached, leaving process without closing it")
        else:
            try:
                while time.time() - start_time < timeout:
                    stdout, stderr = process.stdout.read(),process.stderr.read() # type: ignore
                    logger.debug(f"Output : {stdout}")
                    logger.debug(f"Error : {stderr}")
            finally:
                logger.info(f"Closing process for command {cmd}")
                process.terminate()
        return process
