from enum import Enum

class TimeUnit(Enum):
    HMS = "h/m/s"
    MS  = "ms"
    S   = "s" 

class ReportColumn(Enum):
    NO = "No"
    MODULES = "Modules"
    PASSED = "Passed"
    FAILED = "Failed"
    ASSUMPTION_FAILURE = "Assumption Failure"
    IGNORED = "Ignored"
    TOTAL = "Total"
    DONE = "Done"
    EXECUTION_TIME = "Execution Time"

class ReportColumnCTS_V(Enum):
    NO = "No"
    TEST = "Test"
    RESULT = "Result"
    EXECUTION_TIME = "Execution Time"

class ReportTriageColumns(Enum):
    NO = "No"
    MODULES = "Modules"
    TEST_CASE = "Test Case"
    RESULT = "Result"
    DETAIL = "Detail"
    LOG_FOLDER = "Log Folder"
    
class CTSRetryType(Enum):
    DEFAULT = "DEFAULT"
    NOT_EXECUTED = "NOT_EXECUTED"
    FAILED = "FAILED"

class DeviceType(Enum):
    DUT = "DUT"
    AVD = "AVD"