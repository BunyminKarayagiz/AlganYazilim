from vincenty import vincenty
import numpy as np

referans_konum = [35.3652733, 149.1722989]

def nokta_hesapla(konum):
    i=konum
    y_ussu = (i[0], referans_konum[1])
    x_ussu = (referans_konum[0], i[1])

    y_mesafe = vincenty(y_ussu, referans_konum)
    x_mesafe = vincenty(x_ussu, referans_konum)
    # x i negatif yapmak için  boylamının home boylamından küçük olması gerekir

    if i[1] < referans_konum[1]:
        x_mesafe = x_mesafe * -1000
    else:
        x_mesafe = x_mesafe * 1000
    # y i negatif yapmak için enlemi home enleminin altında olması gerekir

    if i[0] < referans_konum[0]:
        y_mesafe = y_mesafe * -1000
    else:
        y_mesafe = y_mesafe * 1000
    nokta = (x_mesafe, y_mesafe, i[2])

    return nokta 

konum = [35.3662733, 149.1732989, 100]  # Enlem, boylam, yükseklik
sonuc = nokta_hesapla(konum)
print(sonuc)