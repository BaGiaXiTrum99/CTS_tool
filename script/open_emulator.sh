#!/bin/bash
AVD_PREFIX="Automotive_1408p_landscape_with_Google_Play"

# Giá trị mặc định
USE_NO_WINDOW="true"
SHARD=1

# Nhận tham số nếu truyền vào
if [ ! -z "$1" ]; then
    USE_NO_WINDOW="$1"
fi

if [ ! -z "$2" ]; then
    SHARD="$2"
fi

echo "🔧 Tham số cấu hình:"
echo "   👉 Headless mode (USE_NO_WINDOW): $USE_NO_WINDOW"
echo "   👉 Số shard (emulator): $SHARD"

# Kiểm tra trước các AVD có tồn tại không
for i in $(seq 1 "$SHARD"); do
    AVD_NAME="${AVD_PREFIX}_${i}"
    if ! $HOME/Android/Sdk/emulator/emulator -list-avds | grep -Fxq "$AVD_NAME"; then
        echo "❌ Không tìm thấy AVD tên: $AVD_NAME"
        echo "📋 Danh sách AVD hiện có:"
        $HOME/Android/Sdk/emulator/emulator -list-avds
        pause
    fi
done

# Vòng lặp khởi động emulator
for i in $(seq 1 "$SHARD"); do
    AVD_NAME="${AVD_PREFIX}_${i}"
    
    if [ "$USE_NO_WINDOW" == "true" ]; then 
        echo "🚀 [Shard $i] Đang khởi động AVD: $AVD_NAME ở chế độ headless..."
        $HOME/Android/Sdk/emulator/emulator -avd "$AVD_NAME" \
            -no-window \
            -gpu host \
            -wipe-data \
            -no-snapshot &
    else
        echo "🚀 [Shard $i] Đang khởi động AVD: $AVD_NAME với giao diện..."
        $HOME/Android/Sdk/emulator/emulator -avd "$AVD_NAME" -noaudio \
            -gpu host \
            -wipe-data \
            -no-snapshot &
    fi
done

wait
echo "✅ Khởi động tất cả $SHARD emulator hoàn tất."