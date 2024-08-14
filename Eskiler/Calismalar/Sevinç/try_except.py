"""TRY EXCEPT BLOKLARI
- bu ifadeler hata yakalamak için kullanılır.
try:
    a=3
    b=0
    c=a/b
    d=x
    isim='Ali'
    karakter = isim[10]
    list=[ 1,2,3]
    karakter=isim[10]
except NameError:
    print("Bu değişken daha önce tanımlanmamış.")
except IndexError:
    print("Böyle bir indeks bulunmuyor")
except ZeroDivisionError:
    print("Payda sıfır olmamalı")
except Exception:
    print("Bilinmeyen bir hata oluştu.")

else:
    print("Else bloğu çalışıyor")

finally:
    print("finnaly bloğu çalışıyor")
except bloğu bir hata olduğunda çalışır. Biz içine hata türünü yazarsak o hata olduğu zaman onun içinde olan kodlar çalışır. Burada üstte olduğu gibi hataya özel olarak kodların çalışmasını sağlayabildiğimiz gibi hatanın ne olduğu fark etmeksizin herhangi bir hata yakalandığında except: ifadesini kullanabiliriz.
Yukarıdaki except Exception: ifadesi yukarıda yazılmış olan hataların dışında bir hata çalıştığında çalışır.
Else bloğu except blokları çalışmadığı zaman yani herhangi bir hata alınmadığı zaman çalışır.
Finally bloğu: Hata alınsa da alınmasa da çalışır.
RAİSE
try:
    a=3
    b=0
    if b==0:
        raise ZeroDivisionError
    c=a/b
    d=x
    isim='Ali'
    karakter = isim[10]
    list=[1,2,3]
    karakter=isim[10]

except NameError:
    print("Bu değişken daha önce tanımlanmamış.")
except IndexError:
    print("Böyle bir indeks bulunmuyor")
except ZeroDivisionError:
    print("Payda sıfır olmamalı")
except Exception:
    print("Bilinmeyen bir hata oluştu.")

else:
    print("Else bloğu çalışıyor")

finally:
    print("finnaly bloğu çalışıyor")
buradaki raise ifadesi direkt olarak o hatanın olduğu bloktaki kodların çalıştırılmasını sağlar.
Biz bu kodu çalıştırdığımızda birkaç hata olmasına rağmen ilk takıldığı yerdeki hatayı yazdırıp duracak ve birkaç tane hata varsa diğerlerini görmeyeceğiz veya çok önemsiz bşr hata ve programın durmasına sebep olacak
Bunun için  pass ekleyip devam etmesini sağlayabiliriz.
"""