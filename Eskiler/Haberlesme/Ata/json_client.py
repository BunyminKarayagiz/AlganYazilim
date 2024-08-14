import socket
import json

telemetri={"takim_numarasi": 4,
 "iha_enlem": 0.0,
 "iha_boylam": 0.0,
 "iha_irtifa": -0.808,
 "iha_dikilme": -22.35449539868347,
 "iha_yonelme": 46.64746337061367,
 "iha_yatis": -1.4423654114208542,
 "iha_hiz": 0.0,
 "iha_batarya": 100,
 "iha_otonom": 0,
 "iha_kilitlenme": 0,
 "hedef_merkez_X": 383,
 "hedef_merkez_Y": 299,
 "hedef_genislik": 26,
 "hedef_yukseklik": 37,
 "gps_saati": {"saat": 0, "dakika": 0, "saniye": 0, "milisaniye": 0}, "mod": "kilitlenme"}

def send_data(client, data):
    json_data = json.dumps(data)
    data_length = len(json_data).to_bytes(64, byteorder='big')
    #SON verisinin uzunluğunu hesaplar ve bu uzunluğu 64 byte uzunluğunda bir bayta dönüştürür. Bu, sunucuya gönderilecek JSON verisinin uzunluğunu belirtir. to_bytes fonksiyonu, belirtilen bayt uzunluğuna dönüşüm yapar.
    client.send(data_length)
    client.send(json_data.encode())
    # JSON verisini sunucuya gönderirken, encode() yöntemini kullanarak JSON verisini byte verisine dönüştürür. Bu, sunucu tarafından alınan verinin doğru bir şekilde çözümlenmesine yardımcı olur


def main():
    SERVER = "10.80.1.94"
    PORT = 5050
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:
        message = input(telemetri)
        if message == "quit":
            send_data(client, DISCONNECT_MESSAGE)
            break
        else:
            send_data(client, message)

    client.close()


if __name__ == "__main__":
    main()
