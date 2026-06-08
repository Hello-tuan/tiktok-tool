# -*- coding: utf-8 -*-
# FILE: zefoy_full_auto.py
# VERSION: 1.1.0
# REPO: https://github.com/Hello-tuan/tiktok-tool
# TÍNH NĂNG: QUÉT UI THÔNG MINH - TỰ NHẬN DIỆN GIAO DIỆN ZEFOY

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
# CÀI THƯ VIỆN
# ====================================================
def install_deps():
    pkgs = {'selenium': 'selenium', 'requests': 'requests'}
    for module, package in pkgs.items():
        try:
            __import__(module)
        except:
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ====================================================
# QUÉT UI THÔNG MINH - TỰ NHẬN DIỆN GIAO DIỆN
# ====================================================
class SmartUIScanner:
    """Quét và tự động nhận diện mọi thành phần trên trang Zefoy"""
    
    @staticmethod
    def analyze_page(driver):
        """Phân tích toàn bộ trang, trả về cấu trúc"""
        result = {
            'url': driver.current_url,
            'title': driver.title,
            'clickable_elements': [],
            'input_fields': [],
            'forms': [],
        }
        
        try:
            # Quét tất cả elements có thể tương tác
            all_elements = driver.find_elements(By.XPATH, 
                "//a | //button | //input | //textarea | //select | //*[@onclick] | //*[@role='button']")
            
            for el in all_elements:
                try:
                    if not el.is_displayed():
                        continue
                    
                    tag = el.tag_name.lower()
                    text = (el.text or '').strip()
                    placeholder = (el.get_attribute('placeholder') or '').strip()
                    name = (el.get_attribute('name') or '').strip()
                    id_attr = (el.get_attribute('id') or '').strip()
                    class_attr = (el.get_attribute('class') or '').strip()
                    value = (el.get_attribute('value') or '').strip()
                    href = (el.get_attribute('href') or '').strip()
                    onclick = (el.get_attribute('onclick') or '').strip()
                    aria_label = (el.get_attribute('aria-label') or '').strip()
                    element_type = (el.get_attribute('type') or '').strip()
                    
                    # Gom tất cả text có thể
                    all_text = f"{text} {placeholder} {name} {value} {aria_label} {element_type}".lower()
                    
                    element_info = {
                        'element': el,
                        'tag': tag,
                        'text': text,
                        'placeholder': placeholder,
                        'name': name,
                        'id': id_attr,
                        'class': class_attr,
                        'value': value,
                        'href': href,
                        'onclick': onclick,
                        'aria_label': aria_label,
                        'type': element_type,
                        'all_text': all_text,
                    }
                    
                    if tag in ['input', 'textarea']:
                        result['input_fields'].append(element_info)
                    else:
                        result['clickable_elements'].append(element_info)
                        
                except:
                    continue
            
        except Exception as e:
            pass
        
        return result
    
    @staticmethod
    def find_best_match(elements, keywords, min_score=1):
        """Tìm element khớp nhất với keywords"""
        best_match = None
        best_score = 0
        
        for el_info in elements:
            score = 0
            all_text = el_info['all_text']
            
            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in all_text:
                    score += 1
                # Khớp chính xác hơn
                if kw_lower in el_info.get('text', '').lower():
                    score += 2
                if kw_lower in el_info.get('placeholder', '').lower():
                    score += 2
                if kw_lower in el_info.get('aria_label', '').lower():
                    score += 2
            
            if score > best_score:
                best_score = score
                best_match = el_info
        
        if best_score >= min_score:
            return best_match['element'], best_score
        return None, 0
    
    @staticmethod
    def find_views_section(driver):
        """Tìm và click mục Views"""
        info("🔍 Quét UI tìm mục Views...")
        
        analysis = SmartUIScanner.analyze_page(driver)
        
        # Từ khóa cho mục Views
        views_keywords = [
            'views', 'view', 'service', 'services', 
            'send views', 'free views', 'tiktok views',
            'video views', 'increase views', 'get views',
            'lượt xem', 'tăng view', 'buff view',
            'start', 'get started', 'begin',
        ]
        
        element, score = SmartUIScanner.find_best_match(
            analysis['clickable_elements'], views_keywords, min_score=2
        )
        
        if element:
            try:
                text = (element.text or element.get_attribute('value') or '')[:40]
                driver.execute_script("arguments[0].click();", element)
                ok(f"Đã click: {text} (score: {score})")
                return True
            except:
                pass
        
        # Fallback: click phần tử đầu tiên có thể click
        if analysis['clickable_elements']:
            try:
                first = analysis['clickable_elements'][0]['element']
                driver.execute_script("arguments[0].click();", first)
                ok(f"Đã click phần tử đầu tiên: {analysis['clickable_elements'][0]['text'][:30]}")
                return True
            except:
                pass
        
        return False
    
    @staticmethod
    def find_url_input(driver):
        """Tìm ô nhập URL"""
        info("🔍 Quét UI tìm ô nhập URL...")
        
        analysis = SmartUIScanner.analyze_page(driver)
        
        # Từ khóa cho ô URL
        url_keywords = [
            'url', 'link', 'tiktok', 'video', 'http', 'www',
            'paste', 'dán', 'nhập', 'enter', 'input',
            'video url', 'tiktok url', 'video link',
        ]
        
        element, score = SmartUIScanner.find_best_match(
            analysis['input_fields'], url_keywords, min_score=1
        )
        
        if element:
            ok(f"Tìm thấy ô URL (score: {score})")
            return element
        
        # Fallback: tìm ô input hiển thị đầu tiên
        for field_info in analysis['input_fields']:
            try:
                el = field_info['element']
                if el.is_displayed() and el.is_enabled():
                    ok(f"Dùng ô input: {field_info['placeholder'][:30]}")
                    return el
            except:
                continue
        
        return None
    
    @staticmethod
    def find_submit_button(driver):
        """Tìm nút gửi"""
        info("🔍 Quét UI tìm nút gửi...")
        
        analysis = SmartUIScanner.analyze_page(driver)
        
        # Từ khóa cho nút gửi
        submit_keywords = [
            'send', 'submit', 'start', 'views', 'get', 'free',
            'search', 'go', 'gửi', 'bắt đầu', 'tăng', 'nhận',
            'confirm', 'ok', 'next', 'continue', 'run',
            'send views', 'get views', 'free views',
        ]
        
        element, score = SmartUIScanner.find_best_match(
            analysis['clickable_elements'], submit_keywords, min_score=2
        )
        
        if element:
            try:
                text = (element.text or element.get_attribute('value') or '')[:40]
                driver.execute_script("arguments[0].click();", element)
                ok(f"Đã click: {text} (score: {score})")
                return True
            except:
                pass
        
        return False
    
    @staticmethod
    def print_page_analysis(driver):
        """In ra phân tích trang để debug"""
        analysis = SmartUIScanner.analyze_page(driver)
        
        print(f"\n{C}{'='*50}{N}")
        print(f"{C}  📊 PHÂN TÍCH TRANG ZEFOY{N}")
        print(f"{C}{'='*50}{N}")
        print(f"  URL: {analysis['url'][:60]}")
        print(f"  Title: {analysis['title'][:50]}")
        
        print(f"\n  {G}📝 Input fields ({len(analysis['input_fields'])}):{N}")
        for i, field in enumerate(analysis['input_fields'][:8], 1):
            print(f"    {i}. [{field['tag']}] placeholder='{field['placeholder'][:40]}' name='{field['name'][:20]}'")
        
        print(f"\n  {Y}🔘 Clickable elements ({len(analysis['clickable_elements'])}):{N}")
        for i, el in enumerate(analysis['clickable_elements'][:10], 1):
            print(f"    {i}. [{el['tag']}] text='{el['text'][:40]}' href='{el['href'][:40]}'")
        
        print(f"{C}{'='*50}{N}")

