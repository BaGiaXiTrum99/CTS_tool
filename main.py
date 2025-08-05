import argparse
import getpass
from src.create_subsplans_xml.create_subplans_xml import *
from src.gen_report_excel.ResultXMLParser import *
from src.gen_report_excel.MultiResultXMLParser import *
from src.gen_report_excel.ResultXMLParser_CTS_V import *
from src.avd_handler.avd_handler import *
from src.cts_handler.cts_handler import *
from utils.logging_setup import *
from dotenv import load_dotenv

MODULE_LIST = [
        "x86_64 CtsAccessibilityServiceTestCases",
        "x86_64 CtsAnimationTestCases",
        "x86_64 CtsAppExitTestCases",
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
    parser = ResultXMLParser(args.path,args.time_unit)
    parser.parser_all_modules(
        subplans_path=args.subplans_path
    )

def handle_multi_gen_report(args):
    logger.info(f"Running Feature Generate Multiple Report CTS with args: {args}")
    parser = MultiResultXMLParser(args.path,args.time_unit)
    parser.parsing_all_results_file()

def handle_gen_report_CTS_V(args):
    logger.info(f"Running Feature Generate Report CTS Verifier with args: {args}")
    parser = ResultXMLParser_CTS_V(args.path,args.time_unit)
    parser.parser_all_modules()

def handle_avd(args):
    logger.info(f"Running Feature Keep AVD alive with args: {args}")
    avd = AVDHandler(args.name,args.emulator_path,args.timeout,args.is_headless,args.restart_avd)
    avd.keep_avd_alive()

def handle_cts_runner(args):
    logger.info(f"Running Feature Run CTS continuously with args: {args}")
    cts_runner = CTSHandler(args.android_cts_path,args.cmd,args.retry_time,args.retry_type,args.restart_avd)
    cts_runner.run_cts()

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
    report_parser.add_argument("--path", required=False, default = './data/2025.07.10_08.36.27.870_3983', help="thư mục chứa report của CTS")
    report_parser.add_argument("--time_unit", choices=["ms", "s", "h/m/s"], default="h/m/s", help="Đơn vị thời gian")
    report_parser.add_argument("--subplans_path", default=None, help="Nơi lưu báo cáo subplans, dùng để check các test module không chạy được trên DUT nhưng lại xuất hiện trên subplan")
    report_parser.set_defaults(func=handle_gen_report)

    # --- Feature 3: gen-report CTS-V ---
    report_ctsV_parser = subparsers.add_parser("gen-report-CTS-V", help="Phân tích kết quả và sinh báo cáo Excel CTS Verifier")
    report_ctsV_parser.add_argument("--path", required=False, default = './data/CTS_V', help="Thư mục chứa test_result.xml")
    report_ctsV_parser.add_argument("--time_unit", choices=[timeunit.value for timeunit in TimeUnit], default=TimeUnit.HMS.value, help="Đơn vị thời gian")
    report_ctsV_parser.set_defaults(func=handle_gen_report_CTS_V)

    # --- Feature 4: Restart AVD ---
    avd_parser = subparsers.add_parser("keep-avd-alive", help="Tự động khởi động lại avd nếu bị crash")
    avd_parser.add_argument("--name", required=False, default = 'Automotive_1408p_landscape_with_Google_Play_1', help="AVD name")
    avd_parser.add_argument("--emulator_path", required=False, default = '/home/'+getpass.getuser()+'/Android/Sdk/emulator/emulator', help="Đường dẫn tới android emulator")
    avd_parser.add_argument("--timeout", type=int, default = 2, help="Timeout (days) của feature này")
    avd_parser.add_argument("--is_headless", type=str, default = "False", help="True nếu chạy avd ở chế độ headless")
    avd_parser.add_argument("--restart_avd",required=False, type=str, default = os.getenv("NEED_RESTART_AVD", "True"), help = "True nếu muốn restart lại avd để refresh môi trường, False nếu bạn muốn giữ lại để debug")
    avd_parser.set_defaults(func=handle_avd)

    # --- Feature 5: Run CTS Continuously ---
    cts_runner_parser = subparsers.add_parser("cts-runner", help="Tự động chạy CTS command và retry theo option")
    cts_runner_parser.add_argument("--android_cts_path",required=False, default = '/home/'+getpass.getuser()+'/Documents/CTS/'+os.getenv("CTS_VERSION_NAME","android-cts-14_r7-linux_x86-x86")+'/android-cts', help = 'Đường dẫn tới thư mục andoird-cts')
    cts_runner_parser.add_argument("--cmd", required=False, default = os.getenv("CTS_COMMAND", "run cts -m CtsPerfettoTestCases -t HeapprofdCtsTest#ReleaseAppRuntime"), help="Command chạy CTS trong CTS-Tradefed")
    cts_runner_parser.add_argument("--retry_time",required=False, type = int, default = os.getenv("CTS_RETRY_TIME", 5), help = "Số lần retry ( không bao gồm lần đầu chạy)")
    cts_runner_parser.add_argument("--retry_type",required=False, choices=[retry_type.value for retry_type in CTSRetryType], default = os.getenv("CTS_RETRY_TYPE", CTSRetryType.DEFAULT.value), help = "Kiểu retry, chọn giữa DEFAULT, NOT_EXECUTED hay FAILED")
    cts_runner_parser.add_argument("--restart_avd",required=False, type=str, default = os.getenv("NEED_RESTART_AVD", "True"), help = "True nếu muốn restart lại avd để refresh môi trường, False nếu bạn muốn giữ lại để debug")
    cts_runner_parser.set_defaults(func=handle_cts_runner)

    # --- Feature 6: gen-report-cts-with-retry ---
    multi_report_parser = subparsers.add_parser("multi-gen-report", help="Phân tích nhiều file kết quả và sinh báo cáo Excel CTS")
    multi_report_parser.add_argument("--path", required=False, default = './data/results_CTS', help="Thư mục chứa các report folder của CTS")
    multi_report_parser.add_argument("--time_unit", choices=["ms", "s", "h/m/s"], default="h/m/s", help="Đơn vị thời gian")
    multi_report_parser.set_defaults(func=handle_multi_gen_report)

    # Parse và gọi hàm tương ứng
    args = parser.parse_args()
    configure_logger(args.log_level) 
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()




