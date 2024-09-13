# ALGAN Takımı tarafından oluturulan basit test sunucu API dosyası
import datetime
import random
import flask
from flask import jsonify, request
import json
from termcolor import colored, cprint

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
                "hssYaricap": 300
            }
            # {
            #     "id": 1,
            #     "hssEnlem": 40.23351019,
            #     "hssBoylam": 28.99976492,
            #     "hssYaricap": 50
            # },
            # {
            #     "id": 2,
            #     "hssEnlem": 40.23105297,
            #     "hssBoylam": 29.00744677,
            #     "hssYaricap": 75
            # },
            # {
            #     "id": 3,
            #     "hssEnlem": 40.23090554,
            #     "hssBoylam": 29.00221109,
            #     "hssYaricap": 150
            # }
        ]
    }
    
    return jsonify(hava_savunma_sistemleri)
def durum(cls, kod):
    if kod == 200:
        return "İstek baarili"
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
    "qrEnlem": -35.3549662,
    "qrBoylam": 149.1613770
}
#girisveri = [{"kadi": "algan", "sifre": "53SnwjQ2sQ"}
girisveri = [{"kadi": "algan", "sifre": "Ea5ngUqWYV"},{"kadi": "rakip2", "sifre": "rakip2"},{"kadi": "rakip3", "sifre": "rakip3"},
             {"kadi": "rakip4", "sifre": "rakip4"},{"kadi": "rakip5", "sifre": "rakip5"}]
veri1=[{
    "takim_numarasi": 1,
    "iha_enlem": 0.0,
    "iha_boylam": 0.0,
    "iha_irtifa": 0,
    "iha_dikilme": 0,
    "iha_yonelme": 0,
    "iha_yatis": 0,
    "iha_hiz":0,
    "zaman_farki": 0
}]

veri2=[{
    "takim_numarasi": 2,
    "iha_enlem": 0,
    "iha_boylam": 0,
    "iha_irtifa": 0,
    "iha_dikilme": 0,
    "iha_yonelme": 100,
    "iha_yatis": 100,
    "iha_hiz":0,
    "zaman_farki": 0
}]

veri3=[{
    "takim_numarasi": 3,
    "iha_enlem": 0.0,
    "iha_boylam": 0.0,
    "iha_irtifa": 0,
    "iha_dikilme": 0,
    "iha_yonelme": 200,
    "iha_yatis": 200,
    "iha_hiz":0,
    "zaman_farki": 0
}]

veri4=[{
    "takim_numarasi": 4,
    "iha_enlem": -35.1913461,
    "iha_boylam": 149.1680717,
    "iha_irtifa": 0,
    "iha_dikilme": 0,
    "iha_yonelme": 300,
    "iha_yatis": 300,
    "iha_hiz":0,
    "zaman_farki": 0
}]

veri5=[{
    "takim_numarasi": 5,
    "iha_enlem": 0.0,
    "iha_boylam": 0.0,
    "iha_irtifa": 0,
    "iha_dikilme": 0,
    "iha_yonelme": 0,
    "iha_yatis": 0,
    "iha_hiz":0,
    "zaman_farki": 0
}]

@app.route('/api/giris', methods=["POST"])
def giris():
    # gelen deikeni kullanıcı adını ve sifreyi döndürüyor.
    gelen = json.loads(request.data)
    if gelen in girisveri:
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
    if gelen["takim_numarasi"] == 1:
        veri1.append(gelen)
    elif gelen["takim_numarasi"] == 2:
        veri2.append(gelen)
    elif gelen["takim_numarasi"] == 3:
        veri3.append(gelen)
    elif gelen["takim_numarasi"] == 4:
        veri4.append(gelen)
    elif gelen["takim_numarasi"] == 5:
        veri5.append(gelen)

    gelenveri = {
        "sunucusaati": {
            "gun": 13,
            "saat": 11,
            "dakika": 38,
            "saniye": 38,
            "milisaniye": 739
        },
        "konumBilgileri": [
            veri1[-1],
            veri2[-1],
            veri3[-1],
            veri4[-1],
            veri5[-1]
        ]
    }  # Test verileri
    print(gelenveri)
    return jsonify(gelenveri)


@app.route('/api/kilitlenme_bilgisi', methods=["POST"])
def kilit():
    gelen = json.loads(request.data)
    cprint(gelen,"red","on_white",attrs=["bold"]) #TODO EKLENECEK...
    return jsonify(gelen)


@app.route('/api/kamikaze_bilgisi', methods=["POST"])
def kamikaze():
    gelen = json.loads(request.data)
    cprint(gelen,"red","on_white",attrs=["bold"]) #TODO EKLENECEK...
    return jsonify(gelen)


"""@app.route('/api/giris', methods=["POST"])
def giris():
    pass"""


@app.route('/api/cikis', methods=["GET"])
def cikis():
    return "200"


app.run(host='10.0.0.123', port=10001, debug=True, threaded=True)
