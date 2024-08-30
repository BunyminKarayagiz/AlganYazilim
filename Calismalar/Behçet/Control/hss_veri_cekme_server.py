# Hava Savunma Sistemi Kontrol

import time
import requests
from colorama import Fore, init

init(autoreset=True)

server_url = "http://127.0.0.1:5000/api/activation"

def check_activation_status():
    try:
        response = requests.get(server_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "active":
                print(Fore.GREEN + "Hava savunma sistemi aktif edildi.")
            else:
                print(Fore.YELLOW + "Hava savunma sistemi pasif durumda.")
        else:
            print(Fore.RED + f"Sunucudan geçersiz yanıt alındı: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Sunucuyla bağlantı sırasında bir hata oluştu: {e}")

while True:
    check_activation_status()
    time.sleep(10)  # 10 saniyede bir durumu kontrol et