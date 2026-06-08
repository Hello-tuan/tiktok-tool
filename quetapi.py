# -*- coding: utf-8 -*-
# FILE: zefoy_api_catcher.py
# CHỈ BẮT API - KHÔNG LÀM GÌ KHÁC
# CHẠY: python zefoy_api_catcher.py

import time
import json
import os
import sys

# Cài selenium nếu chưa có
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except:
    os.system(f"{sys.executable} -m pip install selenium --quiet")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

# ====================================================
# MỞ CHROME + BẬT LOG PERFORMANCE
# ====================================================
print("Đang mở Chrome...")
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
options.add_argument("--window-size=500,900")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(options=options)

# ====================================================
# BẮT API
# ====================================================
def get_all_requests():
    """Lấy tất cả request từ performance log"""
    logs = driver.get_log("performance")
    requests = []
    
    for entry in logs:
        try:
            log_data = json.loads(entry["message"])
            message = log_data.get("message", {})
            method = message.get("method", "")
            
            if "Network.requestWillBeSent" in method:
                req = message.get("params", {}).get("request", {})
                requests.append({
                    "url": req.get("url", ""),
                    "method": req.get("method", ""),
                    "headers": req.get("headers", {}),
                    "postData": req.get("postData", ""),
                })
            
            if "Network.responseReceived" in method:
                resp = message.get("params", {}).get("response", {})
                requests.append({
                    "url": resp.get("url", ""),
                    "status": resp.get("status", 0),
                    "statusText": resp.get("statusText", ""),
                    "mimeType": resp.get("mimeType", ""),
                    "responseHeaders": resp.get("responseHeaders", {}),
                })
        except:
            pass
    
    return requests

# ====================================================
# VÀO ZEFOY
# ====================================================
print("Vào Zefoy...")
driver.get("https://zefoy.com")
time.sleep(4)

# Xóa log cũ
driver.get_log("performance")

print("\n========================================")
print("BROWSER ĐÃ MỞ - BẠN HÃY TỰ THAO TÁC:")
print("1. Nhập link TikTok vào ô")
print("2. Click nút gửi")
print("3. Đợi Zefoy xử lý xong")
print("========================================")
print("\nSau khi xong, nhấn ENTER để bắt API...")
input()

# ====================================================
# BẮT VÀ LƯU API
# ====================================================
print("Đang bắt API...")
all_requests = get_all_requests()

# Lọc chỉ request Zefoy
zefoy_requests = [r for r in all_requests if "zefoy" in r.get("url", "")]

# In ra
print(f"\n{'='*60}")
print(f"BẮT ĐƯỢC {len(zefoy_requests)} REQUEST ĐẾN ZEFOY")
print(f"{'='*60}\n")

for i, req in enumerate(zefoy_requests, 1):
    url = req.get("url", "")[:100]
    method = req.get("method", "")
    status = req.get("status", "")
    post = req.get("postData", "")[:200]
    
    print(f"{'─'*50}")
    print(f"#{i} {method} {status} {url}")
    if post:
        print(f"   PostData: {post}")

# Lưu file
with open("zefoy_api.json", "w", encoding="utf-8") as f:
    json.dump(zefoy_requests, f, indent=2, ensure_ascii=False)

print(f"\n✅ Đã lưu vào: zefoy_api.json")
print(f"\nGửi file này cho tôi để tôi tích hợp vào tool!")

driver.quit()
