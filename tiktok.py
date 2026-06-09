# -*- coding: utf-8 -*-
# FILE: zefoy_cookie.py
# BẮT COOKIE TỪ CHROME THẬT -> DÙNG LẠI CHO REQUESTS

import time
import threading
import os
import sys
import json
import requests
import subprocess
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "--quiet"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; C = '\033[96m'; N = '\033[0m'; B = '\033[1m'
def ok(s):   print(f"  {G}✅ {s}{N}")
def err(s):  print(f"  {R}❌ {s}{N}")
def info(s): print(f"  {C}ℹ️  {s}{N}")
def clear(): os.system('clear' if os.name != 'nt' else 'cls')

COOKIE_FILE = "zefoy_cookies.json"

class ZefoyCookie:
    def __init__(self):
        self.session = requests.Session()
        self.cookies = {}
        self.load_cookies()
    
    def load_cookies(self):
        if os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE) as f:
                self.cookies = json.load(f)
            # Set vào session
            for cookie in self.cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            return True
        return False
    
    def save_cookies(self, driver):
        """Lấy cookie từ Selenium driver"""
        selenium_cookies = driver.get_cookies()
        self.cookies = []
        for c in selenium_cookies:
            self.cookies.append({
                'name': c['name'],
                'value': c['value'],
                'domain': c.get('domain', ''),
            })
            self.session.cookies.set(c['name'], c['value'])
        
        with open(COOKIE_FILE, 'w') as f:
            json.dump(self.cookies, f, indent=2)
        
        ok(f"Đã lưu {len(self.cookies)} cookies")
    
    def is_valid(self):
        """Kiểm tra cookie còn sống không"""
        try:
            r = self.session.get(
                "https://zefoy.com/",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html",
                },
                timeout=10
            )
            return r.status_code == 200 and 'zefoy' in r.text.lower()
        except:
            return False
    
    def submit(self, tiktok_url):
        """Gửi link dùng cookie"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://zefoy.com",
            "Referer": "https://zefoy.com/",
            "X-Requested-With": "XMLHttpRequest",
        }
        
        try:
            # Lấy trang chủ để có form token
            r = self.session.get("https://zefoy.com/", headers=headers, timeout=10)
            html = r.text
            
            # Tìm form key
            import re
            form_match = re.search(r'name=["\']([a-f0-9]{40,})["\']\s+value=["\']([^"\']*)["\']', html)
            key = form_match.group(1) if form_match else "6eb5da523e1854b87b39a0119a94f342c770c284629ce6dd7ff83f6a"
            val = form_match.group(2) if form_match else "easy"
            
            # Gửi
            data = {key: val, 'url': tiktok_url}
            
            r = self.session.post(
                "https://zefoy.com/",
                data=data,
                headers=headers,
                timeout=15
            )
            
            info(f"Status: {r.status_code}")
            info(f"Response: {r.text[:200]}")
            
            return r.status_code == 200 and 'error' not in r.text.lower()
            
        except Exception as e:
            err(str(e))
            return False

def capture_cookies():
    """Mở Chrome, user giải captcha, tool bắt cookie"""
    print(f"\n{Y}{'='*50}{N}")
    print(f"{Y}  MỞ CHROME - BẠN GIẢI CAPTCHA 1 LẦN{N}")
    print(f"{Y}  Sau đó tool tự lấy cookie dùng mãi{N}")
    print(f"{Y}{'='*50}{N}\n")
    
    options = Options()
    options.add_argument("--window-size=500,900")
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://zefoy.com")
    
    print(f"{G}  Hãy giải captcha trên Chrome (nếu có){N}")
    print(f"{G}  Sau đó NHẤN ENTER tại đây...{N}")
    input()
    
    zc = ZefoyCookie()
    zc.save_cookies(driver)
    
    driver.quit()
    ok("Đã lấy cookie xong!")
    
    # Test cookie
    if zc.is_valid():
        ok("Cookie hoạt động!")
        return zc
    else:
        err("Cookie không hoạt động!")
        return None

def main():
    zc = ZefoyCookie()
    has_cookie = zc.load_cookies()
    
    if has_cookie:
        print(f"\n  {C}Đã tìm thấy cookie đã lưu{N}")
        if zc.is_valid():
            ok("Cookie còn sống!")
        else:
            warn("Cookie hết hạn, cần lấy lại")
            has_cookie = False
    
    while True:
        clear()
        print(f"{B}{Y}{'='*40}{N}")
        print(f"{B}{Y}  ZEFOY COOKIE TOOL{N}")
        print(f"{B}{Y}{'='*40}{N}")
        print(f"  Cookie: {G if has_cookie else R}{'CÓ' if has_cookie else 'KHÔNG'}{N}")
        print(f"  1. 🍪 Lấy cookie mới (mở Chrome)")
        print(f"  2. 🎯 Gửi link test")
        print(f"  3. 🔄 Gửi auto loop")
        print(f"  4. 🚪 Thoát")
        print(f"{'='*40}")
        
        c = input("\n> ").strip()
        
        if c == "1":
            zc = capture_cookies()
            has_cookie = zc is not None
            input("\nEnter...")
        
        elif c == "2":
            if not has_cookie:
                print("Cần lấy cookie trước!")
                input("Enter...")
                continue
            
            url = input("Link TikTok: ").strip()
            if url:
                info("Đang gửi...")
                if zc.submit(url):
                    ok("Thành công!")
                else:
                    err("Thất bại - Cookie có thể hết hạn")
            input("\nEnter...")
        
        elif c == "3":
            if not has_cookie:
                print("Cần lấy cookie trước!")
                input("Enter...")
                continue
            
            url = input("Link TikTok: ").strip()
            if "tiktok.com" not in url:
                print("Link sai!")
                input("Enter...")
                continue
            
            delay = int(input("Delay giây [60]: ") or "60")
            
            print(f"\n{G}Đang chạy auto...{N}")
            count = 0
            try:
                while True:
                    count += 1
                    print(f"\n{B}── Lần #{count} ──{N}")
                    
                    if zc.submit(url):
                        ok("OK!")
                    else:
                        err("Fail - Cookie hết hạn!")
                        break
                    
                    for i in range(delay, 0, -1):
                        print(f"\r  ⏳ {i}s ", end='', flush=True)
                        time.sleep(1)
                    print()
            except KeyboardInterrupt:
                print("\nDừng!")
            input("\nEnter...")
        
        elif c == "4":
            sys.exit(0)

if __name__ == "__main__":
    main()
