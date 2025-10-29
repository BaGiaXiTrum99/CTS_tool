# CTS Automation Tool

Công cụ đa chức năng này được thiết kế để **tự động hóa quy trình chạy, giám sát và phân tích kết quả** của bộ kiểm thử **Android Compatibility Test Suite (CTS)**.  
Mục tiêu là giúp các kỹ sư kiểm thử và tích hợp dễ dàng sinh subplans, chạy lại test tự động (có retry, restart AVD), và xuất báo cáo Excel chi tiết.

---

## ⚙️ Tính năng chính

| Tính năng | Mô tả |
|------------|--------|
| **1. Tạo Subplans XML (`gen-subplan`)** | Tự động sinh các tệp XML chứa danh sách module CTS cần chạy. |
| **2. Sinh báo cáo Excel CTS (`gen-report`)** | Phân tích `test_result.xml` và tạo báo cáo Excel. |
| **3. Sinh báo cáo CTS Verifier (`gen-report-cts-v`)** | Xử lý kết quả CTS Verifier và sinh file Excel. |
| **4. Giữ AVD hoạt động liên tục (`keep-avd-alive`)** | Tự động restart AVD nếu bị crash hoặc tắt. |
| **5. Chạy CTS liên tục (`cts-runner`)** | Tự động chạy CTS với cơ chế retry thông minh. |
| **6. Sinh báo cáo từ nhiều kết quả (`multi-gen-report`)** | Hợp nhất nhiều folder kết quả CTS vào một báo cáo. |
| **7. Chạy CTS từ file CmdFile (`cts-runner-by-cmdfile`)** | Chạy tuần tự các lệnh CTS được định nghĩa trong file `cmdfile.txt`. |
| **8. Báo cáo chi tiết triage (`gen-report-triage`)** | Phân tích chi tiết các test case cần triage để debug lỗi. |

---

## 🧩 Cấu trúc thư mục dự án

```
CTS_tool/
├── main.py
├── requirements.txt
├── .env
├── README.md
├── src/
│   ├── avd_handler/
│   │   └── avd_handler.py
│   ├── cts_handler/
│   │   ├── cts_handler.py
│   │   └── cts_by_cmdfile_handler.py
│   ├── create_subsplans_xml/
│   │   └── create_subplans_xml.py
│   └── gen_report_excel/
│       ├── ResultXMLParser.py
│       ├── MultiResultXMLParser.py
│       ├── ResultXMLParser_CTS_V.py
│       └── ResultXMLTriageParser.py
├── utils/
│   ├── constants.py
│   ├── logging_setup.py
│   ├── StringHandler.py
│   └── time_caculation.py
├── data/
│   ├── cmdfile/
│   │   └── cmdfile.txt
│   └── results_CTS/
├── result/
│   ├── CTS/
│   ├── CTSV/
│   └── CTS_Triage/
├── subplans/
└── logs/
```

---

## 🧠 Cài đặt và cấu hình môi trường

### 1. Cài đặt Python và thư viện cần thiết

```bash
git clone https://github.com/BaGiaXiTrum99/CTS_tool
cd CTS_tool
pip install -r requirements.txt
```

### 2. Tạo file `.env`

Tạo file `.env` ở thư mục gốc để định nghĩa các giá trị mặc định tương tự như file `.env.example`

> ✅ Các giá trị trong `.env` có thể được **ghi đè bằng tham số CLI** khi chạy.

---

## 🚀 Hướng dẫn sử dụng chi tiết

Tất cả các tính năng đều được gọi qua CLI bằng cách:
```bash
python3 main.py <lệnh> [tùy chọn]
```

### 1️⃣ Sinh file Subplans XML

```bash
python3 main.py gen-subplan [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--use-default-module-list` | Dùng danh sách module mặc định trong `main.py` | `False` |
| `--folder_path` | Nơi lưu file subplan | `./subplans` |
| `--file_num` | Số lượng file subplan được tạo | `1` |

**Ví dụ:**
```bash
python3 main.py gen-subplan --use-default-module-list --file_num 3
```

---

### 2️⃣ Sinh báo cáo Excel CTS

```bash
python3 main.py gen-report [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--path` | Đường dẫn tới folder chứa `test_result.xml` | `./data/2025.07.10_08.36.27.870_3983` |
| `--time_unit` | Đơn vị thời gian hiển thị (`ms`, `s`, `h/m/s`) | `h/m/s` |
| `--subplans_path` | Đường dẫn tới subplan XML (nếu cần đối chiếu) | `None` |
| `--output_dir` | Folder lưu báo cáo Excel | `./result/CTS` |

**Ví dụ:**
```bash
python3 main.py gen-report --path ./data/latest_run --time_unit s
```

---

### 3️⃣ Sinh báo cáo CTS Verifier

