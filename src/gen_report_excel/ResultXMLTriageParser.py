import os
import re
import logging
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import Element,ElementTree
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from datetime import datetime

from utils.constants import *
from utils.ExcelHandler import ExcelHandler

logger = logging.getLogger("cts_logger." + __name__)

class ResultXMLTriageParser:
    def __init__(self, path: str, time_unit : str, output_dir: str ) -> None:
        logger.info("Generate Report CTS Triage Feature")
        self.result_path = os.path.abspath(path)
        self.time_unit = time_unit
        self.output_dir = output_dir
        self.index_row = 1

    def __search_all_single_result_folder(self):
        report_files = []
        for subfolder in os.scandir(self.result_path):
            if subfolder.is_dir():
                if os.path.exists(subfolder.path+'/test_result.xml'):
                    logger.info(f'Found valid folder path {subfolder.path}')
                    report_files.append(subfolder.path+'/test_result.xml')
                else:
                    logger.error(f'Folder {subfolder.path} is not containing test_result.xml, can not parse')
        assert len(report_files), 'Length of results not be zero!!!'
        return sorted(report_files)

    def __get_root_of_result_file(self,report_file):
        logger.info(f"Reading XML result file {report_file}")
        try:
            tree = ET.parse(report_file)
        except ET.ParseError as e:
            msg = f"Failed to parse XML file {report_file}: {e}"
            logger.error(msg)
            raise RuntimeError(msg)
        return tree.getroot()     

    def __get_list_modules_name(self, root : ElementTree):
        list_modules = root.findall('.Module')
        logger.info(f"Found {len(list_modules)} module(s)")
        return list_modules
    
    def __parser_module_to_excel(self,ws : Worksheet, module : Element , report_file : str) -> dict:
        name = module.get("name")
        logger.info(f"Parsing module {name}")

        total_tests_str = module.get("total_tests")
        assert total_tests_str is not None, "Can not get total test of module"
        logger.info(f"Found {total_tests_str} tests")
        total_testcases = int(total_tests_str) if total_tests_str else 0

        test_cases = module.findall(".TestCase")
        logger.info(f"Found {len(test_cases)} test cases")

        test_cnt = 0
        for test_case in test_cases:
            logger.debug(f"Parsing test case {test_case.get('name')}")
            for test_step in test_case.findall(".Test"):
                test_step_name = test_step.get('name')
                
                test_step_result = test_step.get("result")
                logger.debug(f"Found Test {test_step_name} with result {test_step_result}") 
                
                # TODO: Add them log fail từ StackTrace 
                if test_step_result == "fail":
                    failure_message = test_step.find(".Failure").get("message")
                    logger.debug(f"Got fail message: {failure_message}")
                else:
                    failure_message = None

                test_case_infor = {
                    ReportTriageColumns.MODULES.value  : name,
                    ReportTriageColumns.TEST_CASE.value   : test_step_name,
                    ReportTriageColumns.RESULT.value   : test_step_result,
                    ReportTriageColumns.DETAIL.value : failure_message,
                    ReportTriageColumns.LOG_FOLDER.value : report_file
                }
                test_cnt += 1
                self.__write_module_row(ws,test_case_infor)

        if total_testcases != test_cnt:
            msg = f"Mismatch test count in {name}: total={total_testcases}, counted={test_cnt}"
            logger.error(msg)
            raise ValueError(msg)

    def __write_module_row(self, ws: Worksheet, module_data: dict):
        row = [self.index_row] + [module_data[col.value] for col in list(ReportTriageColumns)[1:]]
        logger.debug(f"Append row {row} to Excel")
        ws.append(row)
        self.index_row += 1

    def parsing_all_results_file(self):
        wb = Workbook()

        ws : Worksheet = wb.create_sheet(title="CTS Triage Report",index = 0)
        ws = ExcelHandler.create_header_row(ws)

        report_files = self.__search_all_single_result_folder()
        for report_file in report_files:
            logger.info(f"Parsing XML result file {report_file}")
            root = self.__get_root_of_result_file(report_file)
            modules = self.__get_list_modules_name(root)
            for module in modules:
                self.__parser_module_to_excel(ws, module, os.path.basename(os.path.dirname(report_file)))

        output_file = f"{self.output_dir}/myresult_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        wb.save(output_file)
        logger.info(f"Saved result to {output_file}")
