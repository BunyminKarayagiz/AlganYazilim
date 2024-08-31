import time
import socket
from datetime import datetime
from colorama import Fore, init

class AirDefenseSystem:
    def __init__(self, latitude, longitude, activation_interval, active_duration):
        self.latitude = latitude
        self.longitude = longitude
        self.activation_interval = activation_interval
        self.active_duration = active_duration
        self.host = '127.0.0.1'
        self.port = 65432
        init(autoreset=True)
    
    def send_status(self, status, max_retries=5, delay=1):
        retries= 0
        while retries < max_retries:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    message = f"{status},{self.latitude},{self.longitude},{datetime.now().isoformat()}"
                    s.sendall(message.encode('utf-8'))
                    print("Status sent succesfully.")
                    return
            except (socket.timeout, socket.error) as e:
                print(f'Connection failed {e}. Retrying in {delay} seconds...')
                retries += 1
                time.sleep(delay)

    def run(self):
        while True:
            time.sleep(self.activation_interval)
            print(Fore.GREEN + f"Hava savunma sistemi aktif oldu: {datetime.now().isoformat()}")
            self.send_status("active")
            time.sleep(self.active_duration)
            print(Fore.RED + f"Hava savunma sistemi pasif oldu: {datetime.now().isoformat()}")
            self.send_status("inactive")

if __name__ == "__main__":
    system = AirDefenseSystem(latitude=40.7128, longitude=-74.0060, activation_interval=2, active_duration=2)
    system.run()