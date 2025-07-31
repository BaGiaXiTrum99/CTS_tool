#!/bin/bash

echo "📋 Đang tìm và dừng tất cả tiến trình emulator Android đang chạy..."

# Lấy danh sách PID của tất cả emulator đang chạy (có thể là emulator hoặc qemu-system)
PIDS=$(pgrep -f "emulator.*-avd")

# Kiểm tra nếu không có PID nào
if [ -z "$PIDS" ]; then
    echo "✅ Không có emulator nào đang chạy."
else
    echo "📋 Các PID emulator sẽ bị dừng:"
    echo "$PIDS"

    # Dừng từng PID
    for pid in $PIDS; do
        echo "🛑 Đang dừng PID $pid..."
        kill "$pid"
    done

    echo "✅ Tất cả emulator đã được yêu cầu dừng."
fi

read -rp "Nhấn Enter để thoát..."
