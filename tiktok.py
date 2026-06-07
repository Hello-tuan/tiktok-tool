# -*- coding: utf-8 -*-
# FILE: tiktok_tool.py
# REPO: https://github.com/Hello-tuan/tiktok-tool
# TỰ ĐỘNG CẬP NHẬT TỪ GITHUB -> ĐỒNG BỘ PC & PHONE

import time
import threading
import random
import re
import io
import base64
import os
import sys
import json
import hashlib
import requests
import shutil
from datetime import datetime

# ====================================================
# THÔNG TIN GITHUB CỦA BẠN
# ====================================================
GITHUB_USER = "Hello-tuan"
GITHUB_REPO = "tiktok-tool"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# ====================================================
# MÀU SẮC
# ====================================================
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
C = '\033[96m'; N = '\033[0m'; B = '\033[1m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def ok(s):   print(f"  {G}✅ {s}{N}")
def err(s):  print(f"  {R}❌ {s}{N}")
def info(s): print(f"  {C}ℹ️  {s}{N}")
def warn(s): print(f"  {Y}⚠️  {s}{N}")

# ====================================================
# PHÁT HIỆN THIẾT BỊ
# ====================================================
def get_device_id():
    try:
        if os.name == 'nt':
            return hashlib.md5(os.environ.get('COMPUTERNAME', 'PC').encode()).hexdigest()[:8]
        else:
            import socket
            return hashlib.md5(socket.gethostname().encode()).hexdigest()[:8]
    except:
        return hashlib.md5(str(random.random()).encode()).hexdigest()[:8]

DEVICE_ID = get_device_id()
DEVICE_TYPE = "PC" if os.name == 'nt' else "Phone"
CURRENT_VERSION = "1.0.0"

# ====================================================
# CÀI THƯ VIỆN TỰ ĐỘNG
# ====================================================
def install_deps():
    pkgs = {
        'selenium': 'selenium',
        'PIL': 'Pillow',
        'pytesseract': 'pytesseract',
        'requests': 'requests',
    }
    for module, package in pkgs.items():
        try:
            __import__(module)
        except:
            print(f"  Đang cài {package}...")
            os.system(f"{sys.executable} -m pip install {package} --quiet 2>/dev/null")

install_deps()
import warnings
warnings.filterwarnings('ignore')

# ====================================================
# TỰ ĐỘNG CẬP NHẬT
# ====================================================
class Updater:
    @staticmethod
    def check():
        """Kiểm tra version mới từ GitHub"""
        try:
            resp = requests.get(f"{GITHUB_RAW}/version.json", timeout=10)
            if resp.status_code == 200:
                remote = resp.json()
                remote_ver = remote.get('version', '0.0.0')
                
                if remote_ver > CURRENT_VERSION:
                    return {
                        'new_version': remote_ver,
                        'current_version': CURRENT_VERSION,
                        'changelog': remote.get('changelog', ''),
                        'file_url': f"{GITHUB_RAW}/tiktok_tool.py",
                    }
        except:
            pass
        return None
    
    @staticmethod
    def update(file_url):
        """Tải bản mới từ GitHub"""
        try:
            info("Đang tải bản cập nhật...")
            
            # Backup
            os.makedirs("backups", exist_ok=True)
            backup_name = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            if os.path.exists(__file__):
                shutil.copy2(__file__, backup_name)
            
            # Tải file mới
            resp = requests.get(file_url, timeout=30)
            if resp.status_code == 200:
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                ok("Cập nhật thành công!")
                ok("Khởi động lại...")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return True
            
            return False
        except Exception as e:
            err(f"Lỗi: {e}")
            return False

# ====================================================
# GỬI ZEFOY
# ====================================================
def send_to_zefoy(tiktok_url):
    """Gửi link TikTok lên Zefoy"""
    try:
        sess = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        resp = sess.get("https://zefoy.com", headers=headers, timeout=10)
        
        action = re.search(r'action=["\']([^"\']+)["\']', resp.text)
        token = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', resp.text)
        
        if not action or not token:
            return False, "Không tìm thấy form Zefoy"
        
        action_url = action.group(1)
        if not action_url.startswith('http'):
            action_url = f"https://zefoy.com/{action_url.lstrip('/')}"
        
        data = {"_token": token.group(1), "url": tiktok_url}
        resp2 = sess.post(action_url, data=data, headers=headers, timeout=15)
        
        if 'error' in resp2.text.lower():
            return False, "Zefoy báo lỗi"
        
        return True, "OK"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Không kết nối được Zefoy"
    except Exception as e:
        return False, str(e)[:30]

# ====================================================
# GỬI VIEW TRỰC TIẾP (FALLBACK)
# ====================================================
def send_direct_view(video_id, count=50):
    """Gửi view trực tiếp qua TikTok API"""
    ok_count = 0
    
    for _ in range(count):
        try:
            did = str(random.randint(10**18, 10**19-1))
            iid = str(random.randint(10**10, 10**11-1))
            
            r = requests.get(
                "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/detail/",
                params={
                    "aweme_id": video_id, "device_id": did, "install_id": iid,
                    "aid": "1233", "app_name": "musical_ly", "channel": "googleplay",
                    "device_platform": "android", "os_version": str(random.randint(12,15)),
                    "version_code": "320503", "language": "en",
                    "region": random.choice(["US","VN","ID"]),
                    "ts": str(int(time.time()*1000))
                },
                headers={"User-Agent": f"com.zhiliaoapp.musically/2023205030"},
                timeout=5
            )
            
            if r.status_code == 200:
                ok_count += 1
                
            time.sleep(random.uniform(0.01, 0.05))
        except:
            pass
    
    return ok_count

