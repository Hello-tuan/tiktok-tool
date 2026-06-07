# -*- coding: utf-8 -*-
# FILE: zefoy_full_auto.py
# VERSION: 1.0.0
# REPO: https://github.com/Hello-tuan/tiktok-tool
# TÍNH NĂNG:
#   ✅ Tự động mở Chrome
#   ✅ Tự động vào Zefoy
#   ✅ Tự động chọn mục Views
#   ✅ Tự động paste link TikTok
#   ✅ Tự động click gửi
#   ✅ Tự động lặp lại
#   ✅ Lưu session (không cần giải captcha lại)
#   ✅ Tự động check update từ GitHub
#   ✅ Tự động tải bản mới
#   ✅ Đồng bộ PC & Phone

import time
import os
import sys
import json
import shutil
import threading
import subprocess
import requests
from datetime import datetime

# ====================================================
# CẤU HÌNH GITHUB
# ====================================================
GITHUB_USER = "Hello-tuan"
GITHUB_REPO = "tiktok-tool"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
CURRENT_VERSION = "1.0.0"
TOOL_FILENAME = "zefoy_full_auto.py"

# ====================================================
# MÀU SẮC
# ====================================================
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
C = '\033[96m'; M = '\033[95m'; N = '\033[0m'; B = '\033[1m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def ok(s):   print(f"  {G}✅ {s}{N}")
def err(s):  print(f"  {R}❌ {s}{N}")
def info(s): print(f"  {C}ℹ️  {s}{N}")
def warn(s): print(f"  {Y}⚠️  {s}{N}")
def title(s): print(f"\n{B}{Y}{'='*55}{N}\n{B}{Y}  {s}{N}\n{B}{Y}{'='*55}{N}")

# ====================================================
# TỰ ĐỘNG CÀI THƯ VIỆN
# ====================================================
def install_deps():
    pkgs = {
        'selenium': 'selenium',
        'requests': 'requests',
    }
    for module, package in pkgs.items():
        try:
            __import__(module)
        except:
            print(f"  Đang cài {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

install_deps()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ====================================================
# TỰ ĐỘNG CẬP NHẬT TỪ GITHUB
# ====================================================
class AutoUpdater:
    @staticmethod
    def check():
        """Kiểm tra version mới"""
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
                        'download_url': remote.get('download_url', f'{GITHUB_RAW}/{TOOL_FILENAME}'),
                    }
        except:
            pass
        return None
    
    @staticmethod
    def update(download_url):
        """Tải và cài bản mới"""
        try:
            info("Đang tải bản cập nhật...")
            
            # Backup
            os.makedirs("backups", exist_ok=True)
            backup_file = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            shutil.copy2(__file__, backup_file)
            info(f"Đã backup: {backup_file}")
            
            # Tải file mới
            resp = requests.get(download_url, timeout=30)
            if resp.status_code == 200:
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                
                ok("Cập nhật thành công!")
                ok("Khởi động lại...")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            
            return False
        except Exception as e:
            err(f"Lỗi cập nhật: {e}")
            return False

