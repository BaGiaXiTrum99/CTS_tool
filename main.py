import argparse
from src.create_subsplans_xml.create_subplans_xml import *
from src.gen_report_excel.ResultXMLParser import *
from src.gen_report_excel.ResultXMLParser_CTS_V import *
from utils.logging_setup import *
from dotenv import load_dotenv

MODULE_LIST = [
        "x86_64 CtsAccessibilityServiceTestCases",
        "x86_64 CtsAnimationTestCases",
        "x86_64 CtsAppExitTestCases",
        "x86_64 CtsAppExitTestCases[instant]",
        "x86_64 CtsAppFgsTestCases[instant]",
        "x86_64 CtsAppSecurityHostTestCases",
        "x86_64 CtsAppTestCases",
        "x86_64 CtsAppTestCases[instant]",
        "x86_64 CtsBionicTestCases",
        "x86_64 CtsBluetoothTestCases",
        "x86_64 CtsClasspathDeviceInfoTestCases",
        "x86_64 CtsCompanionDeviceManagerUiAutomationTestCases",
        "x86_64 CtsDisplayTestCases",
        "x86_64 CtsDisplayTestCases[instant]",
        "x86_64 CtsMediaDecoderTestCases",
        "x86_64 CtsMediaStressTestCases",
        "x86_64 CtsMediaV2TestCases",
        "x86_64 CtsNotificationTestCases",
        "x86_64 CtsDevicePolicyManagerTestCases",
        "x86_64 CtsGraphicsTestCases",
        "x86_64 CtsGraphicsTestCases[instant]",
        "x86_64 CtsInputTestCases",
        "x86_64 CtsUiRenderingTestCases",
    ]

def handle_gen_subplan(args):
    if args.module_list is None:
        module_list = None
    else:
        module_list = MODULE_LIST
    logger.info(f"Running Feature Generate Subplan with args: {args}")

    generator = SubplanGenerator(module_list, args.folder_path, int(args.file_num))
    generator.gen_xml_file()

def handle_gen_report(args):
    logger.info(f"Running Feature Generate Report CTS with args: {args}")
    parser = ResultXMLParser(args.path,args.time_unit,args.abi)
    parser.parser_all_modules(
        subplans_path=args.subplans_path
    )

def handle_gen_report_CTS_V(args):
    logger.info(f"Running Feature Generate Report CTS Verifier with args: {args}")
    parser = ResultXMLParser_CTS_V(args.path,args.time_unit)
    parser.parser_all_modules()

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Tool đa chức năng cho CTS")

    default_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    parser.add_argument(
        '--log_level',
        type=str,
        default=default_log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f'Đặt cấp độ logging (DEBUG, INFO, WARNING, ERROR, CRITICAL). Mặc định: {default_log_level} (từ .env hoặc INFO).'
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Feature 1: gen-subplan ---
    subplan_parser = subparsers.add_parser("gen-subplan", help="Sinh file subplans XML")
    subplan_parser.add_argument("--module_list", required=False, help="Danh sách module cần chạy")
    subplan_parser.add_argument("--folder_path", required=False, default= "./subplans", help="Đường dẫn folder để lưu file subplan XML")
    subplan_parser.add_argument("--file_num", required=False, default= 1, help="Số lượng file subplan có thể được gen ra")
    subplan_parser.set_defaults(func=handle_gen_subplan)

    # --- Feature 2: gen-report ---
    report_parser = subparsers.add_parser("gen-report", help="Phân tích kết quả và sinh báo cáo Excel CTS")
    report_parser.add_argument("--path", required=False, default = './data/2025.07.10_08.36.27.870_3983', help="Thư mục chứa test_result.xml")
    report_parser.add_argument("--time_unit", choices=["ms", "s", "h/m/s"], default="h/m/s", help="Đơn vị thời gian")
    report_parser.add_argument("--abi", default="x86_64", help="Processor máy của bạn")
    report_parser.add_argument("--subplans_path", default=None, help="Nơi lưu báo cáo Excel")
    report_parser.set_defaults(func=handle_gen_report)

    # --- Feature 2: gen-report CTS-V ---
    report_ctsV_parser = subparsers.add_parser("gen-report-CTS-V", help="Phân tích kết quả và sinh báo cáo Excel CTS")
    report_ctsV_parser.add_argument("--path", required=False, default = './data/CTS_V', help="Thư mục chứa test_result.xml")
    report_ctsV_parser.add_argument("--time_unit", choices=["ms", "s", "h/m/s"], default="h/m/s", help="Đơn vị thời gian")
    report_ctsV_parser.set_defaults(func=handle_gen_report_CTS_V)

    # Parse và gọi hàm tương ứng
    args = parser.parse_args()
    configure_logger(args.log_level) 
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()




