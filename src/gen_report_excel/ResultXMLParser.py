import os
import re
import math
import xml.etree.cElementTree as ET
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from utils.logger import get_logger
from utils.time_caculation import *
from xml.etree.ElementTree import Element
from src.gen_report_excel.SubplansParser import SubplansParser

logger = get_logger()

class ResultHTMLParser:
    def __init__(self, path: str, time_unit : str, abi: str) -> None:
        logger.info("Generate Report Feature")
        self.result_path = f"{path}/test_result.xml"
        self.abi = abi    
        self.time_unit = time_unit
        self.__root = self.__read_result_file()
    
    def __read_result_file(self):
        logger.info(f"Reading XML result file {self.result_path}")
        tree = ET.parse(self.result_path)   
        return tree.getroot()     
    
    def get_module_runner(self):
        list_module = self.__root.findall('.Module')
        logger.info(f"Found {len(list_module)} in result file {self.result_path}")
        return list_module

    def parser_all_modules(self , subplans_path : str ):
        module_count = 1
        wb = Workbook()

        active_sheet = wb.active
        if active_sheet is None:
            raise ValueError("No active sheet found in workbook.")

        ws: Worksheet = active_sheet 
        ws.title = "CTS Report"

        # Ghi header
        headers = [
            "No", 
            "Modules",
            "Passed",
            "Failed",
            "Assumption Failure",
            "Ignored",
            "Total",
            "Done",
            "Execution Time"
            ]
        
        ws.append(headers)
        totals = {
            "Passed": 0,
            "Failed": 0,
            "Assumption Failure": 0,
            "Ignored": 0,
            "Total": 0,
            "Execution Time": "0s" if self.time_unit == TimeUnit.HMS.value else 0,
            "Done": True
        }

        subplan_parser = SubplansParser(subplans_path)
        module_list_from_subplans = subplan_parser.get_module_list_from_subplans()
        modules_runner = self.get_module_runner()

        for idx in range(len(module_list_from_subplans)):
            module_name_from_subplans = module_list_from_subplans[idx]
            matched = False
            for module in modules_runner:
                module_name = module.get('name')
                if module_name_from_subplans == module_name:
                    matched = True
                    logger.info(f"Found module {module_name} existed in DUT, start parsing")
                    module_infor = self.__parser_module(module, self.time_unit)
                    row = [idx+1] + [module_infor[h] for h in headers[1:]]
                    for key in ("Passed", "Failed", "Assumption Failure", "Ignored", "Total"):
                        totals[key] += module_infor[key]

                    if self.time_unit == TimeUnit.HMS.value:
                        totals["Execution Time"] = sum_durations(totals["Execution Time"],module_infor["Execution Time"])
                    else:
                        totals["Execution Time"] = sum((x for x in re.findall(r'\d+',module_infor["Execution Time"])), totals["Execution Time"])
                    
                    totals["Done"] = totals["Done"] and module_infor["Done"]
                    module_count += 1
                    ws.append(row)
                    break
            if not matched: 
                logger.info(f"Found module {module_name_from_subplans} not existed in DUT, end parsing")
                ws.append([idx+1, module_name_from_subplans,0,0,0,0,0,True,"0s" if self.time_unit == TimeUnit.HMS.value else 0])

        if self.time_unit == TimeUnit.S.value:
            totals["Execution Time"] = str(totals["Execution Time"]) + "s" 
        elif self.time_unit == TimeUnit.MS.value:
            totals["Execution Time"] = str(totals["Execution Time"]) + "ms" 

        total_row = ["Total", ""] + [totals[k] for k in headers[2:]]
        ws.append(total_row)

        result_path = "./result/myresult.xlsx"
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        wb.save(result_path)
        logger.info(f"Saved result to {result_path}")

    def __parser_module(self,module : Element , time_unit : str) -> dict:
        name = module.get("name")
        logger.info(f"Parsing module {name}")

        execution_time = int(module.get("runtime")) #type: ignore
        if time_unit == TimeUnit.HMS.value:
            execution_time = format_duration(math.ceil(execution_time/1000)) #type: ignore
            time_unit = ''
        elif time_unit == TimeUnit.S.value:
            execution_time = str(math.ceil(execution_time/1000)) + "s" #type: ignore
        elif time_unit == TimeUnit.MS.value:
            execution_time = str(execution_time) + "ms"
        logger.info(f"Execution Time: {execution_time} {time_unit}")
        
        done = True if module.get("done") == "true" else False
        logger.info(f"Done: {done}")

        test_cases = module.findall(".TestCase")
        logger.info(f"Found {len(test_cases)} test cases")

        pass_count = 0
        fail_count = 0
        assumption_failure = 0
        ignored = 0
        for test_case in test_cases:
            logger.debug(f"Parsing test case {test_case.get('name')}")
            for test_step in test_case.findall(".Test"):
                test_step_name = test_step.get('name')
                test_step_result = test_step.get("result")
                if test_step_result == "fail":
                    fail_count += 1
                    logger.debug(f"Test case {test_step_name} failed")
                elif test_step_result == "ASSUMPTION_FAILURE":
                    assumption_failure += 1
                    logger.debug(f"Test case {test_step_name} assumption failure")
                elif test_step_result == "IGNORED":
                    ignored += 1
                    logger.debug(f"Test case {test_step_name} ignored")
                else:
                    pass_count += 1
                    logger.debug(f"Test case {test_step_name} passed")

        total_tests_str = module.get("total_tests")
        logger.info(f"Found {total_tests_str} tests")
        total_testcases = int(total_tests_str) if total_tests_str else 0

        assert total_testcases == pass_count + fail_count + assumption_failure + ignored, \
            f"Test count mismatch: {total_testcases} vs {pass_count} + {fail_count} + {assumption_failure} + {ignored}"
        
        return {
            "Modules": name,
            "Passed": pass_count,
            "Failed": fail_count,
            "Assumption Failure" : assumption_failure,
            "Ignored": ignored,
            "Total": total_testcases,
            "Done": done,
            "Execution Time": execution_time
        }
    
    

    