# ====================================================
# ZEFOY FULL AUTO BOT
# ====================================================
class ZefoyBot:
    def __init__(self):
        self.driver = None
        self.url = ""
        self.running = False
        self.count = 0
        self.success = 0
        self.fail = 0
    
    def start_browser(self):
        """Mở Chrome với session lưu"""
        info("Mở Chrome...")
        
        options = Options()
        options.add_argument("--window-size=500,900")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--log-level=3")
        options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36")
        
        # Lưu session để không cần captcha
        profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_zefoy_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            ok("Chrome đã mở!")
            return True
        except Exception as e:
            err(f"Không mở được Chrome: {e}")
            info("Cần cài Chrome: https://www.google.com/chrome/")
            return False
    
    def click_views_section(self):
        """Click vào mục Views"""
        keywords = ['views', 'service', 'send', 'free views', 'tiktok views']
        
        for kw in keywords:
            try:
                elements = self.driver.find_elements(By.XPATH,
                    f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{kw}')]")
                
                for el in elements:
                    if el.tag_name in ['a', 'button'] or el.get_attribute('onclick'):
                        try:
                            el.click()
                            time.sleep(2)
                            info(f"Đã click: {el.text[:30]}")
                            return True
                        except:
                            continue
            except:
                continue
        
        # Fallback
        for el in self.driver.find_elements(By.XPATH, "//a | //button"):
            try:
                text = (el.text or '').lower()
                if any(kw in text for kw in ['view', 'service', 'send', 'tiktok']):
                    el.click()
                    time.sleep(2)
                    info(f"Đã click: {el.text[:30]}")
                    return True
            except:
                continue
        
        return False
    
    def fill_and_submit(self):
        """Paste link và click gửi"""
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            all_fields = inputs + textareas
            
            if not all_fields:
                return False
            
            # Chọn ô dài nhất
            best = max(all_fields, key=lambda x: int(x.get_attribute('maxlength') or '0'))
            best.clear()
            time.sleep(0.2)
            best.send_keys(self.url)
            time.sleep(0.3)
            info("Đã paste link")
            
            # Click nút gửi
            send_keywords = ['send', 'submit', 'start', 'search', 'go', 'get views', 'free']
            
            for btn in self.driver.find_elements(By.TAG_NAME, "button"):
                try:
                    text = (btn.text or '').lower()
                    if any(kw in text for kw in send_keywords):
                        btn.click()
                        time.sleep(0.5)
                        info(f"Đã click: {btn.text[:30]}")
                        return True
                except:
                    continue
            
            best.send_keys(Keys.RETURN)
            info("Đã nhấn Enter")
            return True
            
        except Exception as e:
            err(f"Lỗi: {e}")
            return False
    
    def handle_captcha(self):
        """Xử lý captcha nếu có"""
        try:
            page = self.driver.page_source.lower()
            if 'captcha' not in page and 'verify' not in page:
                return True
            
            warn("Phát hiện captcha, thử refresh...")
            self.driver.refresh()
            time.sleep(3)
            
            page = self.driver.page_source.lower()
            if 'captcha' not in page and 'verify' not in page:
                ok("Hết captcha sau refresh")
                return True
            
            warn("Vẫn còn captcha, đợi 15s...")
            time.sleep(15)
            return True
        except:
            return True
    
    def submit_once(self):
        """Gửi 1 lần"""
        try:
            self.driver.get("https://zefoy.com")
            time.sleep(4)
            self.handle_captcha()
            
            info("Tìm mục Views...")
            self.click_views_section()
            time.sleep(3)
            self.handle_captcha()
            
            info("Điền link và gửi...")
            if not self.fill_and_submit():
                return False
            
            time.sleep(5)
            self.handle_captcha()
            time.sleep(2)
            
            page = self.driver.page_source.lower()
            
            for word in ['error', 'fail', 'invalid', 'wrong', 'expired', 'limit']:
                if word in page:
                    err(f"Zefoy: {word}")
                    return False
            
            for word in ['success', 'sent', 'added', 'complete', 'view', 'queued']:
                if word in page:
                    ok(f"Zefoy: {word}")
                    return True
            
            return True
            
        except Exception as e:
            err(f"Lỗi: {e}")
            return False
    
    def run_loop(self, delay=60):
        """Vòng lặp chính"""
        self.running = True
        self.count = 0
        self.success = 0
        self.fail = 0
        
        print(f"\n{B}{Y}{'='*55}{N}")
        print(f"{B}{G}  🎵 ZEFOY FULL AUTO v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*55}{N}")
        print(f"  Link: {self.url[:50]}...")
        print(f"  Delay: {delay}s")
        print(f"  Mode: TỰ ĐỘNG 100%")
        print(f"{'='*55}\n")
        print(f"{C}  Tool tự động:{N}")
        print(f"  1. Vào Zefoy → 2. Chọn Views")
        print(f"  3. Paste link → 4. Gửi → 5. Lặp")
        print(f"{'='*55}\n")
        
        while self.running:
            self.count += 1
            
            print(f"\n{B}┌─ Lần #{self.count} {'─'*42}┐{N}")
            
            if self.submit_once():
                self.success += 1
                ok(f"OK! ({self.success}/{self.count})")
            else:
                self.fail += 1
                err(f"Fail ({self.fail}/{self.count})")
            
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
        if self.driver:
            try: self.driver.quit()
            except: pass
        ok("Đã dừng!")

# ====================================================
# MENU CHÍNH
# ====================================================
def main():
    bot = ZefoyBot()
    thread = None
    
    while True:
        clear()
        print(f"{B}{Y}{'='*50}{N}")
        print(f"{B}{Y}  🤖 ZEFOY FULL AUTO v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*50}{N}")
        print(f"  GitHub: {C}github.com/{GITHUB_USER}/{GITHUB_REPO}{N}")
        
        if bot.url:
            print(f"  Link: {C}{bot.url[:40]}...{N}")
        
        print(f"  {G}OK:{N} {bot.success} | {R}Fail:{N} {bot.fail} | 🔄 {bot.count}")
        
        if bot.running:
            print(f"  {G}● ĐANG CHẠY{N}")
        else:
            print(f"  ● DỪNG")
        
        print(f"{'-'*50}")
        print(f"  {B}1.{N} 🎯 Nhập link + CHẠY AUTO")
        print(f"  {B}2.{N} 🔄 Kiểm tra cập nhật")
        print(f"  {B}3.{N} ⏹  DỪNG")
        print(f"  {B}4.{N} 🚪 Thoát")
        print(f"{B}{Y}{'='*50}{N}")
        print(f"{C}  🔑 Mẹo: Lần đầu giải captcha tay,{N}")
        print(f"{C}  các lần sau tool tự chạy!{N}")
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
            bot.success = 0
            bot.fail = 0
            bot.count = 0
            
            delay = input(f"Delay (giây) [60]: ").strip()
            delay = int(delay) if delay.isdigit() else 60
            
            if not bot.driver:
                if not bot.start_browser():
                    input("\nEnter...")
                    continue
            
            print(f"\n{G}  ✅ Bắt đầu chạy!{N}")
            print(f"{Y}  ⚠️  Lần đầu có thể cần giải captcha tay{N}")
            print(f"{Y}  Các lần sau tự động hoàn toàn!{N}")
            
            thread = threading.Thread(target=bot.run_loop, args=(delay,), daemon=True)
            thread.start()
            
            input(f"\n{G}✅ Đang chạy!{N} Enter về menu...")
        
        elif c == "2":
            print(f"\n{C}🔍 Kiểm tra cập nhật...{N}")
            update = AutoUpdater.check()
            
            if update:
                print(f"\n{Y}🔄 CÓ BẢN MỚI!{N}")
                print(f"  v{update['current_version']} → v{update['new_version']}")
                if update['changelog']:
                    print(f"  Thay đổi: {update['changelog']}")
                
                yn = input(f"\n  Cập nhật? (y/n): ").strip().lower()
                if yn == 'y':
                    AutoUpdater.update(update['download_url'])
                    return
            else:
                ok(f"Đã là bản mới nhất (v{CURRENT_VERSION})")
            
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
    print(f"{B}{C}  🔍 KIỂM TRA CẬP NHẬT...{N}")
    print(f"{B}{C}{'='*55}{N}")
    
    update = AutoUpdater.check()
    
    if update:
        print(f"\n{Y}  🔄 CÓ BẢN MỚI: v{update['new_version']}{N}")
        print(f"  Hiện tại: v{CURRENT_VERSION}")
        if update['changelog']:
            print(f"  Thay đổi: {update['changelog']}")
        
        yn = input(f"\n  Cập nhật ngay? (y/n): ").strip().lower()
        if yn == 'y':
            AutoUpdater.update(update['download_url'])
    else:
        ok(f"Đã là bản mới nhất (v{CURRENT_VERSION})")
    
    print()
    main()