```bash
python3 main.py gen-report-cts-v [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--path` | Thư mục chứa kết quả CTS Verifier | `./data/CTS_V` |
| `--time_unit` | Đơn vị thời gian (`ms`, `s`, `h/m/s`) | `h/m/s` |
| `--output_dir` | Folder lưu báo cáo Excel | `./result/CTSV` |

**Ví dụ:**
```bash
python3 main.py gen-report-cts-v --path ./data/cts_verifier_results
```

---

### 4️⃣ Giữ AVD luôn hoạt động

```bash
python3 main.py keep-avd-alive [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--name` | Tên AVD | `Automotive_1408p_landscape_with_Google_Play_1` |
| `--emulator_path` | Đường dẫn emulator | `/home/<user>/Android/Sdk/emulator/emulator` |
| `--timeout` | Thời gian chạy (ngày) | `2` |
| `--is_headless` | Chạy không hiển thị UI | Theo `.env` |
| `--restart_avd` | Tự restart khi crash | Theo `.env` |

**Ví dụ:**
```bash
python3 main.py keep-avd-alive --name Pixel_6_API_34 --timeout 1
```

---

### 5️⃣ Chạy CTS tự động liên tục

```bash
python3 main.py cts-runner [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--android_cts_path` | Đường dẫn tới `android-cts` | Theo `.env` |
| `--cmd` | Lệnh chạy CTS | Theo `.env` |
| `--retry_time` | Số lần retry (không tính lần đầu) | `5` |
| `--retry_type` | Kiểu retry (`DEFAULT`, `FAILED`, `NOT_EXECUTED`) | `DEFAULT` |
| `--device_type` | Kiểu thiết bị (`AVD`, `DUT`) | `AVD` |
| `--is_headless` | Chạy headless | Theo `.env` |
| `--restart` | Restart môi trường sau mỗi vòng | Theo `.env` |

**Ví dụ:**
```bash
python3 main.py cts-runner --cmd "run cts -m CtsMediaTestCases"
```

---

### 6️⃣ Sinh báo cáo từ nhiều kết quả CTS (number of modules must be the same)

```bash
python3 main.py multi-gen-report [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--path` | Thư mục chứa nhiều folder kết quả CTS | `./data/results_CTS` |
| `--time_unit` | Đơn vị thời gian (`ms`, `s`, `h/m/s`) | `h/m/s` |
| `--output_dir` | Folder lưu báo cáo Excel | `./result/CTS` |

**Ví dụ:**
```bash
python3 main.py multi-gen-report --path ./data/all_results
```

---

### 7️⃣ Chạy CTS từ file CmdFile.txt

```bash
python3 main.py cts-runner-by-cmdfile [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--android_cts_path` | Đường dẫn tới CTS | Theo `.env` |
| `--cmd_file_path` | Đường dẫn tới `cmdfile.txt` | `./data/cmdfile/cmdfile.txt` |
| `--device_type` | Thiết bị (`AVD`, `DUT`) | `AVD` |
| `--restart` | Restart giữa các run | Theo `.env` |

**Ví dụ:**
```bash
python3 main.py cts-runner-by-cmdfile --cmd_file_path ./data/cmdfile/mylist.txt
```

---

### 8️⃣ Sinh báo cáo CTS Triage

```bash
python3 main.py gen-report-triage [tùy chọn]
```

**Tùy chọn:**
| Tham số | Mô tả | Mặc định |
|----------|--------|-----------|
| `--path` | Thư mục chứa các folder kết quả CTS | `./data/results_CTS_Triage` |
| `--time_unit` | Đơn vị thời gian (`ms`, `s`, `h/m/s`) | `h/m/s` |
| `--output_dir` | Folder lưu báo cáo Excel | `./result/CTS_Triage` |

---

## 🪵 Logging

Cấu hình log được định nghĩa trong `utils/logging_setup.py`.  
Theo mặc định, log được in ra console và lưu vào `logs/` với định dạng thời gian, cấp độ, và tên module.

Ví dụ dòng log:
```
2025-10-28 13:45:12,913 - cts_logger.main - INFO - Running Feature Generate Report CTS with args: ...
```

---

## 🧰 Phát triển và mở rộng

- Thêm chức năng mới bằng cách tạo module trong `src/`.
- Dùng `configure_logger()` trong `utils/logging_setup.py` để ghi log.
- Mọi feature mới nên được thêm vào `main.py` qua `subparsers.add_parser()`.

---

## 🤝 Đóng góp

1. Fork repo.  
2. Tạo branch mới (`feature/...` hoặc `fix/...`).  
3. Commit theo chuẩn:  
   ```bash
   git commit -m "[fix] đồng bộ lệnh keep-avd-alive với README"
   ```  
4. Gửi pull request mô tả chi tiết thay đổi.

---

## 📜 Giấy phép

Dự án tuân theo giấy phép **Apache 2.0** của Google CTS.

---

**Tác giả:** Ngo Viet Trung
**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 2025-10-29  