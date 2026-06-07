# -*- coding: utf-8 -*-
# FILE: zefoy_full_auto.py
# VERSION: 1.1.0
# REPO: https://github.com/Hello-tuan/tiktok-tool
# TÍNH NĂNG MỚI:
#   ✅ Quét UI để tìm và click chính xác
#   ✅ Không cài lại ChromeDriver nếu đã có
#   ✅ Tự nhận diện giao diện Zefoy thay đổi
#   ✅ Tự động cập nhật từ GitHub

import time
import os
import sys
import json
import shutil
import threading
import subprocess
import requests
import re
from datetime import datetime

# ====================================================
# CẤU HÌNH GITHUB
# ====================================================
GITHUB_USER = "Hello-tuan"
GITHUB_REPO = "tiktok-tool"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
CURRENT_VERSION = "1.1.0"
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

# ====================================================
# TỰ ĐỘNG CÀI THƯ VIỆN (CHỈ KHI THIẾU)
# ====================================================
def install_deps():
    """Chỉ cài thư viện nếu chưa có, không đụng ChromeDriver"""
    pkgs = {
        'selenium': 'selenium',
        'requests': 'requests',
    }
    
    need_install = False
    for module, package in pkgs.items():
        try:
            __import__(module)
        except:
            if not need_install:
                print(f"  {C}⏳ Đang kiểm tra thư viện...{N}")
                need_install = True
            print(f"  {Y}  Cài {package}...{N}")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "--quiet"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    
    if not need_install:
        print(f"  {G}✅ Thư viện đầy đủ{N}")

install_deps()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ====================================================
# QUÉT UI - TỰ ĐỘNG NHẬN DIỆN GIAO DIỆN
# ====================================================
class UIScanner:
    """Quét và phân tích giao diện Zefoy"""
    
    @staticmethod
    def find_clickable_by_text(driver, texts, element_types=None):
        """Tìm element có thể click dựa trên text"""
        if element_types is None:
            element_types = ['button', 'a', 'div', 'span', 'input', '*']
        
        for text in texts:
            for el_type in element_types:
                try:
                    # Tìm bằng text chứa
                    xpath = f"//{el_type}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            return el
                except:
                    continue
                
                try:
                    # Tìm bằng value/placeholder
                    xpath = f"//{el_type}[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            return el
                except:
                    continue
                
                try:
                    # Tìm bằng aria-label
                    xpath = f"//{el_type}[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            return el
                except:
                    continue
        
        return None
    
    @staticmethod
    def find_input_field(driver):
        """Tìm ô nhập URL (ô to nhất)"""
        inputs = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        all_fields = inputs + textareas
        
        if not all_fields:
            return None
        
        # Lọc các field hiển thị
        visible_fields = [f for f in all_fields if f.is_displayed()]
        
        if not visible_fields:
            return None
        
        # Ưu tiên field có placeholder chứa từ khóa URL
        url_keywords = ['url', 'link', 'tiktok', 'video', 'http', 'www', 'paste', 'dán']
        for field in visible_fields:
            try:
                placeholder = (field.get_attribute('placeholder') or '').lower()
                name = (field.get_attribute('name') or '').lower()
                aria = (field.get_attribute('aria-label') or '').lower()
                
                combined = placeholder + name + aria
                if any(kw in combined for kw in url_keywords):
                    return field
            except:
                continue
        
        # Fallback: chọn field có maxlength lớn nhất
        try:
            return max(visible_fields, key=lambda x: int(x.get_attribute('maxlength') or '0'))
        except:
            return visible_fields[0] if visible_fields else None
    
    @staticmethod
    def find_submit_button(driver):
        """Tìm nút gửi"""
        keywords = [
            'send', 'submit', 'start', 'views', 'get', 'free', 
            'search', 'go', 'gửi', 'bắt đầu', 'tăng', 'nhận',
            'confirm', 'ok', 'next', 'continue', 'run'
        ]
        
        # Tìm button
        btn = UIScanner.find_clickable_by_text(driver, keywords, ['button', 'input'])
        if btn:
            return btn
        
        # Tìm link/div có thể click
        btn = UIScanner.find_clickable_by_text(driver, keywords, ['a', 'div', 'span'])
        if btn:
            return btn
        
        # Tìm bất kỳ element nào có class chứa 'btn' hoặc 'submit'
        try:
            xpath = "//*[contains(@class, 'btn') or contains(@class, 'submit') or contains(@class, 'send')]"
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    return el
        except:
            pass
        
        return None
    
    @staticmethod
    def scan_page_structure(driver):
        """Quét toàn bộ cấu trúc trang để debug"""
        try:
            info = {
                'title': driver.title,
                'url': driver.current_url,
                'buttons': [],
                'inputs': [],
                'links': [],
            }
            
            # Quét buttons
            for btn in driver.find_elements(By.TAG_NAME, "button")[:10]:
                try:
                    if btn.is_displayed():
                        info['buttons'].append({
                            'text': (btn.text or '')[:50],
                            'class': (btn.get_attribute('class') or '')[:50],
                            'id': (btn.get_attribute('id') or '')[:30],
                        })
                except:
                    pass
            
            # Quét inputs
            for inp in driver.find_elements(By.TAG_NAME, "input")[:10]:
                try:
                    if inp.is_displayed():
                        info['inputs'].append({
                            'placeholder': (inp.get_attribute('placeholder') or '')[:50],
                            'name': (inp.get_attribute('name') or '')[:30],
                            'type': (inp.get_attribute('type') or '')[:20],
                        })
                except:
                    pass
            
            # Quét links
            for link in driver.find_elements(By.TAG_NAME, "a")[:10]:
                try:
                    if link.is_displayed():
                        info['links'].append({
                            'text': (link.text or '')[:50],
                            'href': (link.get_attribute('href') or '')[:80],
                        })
                except:
                    pass
            
            return info
        except:
            return None