# ====================================================
# TỰ ĐỘNG CẬP NHẬT
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
            
            resp = requests.get(download_url, timeout=30)
            if resp.status_code == 200:
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                ok("Cập nhật thành công! Khởi động lại...")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            return False
        except Exception as e:
            err(f"Lỗi: {e}")
            return False

# ====================================================
# ZEFOY BOT VỚI UI SCANNER
# ====================================================
class ZefoyBot:
    def __init__(self):
        self.driver = None
        self.url = ""
        self.running = False
        self.count = 0
        self.success = 0
        self.fail = 0
        self.scanner = SmartUIScanner()
    
    def start_browser(self):
        """Mở Chrome"""
        options = Options()
        options.add_argument("--window-size=500,900")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--log-level=3")
        options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36")
        
        profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_zefoy_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            ok("Chrome đã mở!")
            return True
        except:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                ok("Chrome đã mở!")
                return True
            except Exception as e:
                err(f"Không mở được Chrome: {e}")
                return False
    
    def submit_once(self):
        """Gửi 1 lần với UI Scanner"""
        try:
            # 1. Vào Zefoy
            self.driver.get("https://zefoy.com")
            time.sleep(4)
            
            # 2. Click Views section
            self.scanner.find_views_section(self.driver)
            time.sleep(3)
            
            # 3. Tìm ô URL và điền
            url_input = self.scanner.find_url_input(self.driver)
            if not url_input:
                # In phân tích trang để debug
                self.scanner.print_page_analysis(self.driver)
                err("Không tìm thấy ô nhập URL!")
                return False
            
            url_input.clear()
            time.sleep(0.2)
            url_input.send_keys(self.url)
            time.sleep(0.3)
            ok("Đã paste link")
            
            # 4. Tìm và click nút gửi
            if not self.scanner.find_submit_button(self.driver):
                # Fallback: nhấn Enter
                try:
                    url_input.send_keys(Keys.RETURN)
                    ok("Đã nhấn Enter")
                except:
                    err("Không tìm thấy nút gửi!")
                    return False
            
            time.sleep(5)
            
            # 5. Kiểm tra kết quả
            page = self.driver.page_source.lower()
            
            fail_words = ['error', 'fail', 'invalid', 'wrong', 'expired', 'limit']
            success_words = ['success', 'sent', 'added', 'complete', 'view', 'queued']
            
            for word in fail_words:
                if word in page:
                    err(f"Zefoy báo: {word}")
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
        print(f"{B}{G}  🎵 ZEFOY SMART AUTO v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*55}{N}")
        print(f"  Link: {self.url[:50]}...")
        print(f"  Delay: {delay}s")
        print(f"  Mode: QUÉT UI THÔNG MINH")
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

