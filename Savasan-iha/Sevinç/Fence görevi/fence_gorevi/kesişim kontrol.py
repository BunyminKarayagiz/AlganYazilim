from fonksiyonlar import *

nokta1=(148.57652, 588.80945)
nokta2= (508.71109, 503.06313)
nokta3=(687.82564, 268.68984)
nokta4=(586.83552, 7.63991)
nokta5= (60.92473, 106.72456)
nokta6=(-142.96098, 358.24711)
nokta7=(-89.60771, 529.73976)


fence1= (342.93486, 579.28208, 100)
fence2=(678.29827, -28.56409,250)

noktalar=[nokta1,nokta2,nokta3,nokta4,nokta5,nokta6,nokta7]
fenceler=[fence1,fence2]
for nokta in noktalar:
    try:
        sonraki_nokta= noktalar[noktalar.index(nokta)+1]
    except IndexError:
        sonraki_nokta=noktalar[0]
    for fence in fenceler:
        if kesisim_kontrol(sonraki_nokta,nokta,fence):
            print(f"Nokta: {nokta} ile {fence} arasında kesişim var.")
        else:
            print(f"Nokta: {nokta} ile {fence} arasında kesişim yok.")