# ALGAN Takımı tarafından oluşturulan basit test sunucu API dosyası
import datetime
import random
import flask
from flask import jsonify, request
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True



@app.route('/api/hss_koordinatlari', methods=["GET"])
def get_hss_coord():
    hava_savunma_sistemleri = {
        "sunucusaati": {
            "gun": 19,
            "saat": 15,
            "dakika": 51,
            "saniye": 43,
            "milisaniye": 775
        },
        "hss_koordinat_bilgileri": [
            {
                "id": 0,
                "hssEnlem": 40.23260922,
                "hssBoylam": 29.00573015,
                "hssYaricap": 50
            },
            {
                "id": 1,
                "hssEnlem": 40.23351019,
                "hssBoylam": 28.99976492,
                "hssYaricap": 50
            },
            {
                "id": 2,
                "hssEnlem": 40.23105297,
                "hssBoylam": 29.00744677,
                "hssYaricap": 75
            },
            {
                "id": 3,
                "hssEnlem": 40.23090554,
                "hssBoylam": 29.00221109,
                "hssYaricap": 150
            }
        ]
    }
    return jsonify(hava_savunma_sistemleri)
def durum(cls, kod):
    if kod == 200:
        return "İstek başarılı"
    elif kod == 204:
        return "Gonderilen paketin Formati Yanlis"
    elif kod == 400:
        return "Istek hatali veya gecersiz."
    elif kod == 401:
        return "Kimliksiz erisim denemesi. Oturum acmaniz gerekmektedir."
    elif kod == 403:
        return "Yetkisiz erisim denemesi."
    elif kod == 404:
        return "Gecersiz URL."
    elif kod == 500:
        return "Sunucu ici hata."


sunucusaati = {"saat": datetime.datetime.now().hour,
               "dakika": datetime.datetime.now().minute,
               "saniye": datetime.datetime.now().second,
               "milisaniye": datetime.datetime.now().microsecond * 1000
               }  # Test verileri

qr_koordinati = {
    "qrEnlem": -35.3545987,
    "qrBoylam": 149.1547465
}

girisveri = {"kadi": "algan", "sifre": "53SnwjQ2sQ"}


@app.route('/api/giris', methods=["POST"])
def giris():
    # gelen değişkeni kullanıcı adını ve sifreyi döndürüyor.
    gelen = json.loads(request.data)
    if girisveri == gelen:
        print(gelen["kadi"].upper() + " Giris Yapti")
        return "200"
    else:
        print("basarisiz giris")
        return "403"


@app.route('/api/sunucusaati', methods=["GET"])
def getData():
    sunucusaati = {"saat": datetime.datetime.now().hour,
                   "dakika": datetime.datetime.now().minute,
                   "saniye": datetime.datetime.now().second,
                   "milisaniye": datetime.datetime.now().microsecond // 1000
                   }

    return jsonify(sunucusaati)


@app.route('/api/qr_koordinati', methods=["GET"])
def getqrData():
    return jsonify(qr_koordinati)




@app.route('/api/telemetri_gonder', methods=["POST"])
def tele():
    gelen = json.loads(request.data)
    print(gelen)
    gelenveri = {
        "sistemSaati": {
            "saat": 6,
            "dakika": 53,
            "saniye": 42,
            "milisaniye": 500
        },
        "konumBilgileri": [
            {
                "takim_numarasi": 1,
                "iha_enlem": -35.1864710,
                "iha_boylam": 149.1420221,
                "iha_irtifa": 50,
                "iha_dikilme": 5,
                "iha_yonelme": 40,
                "iha_yatis": 0,
                "iha_hiz":0,
                "zaman_farki": 93
            },
            {
                "takim_numarasi": 2,
                "iha_enlem": -35.1827881,
                "iha_boylam": 149.1362715,
                "iha_irtifa": 60,
                "iha_dikilme": 5,
                "iha_yonelme": 256,
                "iha_yatis": 0,
                "iha_hiz":0,
                "zaman_farki": 74
            },
            {
                "takim_numarasi": 3,
                "iha_enlem": -35.1939238,
                "iha_boylam": 149.1358852,
                "iha_irtifa": 70,
                "iha_dikilme": 5,
                "iha_yonelme": 256,
                "iha_yatis": 0,
                "iha_hiz":0,
                "zaman_farki": 43
            }
        ]
    }  # Test verileri
    return jsonify(gelenveri)


@app.route('/api/kilitlenme_bilgisi', methods=["POST"])
def kilit():
    gelen = json.loads(request.data)
    print(gelen)
    return jsonify(gelen)


@app.route('/api/kamikaze_bilgisi', methods=["POST"])
def kamikaze():
    gelen = json.loads(request.data)
    print(gelen)
    return jsonify(gelen)


"""@app.route('/api/giris', methods=["POST"])
def giris():
    pass"""


@app.route('/api/cikis', methods=["GET"])
def cikis():
    return "200"


app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
