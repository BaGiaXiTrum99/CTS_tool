import subprocess
import time 
import keyboard
from utils.logger import get_logger

logger = get_logger() 

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
        logger.debug(f"Closing process")
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
            text=True
        )
        try:
            while time.time() - start_time < timeout:
                if keyboard.is_pressed('q'):
                    logger.debug(f"User Cancellation")
                    break
                stdout, stderr = process.stdout.read(),process.stderr.read() # type: ignore
        finally:
            logger.debug(f"Closing process")
            process.terminate()
            stdout, stderr = None , None
        
        return stdout, stderr
