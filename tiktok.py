# -*- coding: utf-8 -*-
# FILE: zefoy_api_direct.py
# VERSION: 1.2.0
# REPO: https://github.com/Hello-tuan/tiktok-tool
# TỰ ĐỘNG TĂNG VERSION +0.1.0 MỖI LẦN UPDATE

import time
import threading
import random
import re
import os
import sys
import json
import shutil
import requests
from datetime import datetime
from urllib.parse import urljoin

# ====================================================
# CẤU HÌNH GITHUB
# ====================================================
GITHUB_USER = "Hello-tuan"
GITHUB_REPO = "tiktok-tool"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
CURRENT_VERSION = "1.2.0"
TOOL_FILENAME = "zefoy_api_direct.py"

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
# TỰ ĐỘNG CẬP NHẬT + TỰ TĂNG VERSION +0.1.0
# ====================================================
class AutoUpdater:
    @staticmethod
    def parse_version(ver_str):
        """Chuyển version string thành tuple số"""
        try:
            return tuple(map(int, ver_str.split('.')))
        except:
            return (0, 0, 0)
    
    @staticmethod
    def version_to_str(ver_tuple):
        """Chuyển tuple thành string"""
        return '.'.join(map(str, ver_tuple))
    
    @staticmethod
    def bump_version(ver_str):
        """Tự động tăng version lên 0.1.0"""
        v = AutoUpdater.parse_version(ver_str)
        new_v = (v[0], v[1] + 1, 0)  # Tăng minor, reset patch về 0
        return AutoUpdater.version_to_str(new_v)
    
    @staticmethod
    def check():
        """Kiểm tra version mới từ GitHub"""
        try:
            resp = requests.get(f"{GITHUB_RAW}/version.json", timeout=10)
            if resp.status_code == 200:
                remote = resp.json()
                remote_ver = remote.get('version', '0.0.0')
                
                if AutoUpdater.parse_version(remote_ver) > AutoUpdater.parse_version(CURRENT_VERSION):
                    return {
                        'new_version': remote_ver,
                        'current_version': CURRENT_VERSION,
                        'changelog': remote.get('changelog', ''),
                        'download_url': remote.get('download_url', f'{GITHUB_RAW}/{TOOL_FILENAME}'),
                    }
        except:
            pass
        return None
    
    @staticmethod
    def update_and_bump(download_url, new_version):
        """Tải bản mới và tự động tăng version trong file"""
        try:
            info(f"Đang tải bản {new_version}...")
            
            # Backup
            os.makedirs("backups", exist_ok=True)
            backup_file = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            shutil.copy2(__file__, backup_file)
            info(f"Đã backup: {backup_file}")
            
            # Tải file mới
            resp = requests.get(download_url, timeout=30)
            if resp.status_code == 200:
                new_content = resp.text
                
                # Tự động tăng version trong file mới (+0.1.0)
                next_version = AutoUpdater.bump_version(new_version)
                
                # Sửa CURRENT_VERSION trong file mới
                new_content = re.sub(
                    r'CURRENT_VERSION\s*=\s*"[^"]+"',
                    f'CURRENT_VERSION = "{next_version}"',
                    new_content
                )
                
                # Ghi file
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                ok(f"Cập nhật xong! v{new_version} → v{next_version}")
                ok(f"Lần sau sẽ tự tăng lên v{AutoUpdater.bump_version(next_version)}")
                ok("Khởi động lại...")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            
            return False
        except Exception as e:
            err(f"Lỗi cập nhật: {e}")
            return False