# ====================================================
# TỰ ĐỘNG CẬP NHẬT TỪ GITHUB
# ====================================================
class AutoUpdater:
    @staticmethod
    def check():
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
        try:
            info("Đang tải bản cập nhật...")
            
            os.makedirs("backups", exist_ok=True)
            backup_file = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            shutil.copy2(__file__, backup_file)
            info(f"Đã backup: {backup_file}")
            
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
        self.ui_scanner = UIScanner()
    
    def check_chromedriver(self):
        """Kiểm tra ChromeDriver đã có chưa"""
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1,1")
            options.add_argument("--log-level=3")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            driver = webdriver.Chrome(options=options)
            driver.quit()
            return True
        except:
            return False
    
    def start_browser(self):
        """Mở Chrome - không cài lại ChromeDriver nếu đã có"""
        if self.check_chromedriver():
            ok("ChromeDriver đã có, bỏ qua cài đặt")
        else:
            info("ChromeDriver chưa có, đang cài...")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                Service(ChromeDriverManager().install())
            except:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager", "--quiet"])
                from webdriver_manager.chrome import ChromeDriverManager
                Service(ChromeDriverManager().install())
        
        options = Options()
        options.add_argument("--window-size=500,900")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--log-level=3")
        options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36")
        
        # Lưu session
        profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_zefoy_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            ok("Chrome đã mở!")
            return True
        except Exception as e:
            err(f"Không mở được Chrome: {e}")
            return False
    
    def smart_click_views(self):
        """Tìm và click mục Views bằng UI Scanner"""
        info("Quét UI tìm mục Views...")
        
        # Quét cấu trúc trang
        structure = UIScanner.scan_page_structure(self.driver)
        if structure:
            info(f"Tiêu đề trang: {structure['title'][:50]}")
            info(f"Tìm thấy {len(structure['buttons'])} buttons, {len(structure['inputs'])} inputs")
        
        # Danh sách từ khóa mở rộng
        views_keywords = [
            'views', 'view', 'service', 'services', 'send views',
            'free views', 'tiktok views', 'video views',
            'increase views', 'get views', 'buy views',
            'lượt xem', 'tăng view', 'buff view',
            'start', 'get started', 'begin',
        ]
        
        # Thử tìm và click
        element = UIScanner.find_clickable_by_text(self.driver, views_keywords)
        
        if element:
            try:
                text = (element.text or element.get_attribute('value') or '')[:40]
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(2)
                ok(f"Đã click: {text}")
                return True
            except:
                pass
        
        # Fallback: thử click vào link/button đầu tiên
        try:
            clickables = self.driver.find_elements(By.XPATH, 
                "//a[@href] | //button | //*[@onclick] | //*[@role='button']")
            
            for el in clickables[:20]:
                try:
                    if el.is_displayed():
                        text = (el.text or '').lower()
                        if any(kw in text for kw in ['view', 'service', 'start', 'send', 'tiktok']):
                            self.driver.execute_script("arguments[0].click();", el)
                            time.sleep(2)
                            ok(f"Đã click: {el.text[:30]}")
                            return True
                except:
                    continue
        except:
            pass
        
        warn("Không tìm thấy mục Views, thử tiếp tục...")
        return True  # Vẫn tiếp tục
    
    def smart_fill_and_submit(self):
        """Điền link và gửi bằng UI Scanner"""
        # Tìm ô input
        info("Quét UI tìm ô nhập URL...")
        input_field = UIScanner.find_input_field(self.driver)
        
        if not input_field:
            err("Không tìm thấy ô nhập!")
            return False
        
        # Điền link
        try:
            input_field.clear()
            time.sleep(0.2)
            input_field.send_keys(self.url)
            time.sleep(0.3)
            ok("Đã paste link")
        except:
            err("Không thể paste link")
            return False
        
        # Tìm nút gửi
        info("Quét UI tìm nút gửi...")
        submit_btn = UIScanner.find_submit_button(self.driver)
        
        if submit_btn:
            try:
                text = (submit_btn.text or submit_btn.get_attribute('value') or '')[:30]
                self.driver.execute_script("arguments[0].click();", submit_btn)
                time.sleep(0.5)
                ok(f"Đã click: {text}")
                return True
            except:
                pass
        
        # Fallback: Enter
        try:
            input_field.send_keys(Keys.RETURN)
            ok("Đã nhấn Enter")
            return True
        except:
            pass
        
        err("Không tìm thấy nút gửi!")
        return False
    
    def submit_once(self):
        """Gửi 1 lần với UI Scanner"""
        try:
            # Vào Zefoy
            self.driver.get("https://zefoy.com")
            time.sleep(4)
            
            # Kiểm tra captcha
            page = self.driver.page_source.lower()
            if 'captcha' in page:
                warn("Có captcha, thử refresh...")
                self.driver.refresh()
                time.sleep(3)
            
            # Click Views
            self.smart_click_views()
            time.sleep(3)
            
            # Điền và gửi
            if not self.smart_fill_and_submit():
                return False
            
            time.sleep(5)
            
            # Kiểm tra kết quả
            page = self.driver.page_source.lower()
            
            fail_words = ['error', 'fail', 'invalid', 'wrong', 'expired', 'limit']
            success_words = ['success', 'sent', 'added', 'complete', 'view', 'queued']
            
            for word in fail_words:
                if word in page:
                    err(f"Zefoy: {word}")
                    return False
            
            for word in success_words:
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
        print(f"  UI Scanner: {G}ACTIVE{N}")
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
        print(f"  UI Scanner: {G}✅{N} | ChromeDriver: {G}{'✅' if bot.check_chromedriver() else '❌'}{N}")
        
        if bot.url:
            print(f"  Link: {C}{bot.url[:40]}...{N}")
        
        print(f"  {G}OK:{N} {bot.success} | {R}Fail:{N} {bot.fail} | 🔄 {bot.count}")
        print(f"  {'● ĐANG CHẠY' if bot.running else '● DỪNG'}")
        
        print(f"{'-'*50}")
        print(f"  {B}1.{N} 🎯 Nhập link + CHẠY AUTO")
        print(f"  {B}2.{N} 🔍 Quét UI (debug)")
        print(f"  {B}3.{N} 🔄 Kiểm tra cập nhật")
        print(f"  {B}4.{N} ⏹  DỪNG")
        print(f"  {B}5.{N} 🚪 Thoát")
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
            
            thread = threading.Thread(target=bot.run_loop, args=(delay,), daemon=True)
            thread.start()
            
            input(f"\n{G}✅ Đang chạy!{N} Enter về menu...")
        
        elif c == "2":
            if not bot.driver:
                if not bot.start_browser():
                    input("\nEnter...")
                    continue
            
            bot.driver.get("https://zefoy.com")
            time.sleep(4)
            
            info("Đang quét UI...")
            structure = UIScanner.scan_page_structure(bot.driver)
            
            if structure:
                print(f"\n{C}  📊 CẤU TRÚC TRANG ZEFOY:{N}")
                print(f"  Title: {structure['title']}")
                print(f"  URL: {structure['url'][:60]}")
                print(f"\n  {G}Buttons ({len(structure['buttons'])}):{N}")
                for b in structure['buttons']:
                    print(f"    - [{b.get('text', '')}]")
                print(f"\n  {C}Inputs ({len(structure['inputs'])}):{N}")
                for i in structure['inputs']:
                    print(f"    - [{i.get('placeholder', '')}]")
                print(f"\n  {Y}Links ({len(structure['links'])}):{N}")
                for l in structure['links']:
                    print(f"    - [{l.get('text', '')}] -> {l.get('href', '')[:50]}")
            
            input("\nEnter...")
        
        elif c == "3":
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
        
        elif c == "4":
            bot.stop()
            input("\nEnter...")
        
        elif c == "5":
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