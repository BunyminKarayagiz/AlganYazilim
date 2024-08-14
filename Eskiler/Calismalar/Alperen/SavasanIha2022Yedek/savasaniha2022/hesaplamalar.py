import time

from vincenty import vincenty


def yonver(centerx, centery, widthScreen, heightScreen,irtifa):
    cnt = list([widthScreen / 2, heightScreen / 2])

    ktsyX = int((centerx - cnt[0]))
    ktsyY = int((centery - cnt[1])*1.5)

    yatay=1500
    dikey=1500

    # if 80 < irtifa < 150:
    #     yatay = 1500 + ktsyX
    #     dikey = 1500 - ktsyY
    # elif irtifa < 80:
    #     dikey+=100
    #     yatay=1500
    # elif irtifa > 150:
    #     dikey-=200
    #     yatay=1500
    yatay = 1500 + ktsyX
    dikey = 1500 + ktsyY
    return yatay, dikey

def hizayarla(airspeed,pwm,hedefwidth, hedefheight):
    alan = hedefwidth * hedefheight
    yeni_hiz = pwm
    if 4500 < alan < 9600:
        if 16 < airspeed < 22:
            yeni_hiz = pwm
        elif airspeed < 16:
            yeni_hiz += 5
        else:
            yeni_hiz -= 5
    elif alan > 9600:
        if 16 < airspeed < 22:
            ivme = airspeed - 16
            yeni_hiz -= ivme * 1.2
        elif airspeed < 16:
            yeni_hiz += 5
        else:
            yeni_hiz -= 5
    else:
        if 16 < airspeed < 22:
            ivme = 22 - airspeed
            yeni_hiz += ivme * 1.2
        elif airspeed < 16:
            yeni_hiz += 5
        else:
            yeni_hiz -= 5

    if yeni_hiz <= 1200:
        yeni_hiz = 1200
    elif yeni_hiz >= 1800:
        yeni_hiz = 1800
    return yeni_hiz, alan

def mesafe_hesapla(iha,rakip):
    mesafe = vincenty((iha[0],iha[1]),(rakip[0],rakip[1]))
    return mesafe
def en_uzak(algan_iha,rakip):
    en_uzak_iha = None
    en_uzak_mesafe = None
    for iha in rakip:
        if iha[2] < 150 and iha[2] > 40:
            mesafe = mesafe_hesapla(algan_iha,iha)
            if en_uzak_iha is None or en_uzak_mesafe < mesafe:
                en_uzak_iha = iha
                en_uzak_mesafe = mesafe
    return en_uzak_iha


