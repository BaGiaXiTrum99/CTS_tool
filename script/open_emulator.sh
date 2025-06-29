#!/bin/bash
# Tên AVD – bạn có thể đổi thành AVD bạn dùng
AVD_NAME="Automotive_1408p_landscape_with_Google_Play"


# Kiểm tra AVD có tồn tại không
if ! $HOME/Android/Sdk/emulator/emulator -list-avds | grep -Fxq "$AVD_NAME"; then
    echo "❌ Không tìm thấy AVD tên: $AVD_NAME"
    echo "📋 Danh sách AVD hiện có:"
    $HOME/Android/Sdk/emulator/emulator -list-avds
fi

# Giá trị mặc định: chạy không giao diện
USE_NO_WINDOW="true"

# Nếu có truyền argument, dùng nó để ghi đè
if [ ! -z "$1" ]; then
    USE_NO_WINDOW="$1"
    echo 1
fi

# Khởi động emulator ở chế độ headless (ẩn giao diện, tắt GPU, tắt âm thanh & animation)
if [ "$USE_NO_WINDOW" == "true" ]; then 
	echo "🚀 Đang khởi động AVD: $AVD_NAME ở chế độ headless..."
	$HOME/Android/Sdk/emulator/emulator -avd "$AVD_NAME" \
	  -no-window \
	  -wipe-data \
	  -gpu off \
	  -no-audio \
	  -no-boot-anim \
	  -no-snapshot \
	  -read-only &
else
	$HOME/Android/Sdk/emulator/emulator -avd "$AVD_NAME" -wipe-data
fi


