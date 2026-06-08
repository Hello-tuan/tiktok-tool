# -*- coding: utf-8 -*-
# FILE: fix_version.py
# CHẠY 1 LẦN ĐỂ SỬA TẤT CẢ VERSION VỀ 1.1.0

import os
import re

print("Đang quét tất cả file .py trong thư mục hiện tại...")
print("=" * 50)

found_any = False
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'

for filename in os.listdir(current_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(current_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tìm dòng CURRENT_VERSION
            match = re.search(r'CURRENT_VERSION\s*=\s*"([^"]+)"', content)
            if match:
                old_version = match.group(1)
                print(f"  📄 File: {filename}")
                print(f"     Version cũ: {old_version}")
                
                if old_version != "1.1.0":
                    # Sửa thành 1.1.0
                    new_content = re.sub(
                        r'CURRENT_VERSION\s*=\s*"[^"]+"',
                        'CURRENT_VERSION = "1.1.0"',
                        content
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"     ✅ Đã sửa thành: 1.1.0")
                    found_any = True
                else:
                    print(f"     ✅ Đã đúng version")
        except Exception as e:
            print(f"  ❌ Lỗi đọc file {filename}: {e}")

if not found_any:
    print("\n⚠️  Không tìm thấy file nào cần sửa.")
    print("   Có thể bạn đang chạy nhầm file hoặc")
    print("   file tool không có dòng CURRENT_VERSION.")
else:
    print("\n✅ Đã sửa xong tất cả file!")

print("\nBây giờ chạy lại tool: python zefoy_full_auto.py")
input("\nNhấn Enter để thoát...")
