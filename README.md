# CTS Automation Tool

Công cụ đa chức năng này được thiết kế để tự động hóa các tác vụ liên quan đến việc chạy và phân tích kết quả từ bộ kiểm thử Compatibility Test Suite (CTS) của Android. Nó cung cấp các tính năng để tạo các kế hoạch chạy thử (subplans) và phân tích các tệp kết quả XML để tạo báo cáo Excel chi tiết.

## Tính năng

* **Tạo Subplans XML**: Tự động tạo các tệp XML subplan dựa trên danh sách module được cung cấp hoặc tự động thu thập các module có sẵn trên thiết bị đang kiểm tra (DUT). Các module có thể được chia thành nhiều tệp subplan để quản lý việc chạy thử dễ dàng hơn.
* **Phân tích kết quả và tạo báo cáo Excel**: Phân tích tệp `test_result.xml` do CTS tạo ra và sinh ra một báo cáo Excel chi tiết. Báo cáo này bao gồm thông tin về các module đã chạy, số lượng test case Passed/Failed/Ignored, thời gian thực thi, và tổng hợp kết quả.
* **Hỗ trợ đa định dạng thời gian**: Thời gian thực thi trong báo cáo có thể được hiển thị dưới nhiều định dạng khác nhau (giây, mili giây, hoặc giờ/phút/giây).
* **Hỗ trợ khởi động lại avd nếu bị crash khi chạy cts**: Tính năng này giúp đảm bảo AVD (Android Virtual Device) không bị tắt đột ngột, phục vụ cho các pipeline kiểm thử liên tục hoặc khi cần giữ emulator hoạt động sau khi CTS hoàn tất.
* **Log chi tiết**: Ghi lại các hoạt động và lỗi trong quá trình thực thi để dễ dàng gỡ lỗi và theo dõi.

## Cài đặt

Để cài đặt và chạy công cụ này, bạn cần có Python 3 và các thư viện cần thiết.

1.  **Clone repository:**

    ```bash
    git clone https://github.com/BaGiaXiTrum99/CTS_tool
    cd CTS_tool
    ```

2.  **Cài đặt các thư viện Python:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Cấu hình Android SDK và CTS Trade Federation:**
    Chú ý: Cấu hình này chỉ sử dụng khi cần tính năng tự động gen toàn bộ test modules từ DUT. Nếu không cần dùng thì có thể bỏ qua bước này
    Công cụ này cũng sử dụng `cts-tradefed` để liệt kê các module. Hãy đảm bảo cts-tradefed có thể hoạt động bình thường trong máy bạn. Bạn cần điều chỉnh đường dẫn đến `cts-tradefed` trong tệp `create_subplans_xml.py` nếu nó khác với mặc định.

    Ví dụ:
    ```python
    # Trong src/create_subplans_xml/create_subplans_xml.py
    cmd: str | list = "/home/ubuntu/Documents/Cienet/GAS_Cert/CTS/android-cts-14_r8-linux_x86-x86/android-cts/tools/cts-tradefed list modules"
    ```
    Thay đổi đường dẫn trên cho phù hợp với môi trường của bạn.

## Hướng dẫn sử dụng

Công cụ này được chạy thông qua dòng lệnh CLI với các tùy chọn khác nhau cho từng tính năng.

### 1\. Sinh file subplans XML

Tính năng này giúp bạn tạo ra các tệp XML chứa danh sách các module CTS cần chạy.

