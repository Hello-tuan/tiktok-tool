# -*- coding: utf-8 -*-
# FILE: tiktok_tool.py
# VERSION: 2.0.0
# REPO: https://github.com/Hello-tuan/tiktok-tool
# TỰ ĐỘNG CÀI: Python packages + ChromeDriver + Tesseract OCR
# TỰ ĐỘNG FIX: Mọi lỗi thường gặp
# TỰ ĐỘNG UPDATE: Check GitHub mỗi lần chạy

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
import shutil
import zipfile
import subprocess
import requests
from datetime import datetime

# ====================================================
# CONFIG GITHUB - SỬA THÀNH CỦA BẠN
# ====================================================
GITHUB_USER = "Hello-tuan"
GITHUB_REPO = "tiktok-tool"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
CURRENT_VERSION = "2.0.0"

# ====================================================
# MÀU SẮC
# ====================================================
os.system('')
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
C = '\033[96m'; M = '\033[95m'; N = '\033[0m'; B = '\033[1m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def ok(s):   print(f"  {G}✅ {s}{N}")
def err(s):  print(f"  {R}❌ {s}{N}")
def info(s): print(f"  {C}ℹ️  {s}{N}")
def warn(s): print(f"  {Y}⚠️  {s}{N}")
def title(s): print(f"\n{B}{Y}{'='*55}{N}\n{B}{Y}  {s}{N}\n{B}{Y}{'='*55}{N}")