# ====================================================
# MENU
# ====================================================
def main():
    bot = ZefoyBot()
    thread = None
    
    while True:
        clear()
        print(f"{B}{Y}{'='*50}{N}")
        print(f"{B}{Y}  🤖 ZEFOY SMART AUTO v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*50}{N}")
        
        if bot.url:
            print(f"  Link: {C}{bot.url[:40]}...{N}")
        
        print(f"  {G}OK:{N} {bot.success} | {R}Fail:{N} {bot.fail} | 🔄 {bot.count}")
        print(f"  {'● ĐANG CHẠY' if bot.running else '● DỪNG'}")
        
        print(f"{'-'*50}")
        print(f"  {B}1.{N} 🎯 Nhập link + CHẠY AUTO")
        print(f"  {B}2.{N} 🔍 Phân tích UI (debug)")
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
            bot.success = 0; bot.fail = 0; bot.count = 0
            
            delay = input(f"Delay (giây) [60]: ").strip()
            delay = int(delay) if delay.isdigit() else 60
            
            if not bot.driver:
                if not bot.start_browser():
                    input("\nEnter...")
                    continue
            
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
            bot.scanner.print_page_analysis(bot.driver)
            input("\nEnter...")
        
        elif c == "3":
            print(f"\n{C}🔍 Kiểm tra cập nhật...{N}")
            update = AutoUpdater.check()
            
            if update:
                print(f"\n{Y}🔄 CÓ BẢN MỚI!{N}")
                print(f"  v{update['current_version']} → v{update['new_version']}")
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

if __name__ == "__main__":
    clear()
    update = AutoUpdater.check()
    if update:
        print(f"\n{Y}🔄 Có bản mới: v{update['new_version']}{N}")
        yn = input(f"Cập nhật? (y/n): ").strip().lower()
        if yn == 'y':
            AutoUpdater.update(update['download_url'])
    main()