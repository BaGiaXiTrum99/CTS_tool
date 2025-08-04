import re
import os
import math
import logging
from utils.running_commands import Commands

logger = logging.getLogger("cts_logger." + __name__)

class SubplanGenerator:
    def __init__(self, module_list : list[str] | None, folder_path : str , file_num : int) -> None:
        logger.info("Generate Subplans Feature")
        if module_list is None:
            logger.info("Auto Capture Modules from DUT")
            self.module_list = self.__get_module_list_exist_in_DUT()
        else:
            logger.info("Capture Modules from Input")
            self.module_list = module_list
        self.folder_path = folder_path
        self.file_num = file_num
    
    def __write_module_to_file(self,modules, file):
        logger.info(f"Writing file {file} Start")
        with open(file,'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>\n')
            f.writelines('<SubPlan version="2.0">\n')
            for module in modules:
                f.writelines('\t<Entry include="{}" />\n'.format(module))
            f.writelines('</SubPlan>')
        logger.info(f"Writing file {file} Done")

    def gen_xml_file(self):
        module_count = len(self.module_list)
        logger.info(f"Separating {module_count} modules into {self.file_num} files")
        os.makedirs(self.folder_path,exist_ok=True)

        chunk_size = math.ceil(module_count / self.file_num) # làm tròn lên
        for num in range(self.file_num):
            start_index = num * chunk_size
            end_index = start_index + chunk_size
            module_chunk = self.module_list[start_index:end_index]
            separate_filename = f"{self.folder_path}/myplan_{num+1}.xml"
            logger.info(f"Write modules to file {separate_filename}")
            self.__write_module_to_file(module_chunk,separate_filename)

    def __get_module_list_exist_in_DUT(self) -> list[str]:
        cmd: str | list = "/home/vmo/Documents/CTS/android-cts-14_r7-linux_x86-x86/android-cts/tools/cts-tradefed list modules"
        stdout, _ = Commands.execute_short_cmd(cmd)

        # Bắt các dòng bắt đầu bằng x86_64 hoặc x86 và không có [secondary_user]
        pattern = r"^(?:x86_64|x86)\s+([^\[\]\s]+)$"
        matches = re.findall(pattern, stdout, re.MULTILINE)

        unique_modules = sorted(set(matches))
        for module in unique_modules:
            logger.info(f"Found module: {module}")

        logger.info(f"Total unique modules: {len(unique_modules)}")
        return unique_modules