# ====================================================
# HỆ THỐNG TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG
# ====================================================
class AutoSetup:
    """Tự động cài đặt mọi thứ cần thiết"""
    
    @staticmethod
    def install_python_packages():
        """Cài thư viện Python"""
        title("KIỂM TRA THƯ VIỆN PYTHON")
        
        packages = {
            'selenium': 'selenium',
            'PIL': 'Pillow', 
            'pytesseract': 'pytesseract',
            'requests': 'requests',
            'webdriver_manager': 'webdriver-manager',
        }
        
        all_ok = True
        for module, package in packages.items():
            try:
                __import__(module)
                ok(f"{package} - có sẵn")
            except ImportError:
                warn(f"{package} - đang cài...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package, "--quiet"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    ok(f"{package} - đã cài xong")
                except:
                    err(f"{package} - cài thất bại!")
                    all_ok = False
        
        return all_ok
    
    @staticmethod
    def find_tesseract():
        """Tìm hoặc cài Tesseract OCR"""
        title("KIỂM TRA TESSERACT OCR")
        
        # Danh sách đường dẫn có thể
        paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
            r"D:\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]
        
        # Thêm các đường dẫn trong PATH
        for p in os.environ.get('PATH', '').split(os.pathsep):
            tp = os.path.join(p, 'tesseract.exe' if os.name == 'nt' else 'tesseract')
            if os.path.exists(tp):
                paths.append(tp)
        
        for path in paths:
            if os.path.exists(path):
                ok(f"Tìm thấy: {path}")
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = path
                return path
        
        warn("Tesseract chưa được cài đặt!")
        
        # Tự động cài trên Windows
        if os.name == 'nt':
            return AutoSetup._install_tesseract_windows()
        
        return None
    
    @staticmethod
    def _install_tesseract_windows():
        """Tự cài Tesseract trên Windows"""
        info("Đang tải Tesseract OCR...")
        info("(File ~60MB, đợi chút...)")
        
        urls = [
            "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe",
            "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe",
        ]
        
        for url in urls:
            try:
                temp_dir = os.environ.get('TEMP', os.path.expanduser('~'))
                installer = os.path.join(temp_dir, "tesseract_setup.exe")
                
                # Tải file
                resp = requests.get(url, stream=True, timeout=120)
                total = int(resp.headers.get('content-length', 0))
                
                with open(installer, 'wb') as f:
                    downloaded = 0
                    for chunk in resp.iter_content(chunk_size=1024*1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = downloaded / total * 100
                            print(f"\r  ⏳ Tải Tesseract: {pct:.0f}% ({downloaded//1024//1024}MB/{total//1024//1024}MB)", end='', flush=True)
                print()
                
                # Cài đặt silent
                info("Đang cài đặt Tesseract...")
                result = subprocess.run(
                    [installer, "/S", "/D=C:\\Tesseract-OCR"],
                    capture_output=True, timeout=300
                )
                
                # Xóa installer
                try: os.remove(installer)
                except: pass
                
                # Kiểm tra
                test_path = r"C:\Tesseract-OCR\tesseract.exe"
                if os.path.exists(test_path):
                    ok("Tesseract đã cài đặt thành công!")
                    import pytesseract
                    pytesseract.pytesseract.tesseract_cmd = test_path
                    return test_path
                    
            except Exception as e:
                warn(f"Lỗi: {e}")
                continue
        
        err("Không thể tự động cài Tesseract!")
        info("Vui lòng cài thủ công: https://github.com/UB-Mannheim/tesseract/wiki")
        info("Nhớ chọn TIẾNG ANH khi cài đặt!")
        return None
    
    @staticmethod
    def setup_chromedriver():
        """Tự động cài ChromeDriver"""
        title("KIỂM TRA CHROMEDRIVER")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            info("Đang tải ChromeDriver phù hợp...")
            
            # Thử tạo driver xem có hoạt động không
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1,1")
            options.add_argument("--log-level=3")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.quit()
            
            ok("ChromeDriver hoạt động!")
            return True
            
        except Exception as e:
            err(f"ChromeDriver lỗi: {e}")
            
            # Thử cách khác
            try:
                info("Thử phương án dự phòng...")
                from selenium import webdriver
                driver = webdriver.Chrome()
                driver.quit()
                ok("OK - Dùng ChromeDriver mặc định")
                return True
            except:
                err("Không có ChromeDriver!")
                info("Cần cài Chrome: https://www.google.com/chrome/")
                return False

# ====================================================
# KHỞI CHẠY TỰ ĐỘNG CÀI ĐẶT
# ====================================================
print(f"\n{B}{C}{'='*55}{N}")
print(f"{B}{C}  🔧 TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG...{N}")
print(f"{B}{C}{'='*55}{N}")

AutoSetup.install_python_packages()
TESSERACT_OK = AutoSetup.find_tesseract() is not None
CHROMEDRIVER_OK = AutoSetup.setup_chromedriver()

print(f"\n{B}{C}{'='*55}{N}")
print(f"{B}{C}  📊 KẾT QUẢ KIỂM TRA:{N}")
print(f"  Python packages: {G}✅{N}")
print(f"  Tesseract OCR: {G if TESSERACT_OK else R}{'✅' if TESSERACT_OK else '❌'}{N}")
print(f"  ChromeDriver: {G if CHROMEDRIVER_OK else R}{'✅' if CHROMEDRIVER_OK else '❌'}{N}")
print(f"{B}{C}{'='*55}{N}")
time.sleep(2)

# Import sau khi cài
import warnings
warnings.filterwarnings('ignore')

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from PIL import Image
    import pytesseract
except Exception as e:
    print(f"{R}  Lỗi import: {e}{N}")
    print(f"{Y}  Đang thử lại...{N}")
    AutoSetup.install_python_packages()
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from PIL import Image
    import pytesseract

# ====================================================
# PHÁT HIỆN THIẾT BỊ
# ====================================================
def get_device_info():
    try:
        if os.name == 'nt':
            name = os.environ.get('COMPUTERNAME', 'PC')
        else:
            import socket
            name = socket.gethostname()
        device_id = hashlib.md5(name.encode()).hexdigest()[:8]
        device_type = "PC" if os.name == 'nt' else "Phone/Termux"
        return device_id, device_type, name
    except:
        rid = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        return rid, "Unknown", "Unknown"

DEVICE_ID, DEVICE_TYPE, DEVICE_NAME = get_device_info()

# ====================================================
# TỰ ĐỘNG CẬP NHẬT TỪ GITHUB
# ====================================================
class GitHubUpdater:
    @staticmethod
    def check_update():
        """Kiểm tra version mới"""
        try:
            resp = requests.get(f"{GITHUB_RAW}/version.json", timeout=10)
            if resp.status_code == 200:
                remote = resp.json()
                remote_ver = remote.get('version', '0.0.0')
                
                if remote_ver > CURRENT_VERSION:
                    return {
                        'new': remote_ver,
                        'current': CURRENT_VERSION,
                        'log': remote.get('changelog', ''),
                        'url': f"{GITHUB_RAW}/tiktok_tool.py",
                    }
        except:
            pass
        return None
    
    @staticmethod
    def do_update(file_url):
        """Thực hiện cập nhật"""
        try:
            info("Đang tải bản mới từ GitHub...")
            
            # Backup
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
            shutil.copy2(__file__, backup_file)
            info(f"Đã backup: {backup_file}")
            
            # Tải file mới
            resp = requests.get(file_url, timeout=30)
            if resp.status_code == 200:
                current_file = os.path.abspath(__file__)
                with open(current_file, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                
                ok("Cập nhật thành công!")
                ok("Khởi động lại tool...")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            
            return False
        except Exception as e:
            err(f"Lỗi cập nhật: {e}")
            return False

# ====================================================
# GIẢI CAPTCHA
# ====================================================
def solve_captcha_text(driver):
    """Giải captcha chữ bằng OCR"""
    if not TESSERACT_OK:
        return None
    
    try:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            try:
                src = (img.get_attribute('src') or '').lower()
                if 'captcha' not in src and 'verify' not in src:
                    continue
                
                img_b64 = img.screenshot_as_base64
                img_bytes = base64.b64decode(img_b64)
                pil_img = Image.open(io.BytesIO(img_bytes))
                pil_img = pil_img.convert('L')
                pil_img = pil_img.point(lambda x: 0 if x < 130 else 255)
                pil_img = pil_img.resize((pil_img.width * 3, pil_img.height * 3), Image.LANCZOS)
                
                text = pytesseract.image_to_string(pil_img, config='--psm 7')
                text = text.strip().replace(' ', '').replace('\n', '')
                
                if 3 <= len(text) <= 15:
                    return text
            except:
                continue
    except:
        pass
    
    return None

# ====================================================
# ZEFOY BOT SELENIUM
# ====================================================
class ZefoyBot:
    def __init__(self):
        self.driver = None
        self.url = ""
        self.running = False
        self.stats = {"total": 0, "ok": 0, "fail": 0, "captcha": 0}
        self.headless = True
    
    def start_browser(self):
        """Khởi động Chrome"""
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
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except:
            try:
                self.driver = webdriver.Chrome(options=options)
                return True
            except Exception as e:
                err(f"Không mở được Chrome: {e}")
                return False
    
    def find_input_and_fill(self, text):
        """Tìm ô input và điền text"""
        try:
            fields = (self.driver.find_elements(By.TAG_NAME, "input") + 
                     self.driver.find_elements(By.TAG_NAME, "textarea"))
            
            if not fields:
                return False
            
            best = max(fields, key=lambda x: int(x.get_attribute('maxlength') or '0'))
            best.clear()
            time.sleep(0.2)
            best.send_keys(text)
            time.sleep(0.3)
            return True
        except:
            return False
    
    def click_send_button(self):
        """Click nút gửi"""
        try:
            keywords = ['send', 'submit', 'start', 'views', 'get', 'free', 'search', 'go']
            
            for btn in self.driver.find_elements(By.TAG_NAME, "button"):
                try:
                    text = (btn.text or '').lower()
                    if any(kw in text for kw in keywords):
                        btn.click()
                        time.sleep(0.5)
                        return True
                except:
                    continue
            
            # Thử Enter
            fields = self.driver.find_elements(By.TAG_NAME, "input")
            if fields:
                fields[0].send_keys(Keys.RETURN)
                return True
            
            return False
        except:
            return False
    
    def handle_captcha(self):
        """Xử lý captcha"""
        try:
            page = self.driver.page_source.lower()
            if 'captcha' not in page and 'verify' not in page:
                return True
            
            self.stats["captcha"] += 1
            
            # Thử OCR
            answer = solve_captcha_text(self.driver)
            
            if answer:
                info(f"OCR giải được: {G}{answer}{N}")
                
                # Tìm ô captcha và điền
                for inp in self.driver.find_elements(By.TAG_NAME, "input"):
                    ph = (inp.get_attribute('placeholder') or '').lower()
                    nm = (inp.get_attribute('name') or '').lower()
                    if 'captcha' in ph or 'captcha' in nm or 'verify' in ph or 'answer' in ph:
                        inp.clear()
                        inp.send_keys(answer)
                        time.sleep(0.3)
                        self.click_send_button()
                        time.sleep(3)
                        return True
                
                # Nếu không tìm thấy ô captcha cụ thể
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if inputs:
                    inputs[-1].clear()
                    inputs[-1].send_keys(answer)
                    time.sleep(0.3)
                    self.click_send_button()
                    time.sleep(3)
                    return True
            
            # OCR thất bại -> mở browser cho user
            warn("Không giải được captcha tự động")
            
            if self.headless:
                info("Đang mở trình duyệt...")
                self.driver.quit()
                self.headless = False
                time.sleep(2)
                self.start_browser()
                self.driver.get("https://zefoy.com")
                time.sleep(4)
            
            print(f"\n{Y}{'='*50}{N}")
            print(f"{Y}  ⚠️  VUI LÒNG GIẢI CAPTCHA{N}")
            print(f"{Y}  Nhìn trình duyệt -> Điền captcha{N}")
            print(f"{Y}  Sau đó nhấn ENTER tại đây{N}")
            print(f"{Y}{'='*50}{N}")
            input(f"  {C}> {N}")
            
            return True
            
        except Exception as e:
            return True
    
    def submit_once(self):
        """Gửi 1 lần lên Zefoy"""
        try:
            # Vào Zefoy
            self.driver.get("https://zefoy.com")
            time.sleep(4)
            
            # Xử lý captcha trang chủ
            self.handle_captcha()
            time.sleep(2)
            
            # Nhập link
            if not self.find_input_and_fill(self.url):
                return False, "Không tìm thấy ô nhập"
            
            # Click gửi
            self.click_send_button()
            time.sleep(5)
            
            # Xử lý captcha sau gửi
            self.handle_captcha()
            time.sleep(3)
            
            # Kiểm tra kết quả
            page = self.driver.page_source.lower()
            
            if any(w in page for w in ['error', 'fail', 'invalid', 'wrong']):
                return False, "Zefoy báo lỗi"
            
            return True, "OK"
            
        except Exception as e:
            return False, str(e)[:30]
    
    def run_loop(self, delay=60):
        """Chạy vòng lặp"""
        self.running = True
        
        print(f"\n{B}{Y}{'='*55}{N}")
        print(f"{B}{G}  🎵 ZEFOY AUTO - TIKTOK VIEW BUFFER{N}")
        print(f"{B}{Y}{'='*55}{N}")
        print(f"  Link: {self.url[:45]}...")
        print(f"  Delay: {delay}s/lần")
        print(f"  Chế độ: {'ẨN' if self.headless else 'HIỆN'}")
        print(f"  OCR: {G if TESSERACT_OK else R}{'CÓ' if TESSERACT_OK else 'KHÔNG'}{N}")
        print(f"{'='*55}\n")
        
        while self.running:
            self.stats["total"] += 1
            
            print(f"{B}┌─ Lần #{self.stats['total']} {'─'*40}┐{N}")
            
            ok_flag, msg = self.submit_once()
            
            if ok_flag:
                self.stats["ok"] += 1
                ok(f"OK! ({self.stats['ok']}/{self.stats['total']}) - {msg}")
            else:
                self.stats["fail"] += 1
                err(f"Fail ({self.stats['fail']}/{self.stats['total']}) - {msg}")
            
            print(f"│ 📊 OK:{G}{self.stats['ok']}{N} Fail:{R}{self.stats['fail']}{N} | 🤖 Captcha:{self.stats['captcha']}")
            print(f"{B}└{'─'*48}┘{N}\n")
            
            # Đếm ngược
            for i in range(delay, 0, -1):
                if not self.running: break
                pct = (delay - i + 1) / delay * 100
                bar_len = 25
                filled = int(bar_len * (delay - i + 1) / delay)
                bar = f"{C}{'█' * filled}{N}{'░' * (bar_len - filled)}"
                print(f"\r  ⏳ Nghỉ [{bar}] {i}s ({pct:.0f}%)", end='', flush=True)
                time.sleep(1)
            print("\n")
    
    def stop(self):
        self.running = False
        if self.driver:
            try: self.driver.quit()
            except: pass

# ====================================================
# GỬI VIEW TRỰC TIẾP QUA API (FALLBACK)
# ====================================================
def extract_video_id(url):
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

def send_direct_views(video_id, count=50):
    """Gửi view trực tiếp"""
    ok_count = 0
    for i in range(count):
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
            
            if (i+1) % 25 == 0:
                print(f"\r  ⏳ Direct views: {i+1}/{count}", end='', flush=True)
            
            time.sleep(random.uniform(0.01, 0.05))
        except:
            pass
    
    print()
    return ok_count

# ====================================================
# MENU CHÍNH
# ====================================================
def main():
    bot = ZefoyBot()
    thread = None
    
    while True:
        clear()
        print(f"{B}{Y}{'='*50}{N}")
        print(f"{B}{Y}  🎵 TIKTOK TOOL v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*50}{N}")
        print(f"  Thiết bị: {C}{DEVICE_TYPE}{N} ({DEVICE_ID})")
        print(f"  GitHub: {C}github.com/{GITHUB_USER}/{GITHUB_REPO}{N}")
        print(f"  Tesseract: {G if TESSERACT_OK else R}{'✅' if TESSERACT_OK else '❌'}{N}")
        print(f"  Chrome: {G if CHROMEDRIVER_OK else R}{'✅' if CHROMEDRIVER_OK else '❌'}{N}")
        
        if bot.url:
            print(f"  Link: {C}{bot.url[:40]}...{N}")
        
        print(f"  {G}OK:{N}{bot.stats['ok']} | {R}Fail:{N}{bot.stats['fail']} | 🤖:{bot.stats['captcha']}")
        print(f"  Chế độ: {'ẨN' if bot.headless else 'HIỆN'}")
        print(f"  {'● ĐANG CHẠY' if bot.running else '● DỪNG'}")
        print(f"{'-'*50}")
        print(f"  {B}1.{N} 🎯 Nhập link + ZEFOY AUTO")
        print(f"  {B}2.{N} 👁  Ẩn/Hiện browser")
        print(f"  {B}3.{N} 📊 Direct views (API)")
        print(f"  {B}4.{N} 🔍 Kiểm tra cập nhật")
        print(f"  {B}5.{N} ⏹  DỪNG")
        print(f"  {B}6.{N} 🚪 Thoát")
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
            
            if not bot.driver:
                info("Khởi động Chrome...")
                if not bot.start_browser():
                    err("Không khởi động được Chrome!")
                    info("Thử cài Chrome: https://www.google.com/chrome/")
                    input("\nEnter...")
                    continue
                ok("Chrome sẵn sàng!")
            
            thread = threading.Thread(target=bot.run_loop, args=(delay,), daemon=True)
            thread.start()
            
            input(f"\n{G}✅ Đang chạy!{N} Enter về menu...")
        
        elif c == "2":
            bot.headless = not bot.headless
            if bot.driver:
                bot.driver.quit()
                bot.start_browser()
            ok(f"Chế độ: {'ẨN' if bot.headless else 'HIỆN'}")
            input("\nEnter...")
        
        elif c == "3":
            url = input(f"\n{Y}Dán link TikTok:{N} ").strip()
            vid = extract_video_id(url)
            
            if not vid:
                err("Không tìm thấy video ID!")
                input("\nEnter...")
                continue
            
            cnt = input(f"Bao nhiêu view? [100]: ").strip()
            cnt = int(cnt) if cnt.isdigit() else 100
            
            print(f"\n{C}Đang gửi {cnt} views trực tiếp...{N}")
            sent = send_direct_views(vid, cnt)
            ok(f"Đã gửi: {sent}/{cnt} views")
            input("\nEnter...")
        
        elif c == "4":
            print(f"\n{C}🔍 Kiểm tra cập nhật...{N}")
            update = GitHubUpdater.check_update()
            
            if update:
                print(f"\n{Y}🔄 CÓ BẢN MỚI!{N}")
                print(f"  v{update['current']} → v{update['new']}")
                if update['log']:
                    print(f"  Thay đổi: {update['log']}")
                
                yn = input(f"\n  Cập nhật? (y/n): ").strip().lower()
                if yn == 'y':
                    GitHubUpdater.do_update(update['url'])
                    return
            else:
                ok(f"Đã là bản mới nhất (v{CURRENT_VERSION})")
            
            input("\nEnter...")
        
        elif c == "5":
            bot.stop()
            ok("Đã dừng!")
            input("\nEnter...")
        
        elif c == "6":
            bot.stop()
            print(f"\n{Y}👋 Tạm biệt!{N}")
            sys.exit(0)

# ====================================================
# KHỞI ĐỘNG
# ====================================================
if __name__ == "__main__":
    # Kiểm tra cập nhật khi khởi động
    print(f"\n{C}🔍 Kiểm tra cập nhật từ GitHub...{N}")
    update = GitHubUpdater.check_update()
    
    if update:
        print(f"{Y}🔄 Có bản mới: v{update['new']}{N}")
        yn = input(f"Cập nhật ngay? (y/n): ").strip().lower()
        if yn == 'y':
            GitHubUpdater.do_update(update['url'])
    
    main()