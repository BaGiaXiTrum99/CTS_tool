import logging

logger = logging.getLogger("cts_logger." + __name__)

class CTSHandler:
    def __init__(self,android_cts_path : str ,cmd : str ,retry_time : int ,retry_type : str, need_avd_alive : str):
        self.android_cts_path = android_cts_path
        self.cmd = cmd
        self.retry_time = retry_time
        self.retry_type = retry_type
        self.need_avd_alive = need_avd_alive.upper()

    def run():
        pass