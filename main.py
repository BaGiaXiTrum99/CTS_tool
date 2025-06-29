import argparse
from src.create_subsplans_xml.create_subplans_xml import *
from src.gen_report_excel.ResultXMLParser import *

MODULE_LIST = [
    "CtsCompanionDeviceManagerMultiDeviceTestCases",
    "CtsConnectivityMultiDevicesTestCases",
    "CtsContactKeysManagerTestCases",
    "CtsContactKeysProviderPrivilegedApp",
    "CtsContextualSearchServiceTestCases",
    "CtsCorruptApkHostTestCases",
    "CtsCrashDetailHostTestCases",
    "CtsCredentialManagerHostSideTestCases",
    "CtsDeleteKeepDataHostTestCases",
    "CtsDeqpTestCases",
    "CtsDirectBootHostTestCases",
    "CtsDocumentContentTestCases",
    "CtsDropBoxManagerTestCasesAPI34",
    "CtsDynamicMimeChangedGroupAppUpdateHostTestCases",
    "CtsDynamicMimeComplexFilterClearGroupRebootHostTestCases",
    "CtsDynamicMimeComplexFilterRebootHostTestCases",
    "CtsDynamicMimeIndependentGroupRebootHostTestCases",
    "CtsDynamicMimePreferredActivitiesHostTestCases",
    "CtsDynamicMimeRemoveRebootHostTestCases",
    "CtsDynamicMimeSingleAppGroupRebootHostTestCases",
    "CtsDynamicMimeSingleAppRebootHostTestCases",
    "CtsExerciseRouteTestCases",
    "CtsFgsTimeoutTestCases",
    "CtsFingerprintTestCases",
    "CtsGameServiceTestCases",
    "CtsGetBindingUidImportanceTest",
    "CtsHealthFitnessDeviceTestCasesHistoricAccessLimitWithPermission",
    "CtsHealthFitnessDeviceTestCasesNotAllPermissionsAreGranted",
    "CtsHealthFitnessDeviceTestCasesRateLimiter",
    "CtsHealthFitnessShowMigrationInfoIntentAbsentTests",
    "CtsHostsideNetworkPolicyTests",
    "CtsInputMethodInstallTestCases",
    "CtsInputMethodServiceHostTestCases"
    ]

def handle_gen_subplan(args):
    if args.module_list is None:
        module_list = None
    else:
        module_list = MODULE_LIST
    generator = SubplanGenerator(module_list, args.folder_path, int(args.file_num))
    generator.gen_xml_file()

def handle_gen_report(args):
    parser = ResultHTMLParser(args.path,args.time_unit,args.abi)
    parser.parser_all_modules(
        subplans_path=args.subplans_path
    )

def main():
    parser = argparse.ArgumentParser(description="Tool đa chức năng cho CTS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Feature 1: gen-subplan ---
    subplan_parser = subparsers.add_parser("gen-subplan", help="Sinh file subplans XML")
    subplan_parser.add_argument("--module_list", required=False, help="Danh sách module cần chạy")
    subplan_parser.add_argument("--folder_path", required=False, default= "./subplans", help="Đường dẫn folder để lưu file subplan XML")
    subplan_parser.add_argument("--file_num", required=False, default= 1, help="Số lượng file subplan có thể được gen ra")
    subplan_parser.set_defaults(func=handle_gen_subplan)

    # --- Feature 2: gen-report ---
    report_parser = subparsers.add_parser("gen-report", help="Phân tích kết quả và sinh báo cáo Excel")
    report_parser.add_argument("--path", required=False, default = './data/2025.06.27_11.30.02.391_8731', help="Thư mục chứa test_result.xml")
    report_parser.add_argument("--time_unit", choices=["ms", "s", "h/m/s"], default="h/m/s", help="Đơn vị thời gian")
    report_parser.add_argument("--abi", default="x86_64", help="Processor máy của bạn")
    report_parser.add_argument("--subplans_path", default="./subplans/myplan_1.xml", help="Nơi lưu báo cáo Excel")
    report_parser.set_defaults(func=handle_gen_report)

    # Parse và gọi hàm tương ứng
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()




