import requests
from flask import json


class sunucuApi():

    def __init__(self, url):
        self.url = url
        self.ses = requests.Session()

    def get_hava_savunma_coord(self):
        self.hss_koordinat = self.ses.get(self.url + '/api/hss_koordinatlari')
        return self.hss_koordinat.status_code, self.hss_koordinat.text

    def sunucuya_giris(self, kadi, sifre):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.giris = {
            "kadi": kadi, "sifre": sifre}

        self.gidecek = json.dumps(self.giris)

        self.giden = self.ses.post(self.url + '/api/giris', self.gidecek, headers=self.headers)

        return self.giden.status_code, self.giden.text

    def sunucuya_postala(self, mesaj):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.mesaj = json.dumps(mesaj)
        self.rakip = self.ses.post(self.url + '/api/telemetri_gonder', self.mesaj, headers=self.headers)

        return self.rakip.status_code, self.rakip.text

    def sunucu_saati_al(self):
        self.sunucu_saati = self.ses.get(self.url + '/api/sunucusaati')

        return self.sunucu_saati.status_code, self.sunucu_saati.text

    def kilitlenme_postala(self, mesaj):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.mesaj = json.dumps(mesaj)
        print(self.mesaj)
        try:
            self.kilit = self.ses.post(self.url + '/api/kilitlenme_bilgisi', self.mesaj, headers=self.headers)
        except Exception as err:
            print(f"There is an error in \"haberlesme, kilitlenme_postala\" with: {err}")
        return self.kilit.status_code

    def kamikaze_gonder(self, mesaj):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        # mesaj=mesaj.decode("utf-8")
        self.mesaj = json.dumps(mesaj)
        print(self.mesaj)
        self.kamikaze = self.ses.post(self.url + '/api/kamikaze_bilgisi', self.mesaj, headers=self.headers)

        return self.kamikaze.status_code

    def qr_koordinat_al(self):
        self.qr_koordinat = self.ses.get(self.url + '/api/qr_koordinati')
        return self.qr_koordinat.status_code, self.qr_koordinat.text

    def sunucudan_cikis(self):
        self.durum = self.ses.get(self.url + '/api/cikis')
        return self.durum
