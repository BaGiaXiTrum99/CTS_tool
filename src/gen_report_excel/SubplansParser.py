import logging
import xml.etree.cElementTree as ET

logger = logging.getLogger("cts_logger." + __name__)

class SubplansParser:
    def __init__(self,output_path : str) -> None:
        self.subplans_path = output_path
        self.__root = self.__read_result_file()
    
    def __read_result_file(self):
        logger.info(f"Reading XML subplan file {self.subplans_path}")
        tree = ET.parse(self.subplans_path)   
        return tree.getroot()    

    def get_module_list_from_subplans(self) -> list:
        modules = self.__root.findall('.Entry')        
        module_name = [module.get("include") for module in modules]
        logger.info(f"Found {len(module_name)} modules in subplans {self.subplans_path}")
        return module_name


