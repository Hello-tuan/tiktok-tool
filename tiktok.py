# -*- coding: utf-8 -*-
# FILE: zefoy_api_direct.py
# VERSION: 1.2.0
# REPO: https://github.com/Hello-tuan/tiktok-tool
# FIX: VÀO TRANG CHỦ -> TÌM MỤC VIEWS -> CLICK -> GỬI LINK

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
from urllib.parse import urljoin, parse_qs

# ====================================================
# CẤU HÌNH
# ====================================================
GITHUB_USER = "Hello-tuan"
GITHUB_REPO = "tiktok-tool"
GITHUB_BRANCH = "main"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
CURRENT_VERSION = "1.2.0"
TOOL_FILENAME = "zefoy_api_direct.py"

# ====================================================
# MÀU
# ====================================================
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
C = '\033[96m'; N = '\033[0m'; B = '\033[1m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def ok(s):   print(f"  {G}✅ {s}{N}")
def err(s):  print(f"  {R}❌ {s}{N}")
def info(s): print(f"  {C}ℹ️  {s}{N}")
def warn(s): print(f"  {Y}⚠️  {s}{N}")
def log(s):  print(f"  [{time.strftime('%H:%M:%S')}] {s}")

# ====================================================
# TỰ ĐỘNG CẬP NHẬT
# ====================================================
class AutoUpdater:
    @staticmethod
    def parse_version(ver_str):
        try: return tuple(map(int, ver_str.split('.')))
        except: return (0,0,0)
    
    @staticmethod
    def bump_version(ver_str):
        v = AutoUpdater.parse_version(ver_str)
        return f"{v[0]}.{v[1]+1}.0"
    
    @staticmethod
    def check():
        try:
            resp = requests.get(f"{GITHUB_RAW}/version.json", timeout=10)
            if resp.status_code == 200:
                remote = resp.json()
                if AutoUpdater.parse_version(remote.get('version','0')) > AutoUpdater.parse_version(CURRENT_VERSION):
                    return {
                        'new': remote['version'],
                        'url': remote.get('download_url', f'{GITHUB_RAW}/{TOOL_FILENAME}'),
                        'log': remote.get('changelog','')
                    }
        except: pass
        return None
    
    @staticmethod
    def update(url, new_ver):
        try:
            info("Đang tải bản mới...")
            os.makedirs("backups", exist_ok=True)
            shutil.copy2(__file__, f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
            
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                content = resp.text
                next_ver = AutoUpdater.bump_version(new_ver)
                content = re.sub(r'CURRENT_VERSION\s*=\s*"[^"]+"', f'CURRENT_VERSION = "{next_ver}"', content)
                
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                ok(f"Đã update lên v{next_ver}")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            err(f"Lỗi: {e}")

# ====================================================
# ZEFOY CLIENT - ĐÚNG THỨ TỰ
# ====================================================
class ZefoyClient:
    """Vào Zefoy -> Tìm Views -> Click -> Gửi link"""
    
    ZEFOY_URLS = ["https://zefoy.com", "https://zefoy.app"]
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = ""
        self.current_page = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    
    def connect(self):
        """BƯỚC 1: Vào trang chủ Zefoy"""
        for url in self.ZEFOY_URLS:
            try:
                log(f"Thử kết nối: {url}")
                resp = self.session.get(url, headers=self.headers, timeout=15)
                
                if resp.status_code == 200 and 'zefoy' in resp.text.lower():
                    self.base_url = url
                    self.current_page = resp.text
                    ok(f"Đã vào Zefoy!")
                    return True
            except:
                continue
        
        err("Không vào được Zefoy!")
        return False
    
    def find_views_section(self):
        """BƯỚC 2: Tìm mục Views trên trang chủ"""
        log("Đang quét tìm mục Views...")
        
        # Phân tích trang
        html = self.current_page
        
        # Tìm tất cả link và button
        patterns = [
            # Pattern 1: Thẻ a có href
            r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>\s*(.*?)\s*</a>',
            # Pattern 2: Button
            r'<button[^>]*>(.*?)</button>',
            # Pattern 3: Div có onclick
            r'<div[^>]*onclick\s*=\s*["\']([^"\']+)["\'][^>]*>\s*(.*?)\s*</div>',
            # Pattern 4: Card/Service item
            r'<div[^>]*class\s*=\s*["\'][^"\']*card[^"\']*["\'][^>]*>\s*(.*?)\s*</div>',
        ]
        
        views_keywords = [
            'views', 'view', 'tiktok views', 'free views',
            'service', 'send views', 'increase',
            'lượt xem', 'tăng view',
        ]
        
        best_match = None
        best_score = 0
        
        # Tìm trong links
        links = re.findall(r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
        
        for href, text in links:
            text_clean = re.sub(r'<[^>]+>', '', text).strip()
            combined = (text_clean + ' ' + href).lower()
            
            score = sum(1 for kw in views_keywords if kw in combined)
            
            if score > best_score:
                best_score = score
                best_match = ('link', urljoin(self.base_url, href), text_clean)
        
        # Tìm trong forms
        forms = re.findall(r'<form[^>]*action\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</form>', html, re.DOTALL | re.IGNORECASE)
        
        for action, form_content in forms:
            form_text = re.sub(r'<[^>]+>', '', form_content).lower()
            score = sum(1 for kw in views_keywords if kw in form_text)
            
            if score > best_score:
                best_score = score
                action_url = urljoin(self.base_url, action) if action else self.base_url
                best_match = ('form', action_url, form_text[:50])
        
        # Tìm buttons
        buttons = re.findall(r'<button[^>]*>(.*?)</button>', html, re.DOTALL | re.IGNORECASE)
        for btn_text in buttons:
            text_clean = re.sub(r'<[^>]+>', '', btn_text).strip().lower()
            score = sum(1 for kw in views_keywords if kw in text_clean)
            
            if score > best_score:
                best_score = score
                best_match = ('button', None, text_clean)
        
        if best_match:
            match_type, url, text = best_match
            ok(f"Tìm thấy: [{match_type}] {text[:50]}")
            
            if match_type in ['link', 'form'] and url:
                # Click vào link
                log(f"Click: {url}")
                try:
                    resp = self.session.get(url, headers=self.headers, timeout=15)
                    self.current_page = resp.text
                    ok("Đã vào trang Views!")
                    return True
                except:
                    err("Không vào được trang Views")
                    return False
            elif match_type == 'button':
                # Thử POST với button
                log("Thử click button...")
                return True
        
        # Fallback: Thử các path phổ biến
        common_paths = ['/views', '/service', '/tiktok-views', '/free-views', '/send']
        
        for path in common_paths:
            try:
                url = urljoin(self.base_url, path)
                resp = self.session.get(url, headers=self.headers, timeout=10)
                if resp.status_code == 200 and len(resp.text) > 100:
                    self.current_page = resp.text
                    ok(f"Vào Views qua: {path}")
                    return True
            except:
                continue
        
        warn("Không tìm thấy mục Views riêng, dùng trang chủ")
        return True
    
    def find_and_fill_form(self, tiktok_url):
        """BƯỚC 3: Tìm form trên trang Views và điền link"""
        log("Tìm form gửi link...")
        
        html = self.current_page
        
        # Tìm CSRF token
        csrf = re.search(r'name\s*=\s*["\']_token["\']\s+value\s*=\s*["\']([^"\']+)["\']', html)
        token = csrf.group(1) if csrf else ""
        
        # Tìm form action
        form_action = self.base_url
        form_match = re.search(r'<form[^>]*action\s*=\s*["\']([^"\']*)["\']', html)
        if form_match:
            form_action = urljoin(self.base_url, form_match.group(1)) if form_match.group(1) else self.base_url
        
        # Tìm tất cả input name
        input_names = re.findall(r'<input[^>]*name\s*=\s*["\']([^"\']+)["\']', html)
        
        # Tạo form data
        form_data = {}
        
        # Thêm token
        if token:
            form_data['_token'] = token
        
        # Thêm URL TikTok
        # Tìm key phù hợp cho URL
        url_keys = ['url', 'video_url', 'link', 'tiktok_url', 'page_url', 'input', 'video']
        
        for key in url_keys:
            if key in input_names or key in html.lower():
                form_data[key] = tiktok_url
                ok(f"Dùng key: {key}")
                break
        else:
            # Fallback: dùng key đầu tiên không phải token
            for name in input_names:
                if name not in ['_token', '_method', 'csrf']:
                    form_data[name] = tiktok_url
                    ok(f"Dùng key: {name}")
                    break
            else:
                form_data['url'] = tiktok_url
        
        # Gửi form
        log(f"Gửi đến: {form_action}")
        log(f"Data: {json.dumps(form_data, ensure_ascii=False)[:100]}")
        
        try:
            resp = self.session.post(
                form_action,
                data=form_data,
                headers={
                    **self.headers,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": self.base_url,
                    "Referer": self.base_url + "/",
                },
                timeout=15,
                allow_redirects=True
            )
            
            self.current_page = resp.text
            
            if resp.status_code == 200:
                # Kiểm tra kết quả
                text_lower = resp.text.lower()
                
                # Từ khóa thành công
                if any(w in text_lower for w in ['success', 'sent', 'added', 'complete', 'view', 'queued', 'processing']):
                    return True, "OK - Đã gửi"
                
                # Từ khóa lỗi
                errors = []
                for w in ['error', 'fail', 'invalid', 'wrong', 'expired', 'limit', 'not found']:
                    if w in text_lower:
                        # Trích xuất thông báo lỗi
                        error_match = re.search(rf'{w}[^<]*', text_lower)
                        if error_match:
                            errors.append(error_match.group()[:50])
                
                if errors:
                    return False, '; '.join(errors)
                
                # Không có lỗi -> OK
                return True, "OK"
            
            return False, f"HTTP {resp.status_code}"
            
        except Exception as e:
            return False, str(e)[:40]
    
    def submit(self, tiktok_url):
        """Thực hiện đầy đủ quy trình"""
        # B1: Vào trang chủ
        if not self.connect():
            return False, "Không vào được Zefoy"
        
        # B2: Tìm và click Views
        self.find_views_section()
        
        # B3: Điền form và gửi
        ok_flag, msg = self.find_and_fill_form(tiktok_url)
        
        return ok_flag, msg

# ====================================================
# BOT
# ====================================================
class ZefoyBot:
    def __init__(self):
        self.client = ZefoyClient()
        self.url = ""
        self.running = False
        self.count = 0
        self.success = 0
        self.fail = 0
    
    def submit_once(self):
        ok_flag, msg = self.client.submit(self.url)
        
        if ok_flag:
            ok(msg)
        else:
            err(msg)
        
        return ok_flag
    
    def run_loop(self, delay=60):
        self.running = True
        self.count = 0
        self.success = 0
        self.fail = 0
        
        print(f"\n{B}{Y}{'='*55}{N}")
        print(f"{B}{G}  🎵 ZEFOY v{CURRENT_VERSION} - ĐÚNG THỨ TỰ{N}")
        print(f"{B}{Y}{'='*55}{N}")
        print(f"  Link: {self.url[:50]}...")
        print(f"  Delay: {delay}s")
        print(f"  Flow: Vào Zefoy → Views → Gửi link")
        print(f"{'='*55}\n")
        
        while self.running:
            self.count += 1
            
            print(f"\n{B}┌─ Lần #{self.count} {'─'*42}┐{N}")
            log("B1: Vào Zefoy...")
            log("B2: Tìm Views...")
            log("B3: Gửi link...")
            
            if self.submit_once():
                self.success += 1
            else:
                self.fail += 1
            
            print(f"│ 📊 OK:{G}{self.success}{N} | Fail:{R}{self.fail}{N}")
            print(f"{B}└{'─'*48}┘{N}")
            
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
        print(f"{B}{Y}  🤖 ZEFOY v{CURRENT_VERSION}{N}")
        print(f"{B}{Y}{'='*50}{N}")
        
        if bot.url:
            print(f"  Link: {C}{bot.url[:40]}...{N}")
        
        print(f"  {G}OK:{N} {bot.success} | {R}Fail:{N} {bot.fail} | 🔄 {bot.count}")
        print(f"  Flow: Trang chủ → Views → Gửi link")
        
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
                print(f"\n{Y}Có bản mới: v{update['new']}{N}")
                yn = input(f"Update? (y/n): ").strip().lower()
                if yn == 'y':
                    AutoUpdater.update(update['url'], update['new'])
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

if __name__ == "__main__":
    clear()
    print(f"\n{C}Kiểm tra update...{N}")
    update = AutoUpdater.check()
    if update:
        print(f"{Y}Có bản mới: v{update['new']}{N}")
        yn = input(f"Update? (y/n): ").strip().lower()
        if yn == 'y':
            AutoUpdater.update(update['url'], update['new'])
    else:
        ok(f"v{CURRENT_VERSION} - Mới nhất")
    
    print()
    main()
