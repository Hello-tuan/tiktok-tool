# -*- coding: utf-8 -*-
# FILE: zefoy_pc_full_auto.py
# PHIÊN BẢN: TÍCH HỢP TẤT CẢ - CHROMIUM + TESSERACT + TỰ ĐỘNG CÀI ĐẶT
# CHỈ CẦN CHẠY FILE NÀY - MỌI THỨ TỰ ĐỘNG

import subprocess
import sys
import os
import time
import threading
import random
import re
import io
import base64
import zipfile
import tarfile
import requests
import json
import shutil
import stat
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ====================================================
# TỰ ĐỘNG CÀI ĐẶT TẤT CẢ
# ====================================================
def setup_environment():
    """Tự động cài đặt mọi thứ cần thiết"""
    print("\033[1;36m  ⏳ ĐANG KIỂM TRA & CÀI ĐẶT MÔI TRƯỜNG...\033[0m")
    print("=" * 55)
    
    # 1. Cài thư viện Python
    required_packages = {
        'selenium': 'selenium',
        'PIL': 'Pillow',
        'pytesseract': 'pytesseract',
        'requests': 'requests',
        'webdriver_manager': 'webdriver-manager',
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  \033[92m✅ {package}\033[0m")
        except ImportError:
            print(f"  \033[93m⏳ Đang cài {package}...\033[0m")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"  \033[92m✅ {package} - Đã cài\033[0m")
    
    # 2. Cài Tesseract OCR
    tesseract_path = find_or_install_tesseract()
    
    # 3. Cài Chromium + ChromeDriver
    chrome_path = find_or_install_chromium()
    
    print("=" * 55)
    print(f"  \033[92m✅ MÔI TRƯỜNG SẴN SÀNG!\033[0m")
    print(f"  Tesseract: {tesseract_path or '❌'}")
    print(f"  Chromium: {chrome_path or '❌'}")
    print("=" * 55)
    
    return tesseract_path, chrome_path

def find_or_install_tesseract():
    """Tìm hoặc cài Tesseract OCR"""
    # Các đường dẫn có thể có
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        r"C:\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"  \033[92m✅ Tìm thấy Tesseract: {path}\033[0m")
            return path
    
    # Tự động cài Tesseract trên Windows
    if os.name == 'nt':
        print("  \033[93m⏳ Đang tải Tesseract OCR...\033[0m")
        tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
        installer_path = os.path.join(os.environ.get('TEMP', '.'), "tesseract_installer.exe")
        
        try:
            # Tải installer
            response = requests.get(tesseract_url, stream=True)
            total = int(response.headers.get('content-length', 0))
            
            with open(installer_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded / total * 100
                        print(f"\r  ⏳ Tải Tesseract: {pct:.0f}%", end='', flush=True)
            print()
            
            # Cài đặt silent
            print("  ⏳ Đang cài Tesseract...")
            subprocess.run([installer_path, "/S", "/D=C:\\Tesseract-OCR"], 
                         capture_output=True, timeout=120)
            
            # Kiểm tra lại
            test_path = r"C:\Tesseract-OCR\tesseract.exe"
            if os.path.exists(test_path):
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = test_path
                print(f"  \033[92m✅ Tesseract đã cài: {test_path}\033[0m")
                return test_path
            
        except Exception as e:
            print(f"  \033[91m❌ Không thể cài Tesseract: {e}\033[0m")
            print("  \033[93m  Vui lòng cài thủ công:\033[0m")
            print("  \033[93m  https://github.com/UB-Mannheim/tesseract/wiki\033[0m")
    
    return None

def find_or_install_chromium():
    """Tìm Chrome hoặc cài Chromium"""
    # Tìm Chrome trước
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Chromium\Application\chrome.exe",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"  \033[92m✅ Tìm thấy Chrome/Chromium: {path}\033[0m")
            return path
    
    # Tự cài Chromium portable trên Windows
    if os.name == 'nt':
        print("  \033[93m⏳ Đang tải Chromium portable...\033[0m")
        chromium_url = "https://storage.googleapis.com/chromium-browser-snapshots/Win/1315727/chrome-win.zip"
        chromium_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromium")
        chromium_exe = os.path.join(chromium_dir, "chrome-win", "chrome.exe")
        
        if not os.path.exists(chromium_exe):
            try:
                zip_path = os.path.join(os.environ.get('TEMP', '.'), "chromium.zip")
                
                # Tải
                response = requests.get(chromium_url, stream=True)
                total = int(response.headers.get('content-length', 0))
                
                with open(zip_path, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = downloaded / total * 100
                            print(f"\r  ⏳ Tải Chromium: {pct:.0f}%", end='', flush=True)
                print()
                
                # Giải nén
                print("  ⏳ Đang giải nén Chromium...")
                os.makedirs(chromium_dir, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(chromium_dir)
                
                # Xóa file zip
                os.remove(zip_path)
                
                if os.path.exists(chromium_exe):
                    print(f"  \033[92m✅ Chromium đã cài: {chromium_exe}\033[0m")
                    return chromium_exe
                    
            except Exception as e:
                print(f"  \033[91m❌ Không thể tải Chromium: {e}\033[0m")
    
    return None

# ====================================================
# KHỞI TẠO MÔI TRƯỜNG
# ====================================================
TESSERACT_PATH, CHROMIUM_PATH = setup_environment()

# Import sau khi cài
import warnings
warnings.filterwarnings('ignore')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract

# ====================================================
# MÀU SẮC
# ====================================================
os.system('')
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
C = '\033[96m'; M = '\033[95m'; N = '\033[0m'; B = '\033[1m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def ok(s):    print(f"  {G}✅ {s}{N}")
def err(s):   print(f"  {R}❌ {s}{N}")
def info(s):  print(f"  {C}ℹ️  {s}{N}")
def warn(s):  print(f"  {Y}⚠️  {s}{N}")

# ====================================================
# LOADING BAR
# ====================================================
def progress_bar(current, total, label="", width=30):
    pct = current / total * 100 if total > 0 else 0
    filled = int(width * current / total) if total > 0 else 0
    bar = f"{G}{'█' * filled}{N}{'░' * (width - filled)}"
    print(f"\r  {label} [{bar}] {pct:.1f}% ({current}/{total})", end='', flush=True)

def countdown(seconds, label="Đợi"):
    for i in range(seconds, 0, -1):
        pct = (seconds - i + 1) / seconds * 100
        bar_len = 25
        filled = int(bar_len * (seconds - i + 1) / seconds)
        bar = f"{C}{'█' * filled}{N}{'░' * (bar_len - filled)}"
        print(f"\r  {label} [{bar}] {i}s", end='', flush=True)
        time.sleep(1)
    print()

# ====================================================
# GIẢI CAPTCHA
# ====================================================
def solve_captcha(driver):
    if not TESSERACT_PATH:
        return None
    
    try:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        
        for img in imgs:
            try:
                src = (img.get_attribute('src') or '').lower()
                if 'captcha' in src or 'verify' in src:
                    img_b64 = img.screenshot_as_base64
                    img_bytes = base64.b64decode(img_b64)
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    pil_img = pil_img.convert('L')
                    pil_img = pil_img.point(lambda x: 0 if x < 130 else 255)
                    pil_img = pil_img.resize((pil_img.width * 3, pil_img.height * 3), Image.LANCZOS)
                    
                    text = pytesseract.image_to_string(pil_img, config='--psm 7')
                    text = text.strip().replace(' ', '').replace('\n', '')
                    
                    if len(text) >= 3:
                        return text
            except:
                continue
    except:
        pass
    
    return None

# ====================================================
# ZEFOY BOT
# ====================================================
class ZefoyBot:
    def __init__(self):
        self.driver = None
        self.url = ""
        self.running = False
        self.stats = {"total": 0, "ok": 0, "fail": 0, "captcha": 0}
        self.headless = True
    
    def init_driver(self):
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=450,850")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36")
        
        # Dùng Chromium nếu có
        if CHROMIUM_PATH:
            options.binary_location = CHROMIUM_PATH
        
        # ChromeDriver tự động
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return True
    
    def fill_input(self, text):
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            all_fields = inputs + textareas
            
            if not all_fields:
                return False
            
            best = max(all_fields, key=lambda x: int(x.get_attribute('maxlength') or '0'))
            best.clear()
            time.sleep(0.2)
            best.send_keys(text)
            time.sleep(0.3)
            return True
        except:
            return False
    
    def click_send(self):
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            keywords = ['send', 'submit', 'start', 'views', 'get', 'free', 'search', 'go']
            
            for btn in buttons:
                try:
                    text = (btn.text or '').lower()
                    if any(kw in text for kw in keywords):
                        btn.click()
                        return True
                except:
                    continue
            
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            if inputs:
                inputs[0].send_keys(Keys.RETURN)
                return True
        except:
            pass
        return False
    
    def handle_captcha(self):
        try:
            page = self.driver.page_source.lower()
            if 'captcha' not in page and 'verify' not in page:
                return True
            
            # Thử OCR
            answer = solve_captcha(self.driver)
            if answer:
                self.stats["captcha"] += 1
                print(f"  {G}🤖 OCR: {answer}{N}")
                
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    ph = (inp.get_attribute('placeholder') or '').lower()
                    if 'captcha' in ph or 'verify' in ph or 'answer' in ph:
                        inp.clear()
                        inp.send_keys(answer)
                        time.sleep(0.5)
                        self.click_send()
                        time.sleep(3)
                        return True
                
                if inputs:
                    inputs[-1].clear()
                    inputs[-1].send_keys(answer)
                    time.sleep(0.5)
                    self.click_send()
                    time.sleep(3)
                    return True
            
            # Cần người giải
            if self.headless:
                warn("Đang mở trình duyệt để giải captcha...")
                self.driver.quit()
                self.headless = False
                time.sleep(2)
                self.init_driver()
                self.driver.get("https://zefoy.com")
                time.sleep(4)
            
            print(f"\n{Y}{'='*50}{N}")
            print(f"{Y}⚠️  VUI LÒNG GIẢI CAPTCHA TRÊN TRÌNH DUYỆT{N}")
            print(f"{Y}  Sau đó nhấn Enter để tiếp tục...{N}")
            print(f"{Y}{'='*50}{N}")
            input(f"  {C}> {N}")
            return True
            
        except:
            return True
    
    def submit_once(self):
        try:
            self.driver.get("https://zefoy.com")
            time.sleep(4)
            self.handle_captcha()
            time.sleep(2)
            
            if not self.fill_input(self.url):
                return False
            
            self.click_send()
            time.sleep(5)
            self.handle_captcha()
            time.sleep(3)
            
            page = self.driver.page_source.lower()
            if 'error' in page or 'fail' in page or 'invalid' in page:
                return False
            
            return True
            
        except Exception as e:
            err(f"Lỗi: {e}")
            return False
    
    def run_loop(self, delay=60):
        self.running = True
        
        print(f"\n{B}{Y}{'='*50}{N}")
        print(f"{B}{G}  🎵 ZEFOY AUTO VIEWS{N}")
        print(f"{B}{Y}{'='*50}{N}")
        print(f"  Link: {self.url[:45]}...")
        print(f"  Delay: {delay}s")
        print(f"  Chế độ: {'ẨN' if self.headless else 'HIỆN'}")
        print(f"  OCR: {G if TESSERACT_PATH else R}{'CÓ' if TESSERACT_PATH else 'KHÔNG'}{N}")
        print(f"{'='*50}\n")
        
        while self.running:
            self.stats["total"] += 1
            
            print(f"{B}┌─ Lần #{self.stats['total']} ──────────────────┐{N}")
            
            if self.submit_once():
                self.stats["ok"] += 1
                ok(f"OK! ({self.stats['ok']}/{self.stats['total']})")
            else:
                self.stats["fail"] += 1
                err(f"Fail ({self.stats['fail']}/{self.stats['total']})")
            
            print(f"│ 📊 OK:{G}{self.stats['ok']}{N} Fail:{R}{self.stats['fail']}{N} | 🤖 Captcha:{self.stats['captcha']}")
            print(f"{B}└{'─'*40}┘{N}\n")
            
            countdown(delay, "⏳ Nghỉ")
    
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
        print(f"{B}{Y}  🤖 ZEFOY AUTO - TIKTOK VIEW BUFFER{N}")
        print(f"{B}{Y}{'='*50}{N}")
        
        if bot.url:
            print(f"  {C}Link:{N} {bot.url[:40]}...")
        
        print(f"  {G}OK:{N}{bot.stats['ok']} | {R}Fail:{N}{bot.stats['fail']} | 🤖:{bot.stats['captcha']}")
        print(f"  Chế độ: {'ẨN' if bot.headless else 'HIỆN'}")
        print(f"  {'● ĐANG CHẠY' if bot.running else '● DỪNG'}")
        print(f"{'-'*50}")
        print(f"  {B}1.{N} 🎯 Nhập link + CHẠY")
        print(f"  {B}2.{N} 👁  Ẩn/Hiện browser")
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
            bot.stats = {"total": 0, "ok": 0, "fail": 0, "captcha": 0}
            
            delay = input(f"Delay (giây) [60]: ").strip()
            delay = int(delay) if delay.isdigit() else 60
            
            info("Khởi tạo Chrome + ChromeDriver...")
            if not bot.init_driver():
                err("Không khởi tạo được!")
                input("\nEnter...")
                continue
            
            ok("Sẵn sàng!")
            
            thread = threading.Thread(target=bot.run_loop, args=(delay,), daemon=True)
            thread.start()
            
            input(f"\n{G}✅ Đang chạy!{N} Enter về menu...")
        
        elif c == "2":
            bot.headless = not bot.headless
            if bot.driver:
                bot.driver.quit()
                bot.init_driver()
            ok(f"Chế độ: {'ẨN' if bot.headless else 'HIỆN'}")
            input("\nEnter...")
        
        elif c == "3":
            bot.stop()
            ok("Đã dừng!")
            input("\nEnter...")
        
        elif c == "4":
            bot.stop()
            print(f"\n{Y}👋 Tạm biệt!{N}")
            sys.exit(0)

if __name__ == "__main__":
    main()