from dbr import BarcodeReader
from dbr import *
import cv2


class QR_Detection:
    def __init__(self):
        self.license_key = "DLC2TdMdmL9ZvN620g//F4iSiRzjtjjLkjT3d0OCuvqDeA3i4W4Ng5HA1sMKbB3Nwe3xlSDeD22uWy6Oj1C9wvdCV3aT9WS0VGcfu41ibk96+cYwsDp26UaZfjGzMa7yPmt5VweXkmHkLVR3v3bpS3sh5SFHJCUKKkjP+ffkX1QdTpuMov9hEMNXk21h/yOLtoEB4Goz4D/dGG6goUb7NfS7OSYhSReEnB/O1keBRjaothIADoIPwEU9QRVoCbubGJwTJ6nsQC8Hst5vIkuTjxExPSieX8ld0lLCyHUe4tCtpD2H6xSUPHl2XHWWp7GBn9/T3y6zr2h8dAuX6tGjw95rXNxe62Y7sAeZeMUVrDVp2PEVQzj4AB1Q1pUNjmAcd9p55KYn5fK1B8IEDTcEHR3IRbHBRNlGKUHld/jN5EtYTY6Y8cO5Y8lYWPBcuqSVnnLQ+LUewnupLecxkYHjoNzFYGGAfAUsZYS8F3DWsbMCy/+euUOa"
        BarcodeReader.init_license(self.license_key)
        self.image_path = "temp_frame.jpg"

    def decode_data_matrix(self):
        reader = BarcodeReader()
        try:
            # Resmi okuyun ve sonuçları alın
            results = reader.decode_file(self.image_path)

            # Sonuçlar boş değilse, her bir sonucu yazdırın
            if results:
                for result in results:
                    #print("Tespit edilen barkod: " + result.barcode_text)
                    return result.barcode_text
            """else:
                print("Barkod bulunamadı.")"""
        except Exception as e:
            print("Hata: " + str(e))
        finally:
            # Okuyucuyu kapatın
            del reader

    def file_operations(self, frame):
        # Frame'i geçici bir dosyaya kaydedin
        cv2.imwrite(self.image_path, frame)

        # Barkodları tespit etmek için decode_data_matrix fonksiyonunu çağırın
        qr_bilgisi = self.decode_data_matrix()

        # Geçici dosyayı silin
        os.remove(self.image_path)
        return qr_bilgisi

"""if __name__ == "__main__":

    qrd = QR_Detection()
    # Webcam'i başlatın
    cap = cv2.VideoCapture(0)

    while True:
        # Frame alır
        ret, frame = cap.read()

        qrd.file_operations(frame=frame)
        # Alınan frame'i gösterin
        cv2.imshow("Webcam", frame)

        # 'q' tuşuna basıldığında döngüden çıkın
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Çıkış yaparken kamera bağlantısını serbest bırakın ve pencereleri kapatın
    cap.release()
    cv2.destroyAllWindows()
"""