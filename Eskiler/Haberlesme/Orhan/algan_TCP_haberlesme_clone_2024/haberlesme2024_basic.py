import socket
import json, requests


class server_TCP:
    ses = requests.Session()

    def __init__(self):
        super(server_TCP, self).__init__()
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connected(self, host, port):
        self.skt.bind((host, port))
        self.skt.listen()
        print("listening...")
        self.conn, self.addr = self.skt.accept()
        print('connected to:', self.addr)
        return self.conn

    def send_telemetry(self, package):
        package = json.dumps(package)
        self.conn.send(package.encode("utf-8"))

    def get_telemetry(self):
        response = self.conn.recv(512)
        result = json.dumps(response.decode("utf-8"))
        result = json.loads(result)
        return result

    def enter_server(self, url, kadi, sifre):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        enter = {
            "kadi": kadi, "sifre": sifre}

        sending = json.dumps(enter)
        print(sending)

        sent = server_TCP.ses.post(url + '/api/giris', sending, headers=headers)

        return sent.status_code, sent.text

    def post_to_server(self, url, package):
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        package = json.dumps(package)
        rakip = server_TCP.ses.post(url + '/api/telemetri_gonder', package, headers=headers)
        return rakip.status_code, rakip.text

    def get_servertime(self, url):
        servertime = server_TCP.ses.get(url + '/api/sunucusaati')

        return servertime.status_code, servertime.text

    def get_qr_coordinate(self, url):
        qr_coordinate = server_TCP.ses.get(url + '/api/qr_koordinati')
        return qr_coordinate.status_code, qr_coordinate.text


class client_TCP:
    def __init__(self):
        super(client_TCP, self).__init__()
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connected(self, host, port):
        self.skt.connect((host, port))
        return self.skt

    def send_telemetry(self, package):
        package = json.dumps(package)
        self.skt.sendall(package.encode("utf-8"))

    def get_telemetry(self):
        response = self.skt.recv(2048)
        result = json.dumps(response.decode("utf-8"))
        result = json.loads(result)
        return result