# ====================================================
# ZEFOY API DIRECT
# ====================================================
class ZefoyAPI:
    """Gửi trực tiếp request đến Zefoy"""
    
    ZEFOY_URLS = [
        "https://zefoy.com",
        "https://zefoy.app",
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    
    def connect(self):
        """Kết nối đến Zefoy"""
        for url in self.ZEFOY_URLS:
            try:
                resp = self.session.get(url, headers=self.headers, timeout=10)
                if resp.status_code == 200:
                    self.base_url = url
                    ok(f"Kết nối: {url}")
                    return True
            except:
                continue
        return False
    
    def get_page(self, path=""):
        """Lấy trang và parse form"""
        try:
            url = urljoin(self.base_url, path) if path else self.base_url
            resp = self.session.get(url, headers=self.headers, timeout=15)
            html = resp.text
            
            # Tìm CSRF token
            csrf = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', html)
            token = csrf.group(1) if csrf else ""
            
            # Tìm tất cả form
            forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>(.*?)</form>', html, re.DOTALL)
            
            # Tìm links
            links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
            
            return {
                'html': html,
                'token': token,
                'forms': forms,
                'links': [(urljoin(self.base_url, l[0]), re.sub(r'<[^>]+>', '', l[1]).strip()) for l in links],
            }
        except:
            return None
    
    def find_and_click_views(self):
        """Tìm link Views và click"""
        info("Tìm mục Views...")
        
        page = self.get_page()
        if not page:
            return None
        
        keywords = ['view', 'service', 'send', 'tiktok', 'free']
        
        for url, text in page['links']:
            if any(kw in text.lower() for kw in keywords):
                ok(f"Click: {text[:30]}")
                return self.get_page(url)
        
        # Fallback: dùng trang chủ
        return page
    
    def submit_tiktok_url(self, tiktok_url):
        """Gửi link TikTok"""
        info("Đang gửi link...")
        
        # Lấy trang views
        page = self.find_and_click_views()
        if not page:
            return False, "Không lấy được trang"
        
        # Tìm form
        form_data = {'_token': page['token']}
        
        # Tìm key cho URL
        url_keys = ['url', 'video_url', 'link', 'tiktok_url', 'page_url', 'input']
        url_key = 'url'
        
        for key in url_keys:
            if key in page['html'].lower():
                url_key = key
                break
        
        form_data[url_key] = tiktok_url
        
        # Tìm form action
        action = self.base_url
        for form_action, _ in page['forms']:
            if form_action:
                action = urljoin(self.base_url, form_action)
                break
        
        # Gửi
        try:
            resp = self.session.post(action, data=form_data, headers=self.headers, timeout=15)
            
            if resp.status_code == 200:
                if 'error' in resp.text.lower():
                    return False, "Zefoy báo lỗi"
                if any(w in resp.text.lower() for w in ['success', 'sent', 'added']):
                    return True, "OK"
                return True, "Đã gửi"
            return False, f"HTTP {resp.status_code}"
        except Exception as e:
            return False, str(e)[:30]

# ====================================================
# BOT CHÍNH
# ====================================================
class ZefoyBot:
    def __init__(self):
        self.api = ZefoyAPI()
        self.url = ""
        self.running = False
        self.count = 0
        self.success = 0
        self.fail = 0
    
    def submit_once(self):
        """Gửi 1 lần"""
        ok_flag, msg = self.api.submit_tiktok_url(self.url)
        
        if ok_flag:
            ok(msg)
        else:
            err(msg)
        
        return ok_flag
    
    def run_loop(self, delay=60):
        """Vòng lặp"""
        self.running = True
        self.count = 0
        self.success = 0
        self.fail = 0
        
        if not self.api.connect():
            err("Không kết nối được Zefoy!")
            return
        
        print(f"\n{B}{Y}{'='*55}{N}")
        print(f"{B}{G}  🎵 ZEFOY API DIRECT v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*55}{N}")
        print(f"  Link: {self.url[:50]}...")
        print(f"  Delay: {delay}s")
        print(f"  Mode: API DIRECT (không Chrome)")
        print(f"{'='*55}\n")
        
        while self.running:
            self.count += 1
            
            print(f"\n{B}┌─ Lần #{self.count} {'─'*42}┐{N}")
            
            if self.submit_once():
                self.success += 1
            else:
                self.fail += 1
            
            print(f"│ 📊 OK:{G}{self.success}{N} | Fail:{R}{self.fail}{N}")
            print(f"{B}└{'─'*48}┘{N}")
            
            # Đếm ngược
            print(f"\n{C}  ⏳ Đợi {delay}s...{N}")
            for i in range(delay, 0, -1):
                if not self.running: break
                pct = (delay - i + 1) / delay * 100
                bar_len = 30
                filled = int(bar_len * (delay - i + 1) / delay)
                bar = f"{G}{'█' * filled}{N}{'░' * (bar_len - filled)}"
                print(f"\r  [{bar}] {i}s ({pct:.0f}%)", end='', flush=True)
                time.sleep(1)
            print("\n")
    
    def stop(self):
        self.running = False

# ====================================================
# MENU
# ====================================================
def main():
    bot = ZefoyBot()
    thread = None
    
    while True:
        clear()
        print(f"{B}{Y}{'='*50}{N}")
        print(f"{B}{Y}  🤖 ZEFOY DIRECT v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*50}{N}")
        
        if bot.url:
            print(f"  Link: {C}{bot.url[:40]}...{N}")
        
        print(f"  {G}OK:{N} {bot.success} | {R}Fail:{N} {bot.fail} | 🔄 {bot.count}")
        print(f"  {'● RUNNING' if bot.running else '● STOPPED'}")
        print(f"  Auto bump: +0.1.0 mỗi update")
        
        print(f"{'-'*50}")
        print(f"  {B}1.{N} 🎯 Nhập link + CHẠY")
        print(f"  {B}2.{N} 🔄 Kiểm tra update")
        print(f"  {B}3.{N} ⏹  DỪNG")
        print(f"  {B}4.{N} 🚪 Thoát")
        print(f"{B}{Y}{'='*50}{N}")
        
        c = input(f"\n> ").strip()
        
        if c == "1":
            print(f"\n{Y}Dán link TikTok:{N}")
            url = input("> ").strip()
            
            if not url or "tiktok.com" not in url:
                err("Link không hợp lệ!")
                input("\nEnter...")
                continue
            
            bot.url = url
            bot.success = 0; bot.fail = 0; bot.count = 0
            
            delay = input(f"Delay (giây) [60]: ").strip()
            delay = int(delay) if delay.isdigit() else 60
            
            thread = threading.Thread(target=bot.run_loop, args=(delay,), daemon=True)
            thread.start()
            
            input(f"\n{G}✅ Đang chạy!{N} Enter về menu...")
        
        elif c == "2":
            print(f"\n{C}Kiểm tra update...{N}")
            update = AutoUpdater.check()
            
            if update:
                print(f"\n{Y}🔄 CÓ BẢN MỚI!{N}")
                print(f"  v{update['current_version']} → v{update['new_version']}")
                print(f"  Sau update: v{AutoUpdater.bump_version(update['new_version'])}")
                
                yn = input(f"\n  Cập nhật? (y/n): ").strip().lower()
                if yn == 'y':
                    AutoUpdater.update_and_bump(update['download_url'], update['new_version'])
                    return
            else:
                ok(f"Đã là bản mới nhất (v{CURRENT_VERSION})")
                next_ver = AutoUpdater.bump_version(CURRENT_VERSION)
                info(f"Bản tiếp theo sẽ là: v{next_ver}")
            
            input("\nEnter...")
        
        elif c == "3":
            bot.stop()
            input("\nEnter...")
        
        elif c == "4":
            bot.stop()
            print(f"\n{Y}👋 Tạm biệt!{N}")
            sys.exit(0)

# ====================================================
# KHỞI ĐỘNG
# ====================================================
if __name__ == "__main__":
    clear()
    print(f"\n{B}{C}{'='*55}{N}")
    print(f"{B}{C}  🔍 KIỂM TRA UPDATE...{N}")
    print(f"{B}{C}{'='*55}{N}")
    
    update = AutoUpdater.check()
    
    if update:
        print(f"\n{Y}  Có bản mới: v{update['new_version']}{N}")
        yn = input(f"  Update? (y/n): ").strip().lower()
        if yn == 'y':
            AutoUpdater.update_and_bump(update['download_url'], update['new_version'])
    else:
        ok(f"Đã là bản mới nhất (v{CURRENT_VERSION})")
        next_ver = AutoUpdater.bump_version(CURRENT_VERSION)
        info(f"Bản sau update sẽ là: v{next_ver}")
    
    print()
    main()
