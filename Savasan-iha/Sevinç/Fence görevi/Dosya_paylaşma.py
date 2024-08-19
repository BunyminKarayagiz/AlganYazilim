import os
import shutil

dosya = r'C:\Users\svnck\Desktop\Algan\Yazılım\AlganYazılım\Savasan-iha\Sevinç\Fence görevi\waypoints.waypoints'
hedef_klasor = r'\\ALPEREN\123'
hedef_dosya = os.path.join(hedef_klasor, os.path.basename(dosya))


try:
    shutil.copy2(dosya, hedef_dosya)
    print(f"Dosya başarıyla kopyalandı: {hedef_dosya}")
except Exception as e:
    print(f"Dosya kopyalama işlemi başarısız: {e}")
