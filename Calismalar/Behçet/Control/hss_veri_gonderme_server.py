# İstemci

import time
import requests
from datetime import datetime
from colorama import Fore, init

latitude = 40.7128
longitude = -74.0060 

activation_interval = 10
active_duration = 10

init(autoreset=True)

server_url = "http://127.0.0.1:5000/api/activation"

def send_activation_message(status, latitude, longitude, active_duration=None):

    message = {
        "status": status,
        "latitude": latitude,
        "longitude": longitude,
        "activation_time": datetime.now().isoformat()
    }
    
    if active_duration is not None:
        message["active_duration"] = active_duration

    try:
        response = requests.post(server_url, json=message)
        # server_url adresine bir post isteği gönderir. response sunucudan gelen verileri saklar
        if response.status_code == 200:
            print(f"Mesaj başarıyla gönderildi: {response.json()}")
        else:
            print(f"Mesaj gönderme başarısız: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"İstek gönderirken bir hata oluştu: {e}")

while True:
    time.sleep(activation_interval)

    print(Fore.GREEN + f"Hava savunma sistemi aktif oldu: {datetime.now().isoformat()}")

    send_activation_message("active", latitude, longitude, active_duration)

    time.sleep(active_duration)

    print(Fore.RED + f"Hava savunma sistemi pasif oldu: {datetime.now().isoformat()}")

    send_activation_message("inactive", latitude, longitude, activation_interval)