def get_video_id(url):
    """Lấy video ID từ link"""
    m = re.search(r'/video/(\d+)', url)
    if m: return m.group(1)
    
    if any(s in url for s in ['vm.tiktok.com', 'vt.tiktok.com', 'tiktok.com/t/']):
        try:
            r = requests.head(url, allow_redirects=True, timeout=10,
                headers={"User-Agent": "Mozilla/5.0"})
            m = re.search(r'/video/(\d+)', r.url)
            if m: return m.group(1)
        except: pass
    
    return ""

# ====================================================
# MENU CHÍNH
# ====================================================
def main():
    clear()
    print(f"{B}{Y}{'='*50}{N}")
    print(f"{B}{Y}  🎵 TIKTOK TOOL{N}")
    print(f"{B}{Y}{'='*50}{N}")
    print(f"  Thiết bị: {C}{DEVICE_TYPE}{N} ({DEVICE_ID})")
    print(f"  Version: {C}v{CURRENT_VERSION}{N}")
    print(f"  Repo: {C}github.com/{GITHUB_USER}/{GITHUB_REPO}{N}")
    print(f"{'='*50}")
    
    # Kiểm tra cập nhật
    print(f"\n{C}  🔍 Kiểm tra cập nhật...{N}")
    update_info = Updater.check()
    
    if update_info:
        print(f"\n{Y}  🔄 CÓ PHIÊN BẢN MỚI!{N}")
        print(f"  v{update_info['current_version']} → v{update_info['new_version']}")
        if update_info['changelog']:
            print(f"  Thay đổi: {update_info['changelog']}")
        
        yn = input(f"\n  Cập nhật? (y/n): ").strip().lower()
        if yn == 'y':
            Updater.update(update_info['file_url'])
            return
    else:
        ok(f"Đã là bản mới nhất (v{CURRENT_VERSION})")
    
    print(f"\n{B}{Y}{'='*50}{N}")
    print(f"  {B}1.{N} 🎯 Nhập link TikTok → Gửi Zefoy + Direct")
    print(f"  {B}2.{N} 🔄 Chạy liên tục (loop)")
    print(f"  {B}3.{N} 🔍 Kiểm tra cập nhật")
    print(f"  {B}4.{N} 🚪 Thoát")
    print(f"{B}{Y}{'='*50}{N}")
    
    c = input(f"\n> ").strip()
    
    if c == "1":
        url = input(f"\n{Y}Dán link TikTok:{N} ").strip()
        
        if "tiktok.com" not in url:
            err("Link không hợp lệ!")
            input("\nEnter...")
            main()
            return
        
        vid = get_video_id(url)
        print(f"\n  Video ID: {vid or 'Không tìm thấy'}")
        
        # 1. Gửi Zefoy
        print(f"\n{C}  Gửi Zefoy...{N}")
        success, msg = send_to_zefoy(url)
        if success:
            ok(f"Zefoy: {msg}")
        else:
            warn(f"Zefoy: {msg}")
        
        # 2. Gửi direct nếu có video ID
        if vid:
            views = input(f"\n  Gửi thêm bao nhiêu view trực tiếp? [50]: ").strip()
            views = int(views) if views.isdigit() else 50
            
            print(f"{C}  Đang gửi {views} views trực tiếp...{N}")
            sent = send_direct_view(vid, views)
            ok(f"Đã gửi: {sent}/{views} views")
        
        input("\nEnter để về menu...")
        main()
    
    elif c == "2":
        url = input(f"\n{Y}Dán link TikTok:{N} ").strip()
        
        if "tiktok.com" not in url:
            err("Link không hợp lệ!")
            input("\nEnter...")
            main()
            return
        
        delay = input(f"Delay mỗi lần (giây) [60]: ").strip()
        delay = int(delay) if delay.isdigit() else 60
        
        vid = get_video_id(url)
        
        count = 0
        print(f"\n{B}Đang chạy... (Ctrl+C để dừng){N}\n")
        
        try:
            while True:
                count += 1
                print(f"{B}┌─ Lần #{count}{N}")
                
                # Zefoy
                success, msg = send_to_zefoy(url)
                if success:
                    ok(f"Zefoy OK")
                else:
                    warn(f"Zefoy: {msg}")
                
                # Direct views
                if vid:
                    sent = send_direct_view(vid, 30)
                    ok(f"Direct: {sent} views")
                
                print(f"{B}└{'─'*40}┘{N}")
                
                # Đếm ngược
                for i in range(delay, 0, -1):
                    pct = (delay - i + 1) / delay * 100
                    bar_len = 25
                    filled = int(bar_len * (delay - i + 1) / delay)
                    bar = f"{C}{'█' * filled}{N}{'░' * (bar_len - filled)}"
                    print(f"\r  ⏳ [{bar}] {i}s ({pct:.0f}%)", end='', flush=True)
                    time.sleep(1)
                print("\n")
                
        except KeyboardInterrupt:
            print(f"\n{Y}  Đã dừng!{N}")
    
    elif c == "3":
        print(f"\n{C}  Đang kiểm tra...{N}")
        update_info = Updater.check()
        if update_info:
            print(f"{Y}  Có bản mới: v{update_info['new_version']}{N}")
        else:
            ok(f"Đã là bản mới nhất!")
        input("\nEnter...")
        main()
    
    elif c == "4":
        print(f"\n{Y}👋 Tạm biệt!{N}")
        sys.exit(0)
    else:
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}👋 Tạm biệt!{N}")
        sys.exit(0)