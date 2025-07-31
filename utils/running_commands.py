import subprocess
import time 
import keyboard
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
            text=True,  # Decode bytes to str
            check=False
        )       

        stdout , stderr = process.communicate()
        logger.info(f"Closing process")
        logger.debug(f"Output : ", stdout)
        logger.debug(f"Error : ", stderr)
        return stdout , stderr

    @staticmethod
    def execute_timeout_cmd(cmd , timeout : int = 60):
        logger.info(f"Running command with timeout: {cmd}")
        logger.debug(f"Timeout set {timeout}")
        start_time = time.time()
        process = subprocess.Popen(
            cmd,
            shell=True,
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            check=False
        )
        try:
            while time.time() - start_time < timeout:
                if keyboard.is_pressed('q'):
                    logger.debug(f"User Cancellation")
                    break
                stdout, stderr = process.stdout.read(),process.stderr.read() # type: ignore
                logger.debug(f"Output : ", stdout)
                logger.debug(f"Error : ", stderr)
        finally:
            logger.info(f"Closing process")
            process.terminate()
            stdout, stderr = None , None
        
        return stdout, stderr