```bash
python3 main.py gen-subplan [tùy_chọn]
````

**Tùy chọn:**

  * `--module_list`: (Tùy chọn) Nếu được cung cấp, công cụ sẽ sử dụng danh sách module được định nghĩa sẵn trong `main.py`. Nếu không, nó sẽ tự động thu thập các module từ DUT.
  * `--folder_path`: (Tùy chọn) Đường dẫn đến thư mục để lưu các tệp subplan XML được tạo ra. Mặc định là `./subplans`.
  * `--file_num`: (Tùy chọn) Số lượng tệp subplan XML bạn muốn tạo ra. Các module sẽ được chia đều vào các tệp này. Mặc định là 1.

**Ví dụ:**

  * Sinh một tệp subplan với các module tự động thu thập và lưu vào thư mục mặc định:

    ```bash
    python3 main.py gen-subplan
    ```

  * Sinh 3 tệp subplan từ danh sách module đã định nghĩa và lưu vào thư mục `./my_custom_subplans`:

    ```bash
    python3 main.py gen-subplan --module_list True --file_num 3 --folder_path ./my_custom_subplans
    ```

### 2\. Phân tích kết quả và sinh báo cáo Excel

Tính năng này giúp bạn phân tích tệp `test_result.xml` và tạo báo cáo dưới dạng tệp Excel.

```bash
python3 main.py gen-report [tùy_chọn]
```

**Tùy chọn:**

  * `--path`: (Tùy chọn) Đường dẫn đến thư mục chứa tệp `test_result.xml`. Mặc định là `./data/2025.06.27_10.41.58.033_4484`.
  * `--time_unit`: (Tùy chọn) Đơn vị thời gian cho cột "Execution Time" trong báo cáo. Các lựa chọn: `ms` (mili giây), `s` (giây), `h/m/s` (giờ/phút/giây). Mặc định là `h/m/s`.
  * `--abi`: (Tùy chọn) Kiến trúc bộ xử lý của thiết bị (ví dụ: `x86_64`, `x86`). Mặc định là `x86_64`.
  * `--subplans_path`: (Tùy chọn) Đường dẫn đến tệp subplan XML đã được sử dụng để chạy CTS. Mặc định là `./subplans/myplan_1.xml`.

**Ví dụ:**

  * Tạo báo cáo Excel từ tệp kết quả mặc định, với thời gian hiển thị dưới dạng giờ/phút/giây:

    ```bash
    python3 main.py gen-report
    ```

  * Tạo báo cáo từ một thư mục kết quả cụ thể, với thời gian hiển thị dưới dạng mili giây và cho kiến trúc `x86_64`:

    ```bash
    python3 main.py gen-report --path ./my_test_results/latest --time_unit ms --abi x86_64
    ```

### 3\. Giữ AVD luôn hoạt động (Keep AVD Alive)

Tính năng này giúp bạn phân tích tệp `test_result.xml` và tạo báo cáo dưới dạng tệp Excel.

```bash
python3 main.py keep-alive-avd [tùy_chọn]
```

**Tùy chọn:**

  * `--name`: (Tùy chọn) Tên của AVD cần giữ cho hoạt động. Mặc định: `Automotive_1408p_landscape_with_Google_Play_1`.

  * `--emulator_path`: (Tùy chọn) Đường dẫn đầy đủ đến file emulator trong Android SDK. Mặc định: `/home/vmo/Android/Sdk/emulator/emulator`.

  * `--timeout`: (Tùy chọn) Thời gian chạy tối đa của tính năng này, tính bằng ngày. Sau khoảng thời gian này, công cụ sẽ tự dừng. Mặc định: `2` (tức 2 ngày).

**Chức năng:**

  * Theo dõi trạng thái emulator liên tục.
  * Tự động khởi động lại emulator nếu bị tắt.
  * Ghi log quá trình giám sát vào thư mục `logs/`.

**Ví dụ:**

    ```bash
    python3 main.py keep-avd-alive --name Pixel_6_API_34 --emulator_path /home/user/Android/Sdk/emulator/emulator --timeout 1

    ```

## Cấu trúc dự án

```
.
├── main.py                     # Điểm vào chính của ứng dụng, xử lý các đối số dòng lệnh và điều phối các tính năng.
├── README.md                   # Mô tả dự án
├── .gitignore                  # File không được push
├── requirements.txt            # Danh sách các thư viện python3 cần thiết.
├── src/
│   ├── avd_handler/
│   │   └── avd_handler.py      # Tự động giữ cho AVD luôn chạy, khởi động lại nếu bị crash.
│   ├── gen_report_excel/
│   │   ├── ResultXMLParser.py  # Xử lý tệp XML kết quả CTS và tạo báo cáo Excel.
│   │   ├── SubplansParser.py   # Phân tích tệp XML subplan để lấy danh sách module.
│   │   └── SummaryParser.py    # Phân tích tệp invocation_summary.txt để lấy thời gian thực thi module (hiện chưa được tích hợp đầy đủ).
│   └── create_subsplans_xml/
│       └── create_subplans_xml.py # Tạo các tệp XML subplan cho CTS.
├── utils/
│   ├── __init__.py
│   ├── constants.py            # Định nghĩa các hằng số (TimeUnit, ReportColumn) được sử dụng trong dự án.
│   ├── logger.py               # Cấu hình hệ thống ghi log.
│   ├── running_commands.py     # Cung cấp các hàm để thực thi các lệnh shell.
│   └── time_caculation.py      # Các hàm tiện ích để phân tích và định dạng thời gian.
├── script/
│   ├── open_emulator.sh        # Khởi động emulator ở 2 chế độ headless or normal (wipe data mỗi khi khởi chạy)
│   └── close_emulator.sh       # Ngắt PID của emulator   
├── data/                       # Nơi lưu trữ các kết quả CTS 
├── logs/                       # Log trong quá trình chạy 
├── subplans/                   # Nơi lưu trữ kết quả gen subplans
└── result/                     # Nơi chứa kết quả gen report excel
```

## Phát triển

  * Thêm các tính năng mới bằng cách tạo các module trong thư mục `src`.
  * Sử dụng `utils/logger.py` để ghi log trong các module của bạn.
  * Tuân thủ cấu trúc dự án hiện có để duy trì tính nhất quán.

## Đóng góp

Chào mừng mọi đóng góp\! Nếu bạn có bất kỳ đề xuất cải tiến hoặc phát hiện lỗi nào, vui lòng mở một "issue" hoặc gửi một "pull request".

```
```