#!/bin/bash

# Lấy danh sách PID từ jobs -l (cột thứ 2)
PIDS=$(jobs -l | awk '{print $2}')

# Nếu không có tiến trình nền
if [ -z "$PIDS" ]; then
    echo "✅ Không có tiến trình nền nào đang chạy."
fi

echo "📋 Đang dừng các tiến trình nền sau:"
echo "$PIDS"

# Dừng tất cả PID đã lấy được
for pid in $PIDS; do
    echo "🛑 Dừng PID $pid..."
    kill "$pid"
done

echo "✅ Tất cả tiến trình nền đã được dừng."
read -rp "Nhấn Enter để thoát..."
