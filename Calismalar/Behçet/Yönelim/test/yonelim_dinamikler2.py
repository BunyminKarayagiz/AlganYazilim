from geopy.distance import geodesic
import numpy as np

referans_konum = [35.3652733, 149.1722989]

def nokta_hesapla(konum):
    y_ussu = (konum[0], referans_konum[1])
    x_ussu = (referans_konum[0], konum[1])

    y_mesafe = geodesic(y_ussu, referans_konum).meters
    x_mesafe = geodesic(x_ussu, referans_konum).meters
    
    # x'i negatif yapmak için boylamının home boylamından küçük olması gerekir
    if konum[1] < referans_konum[1]:
        x_mesafe *= -1

    # y'i negatif yapmak için enlemi home enleminin altında olması gerekir
    if konum[0] < referans_konum[0]:
        y_mesafe *= -1

    nokta = (x_mesafe, y_mesafe, konum[2])

    return nokta 

konum = [35.3662733, 149.1732989, 100]  # Enlem, boylam, yükseklik
sonuc = nokta_hesapla(konum)
print(sonuc)