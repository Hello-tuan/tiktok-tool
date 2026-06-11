import subprocess
import sys
import os
import time
import random
import importlib

# ---------- АВТОУСТАНОВКА И ПРОВЕРКА ЗАВИСИМОСТЕЙ ----------
REQUIRED_LIBRARIES = ["selenium"]

def check_and_install_libraries():
    """Проверяет наличие библиотек, устанавливает отсутствующие."""
    for lib in REQUIRED_LIBRARIES:
        try:
            importlib.import_module(lib)
            print(f"[OK] {lib} уже установлена")
        except ImportError:
            print(f"[УСТАНОВКА] {lib} не найдена, устанавливаю...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"[OK] {lib} установлена")

check_and_install_libraries()

# Импорт после проверки
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ---------- КОНФИГУРАЦИЯ ----------
ACCOUNTS_FILE = "tkig.txt"
GOLIKE_LOGIN_URL = "https://app.golike.net/"
MANAGER_URL = "https://app.golike.net/account/manager/instagram"
DELAY_BETWEEN_ACCOUNTS = (15, 30)
DELAY_AFTER_ADD = (5, 10)

def read_accounts(file_path):
    accounts = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and ":" in line:
                login, pwd = line.split(":", 1)
                accounts.append({"login": login.strip(), "password": pwd.strip()})
    return accounts

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def login_golike(driver, username, password):
    driver.get(GOLIKE_LOGIN_URL)
    time.sleep(3)
    user_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[placeholder*='tên đăng nhập'], input[placeholder*='username']"))
    )
    user_input.clear()
    user_input.send_keys(username)
    pwd_input = driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[type='password']")
    pwd_input.clear()
    pwd_input.send_keys(password)
    login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Đăng nhập')")
    login_btn.click()
    time.sleep(5)
    return "account" in driver.current_url or "manager" in driver.current_url

def go_to_manager(driver):
    driver.get(MANAGER_URL)
    time.sleep(5)
    return "instagram" in driver.current_url

def click_add_account_button(driver):
    try:
        btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'THÊM', 'thêm'), 'thêm')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        return True
    except:
        return False

def fill_instagram_account(driver, acc):
    login_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='instagram' i][type='text'], input[name='username']"))
    )
    login_field.clear()
    login_field.send_keys(acc["login"])
    pwd_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    pwd_field.clear()
    pwd_field.send_keys(acc["password"])
    save_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'LƯU', 'lưu'), 'lưu') or contains(translate(text(), 'THÊM', 'thêm'), 'thêm')]")
    save_btn.click()
    time.sleep(2)
    return True

def main():
    GOLIKE_USER = "your_golike_username"
    GOLIKE_PASS = "your_golike_password"

    print("=== ПРОВЕРКА ЗАВИСИМОСТЕЙ ВЫПОЛНЕНА ===")
    accounts = read_accounts(ACCOUNTS_FILE)
    if not accounts:
        print("Нет аккаунтов в tkig.txt")
        return

    driver = setup_driver()
    try:
        print("Выполняется вход в golike.net...")
        if not login_golike(driver, GOLIKE_USER, GOLIKE_PASS):
            print("Ошибка авторизации")
            return
        print("Вход выполнен")
        if not go_to_manager(driver):
            print("Не удалось открыть менеджер")
            return
        for idx, acc in enumerate(accounts):
            print(f"Добавление {idx+1}/{len(accounts)}: {acc['login']}")
            if not click_add_account_button(driver):
                print("Кнопка добавления не найдена")
                continue
            time.sleep(random.uniform(2, 4))
            fill_instagram_account(driver, acc)
            print(f"Отправлен: {acc['login']}")
            time.sleep(random.uniform(*DELAY_AFTER_ADD))
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, ".modal .close, button[aria-label='Close']")
                close_btn.click()
            except:
                pass
            time.sleep(random.uniform(*DELAY_BETWEEN_ACCOUNTS))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
