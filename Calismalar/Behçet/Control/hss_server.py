# Flask Sunucu

from flask import Flask, request, jsonify
from colorama import Fore, init

init(autoreset=True)

app = Flask(__name__)


# Bu, endpoint'in URL yoludur. Web tarayıcınızda veya başka bir istemcide bu URL'ye bir istek yapıldığında, 
# Flask bu isteği işler ve bu endpoint'e bağlı olan işlevi (bu durumda activation fonksiyonu) çağırır.

# Bu, bu endpoint'in hangi HTTP metodunu kabul edeceğini belirtir. Bu örnekte, yalnızca POST isteği kabul edilmektedir. 
# Yani, bu endpoint'e sadece POST istekleri yapıldığında activation fonksiyonu çalıştırılır.


@app.route('/api/activation', methods=['POST', 'GET'])
def activation():
    # Bu fonksiyon, /api/activation endpoint'ine yapılacak HTTP POST istekleri için çağrılır.

    data = request.get_json() # Gelen JSON formatındaki verileri alır 

    if not data:
        return jsonify({"error": "Geçersiz veri formati"}), 400

    print(Fore.GREEN + f"Hava savunma sistemi mesaji alindi: {data}")

    return jsonify({"status": "Mesaj alindi"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
