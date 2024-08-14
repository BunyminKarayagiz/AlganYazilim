import path
import argparse
import openpyxl
import time

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
args = parser.parse_args()
connection_string = args.connect
iha = path.Plane(connection_string)
dosya = openpyxl.load_workbook("./123.xlsx")
sayfa = dosya["Sheet1"]
row = 2
column = 1
while True:
    try:
        iha_enlem = float("{:.7f}".format(iha.pos_lat))
        iha_boylam = float("{:.7f}".format(iha.pos_lon))
        iha_irtifa = float("{:.2f}".format(iha.pos_alt_rel))
        iha_dikilme = float("{:.2f}".format(iha.att_pitch_deg))
        iha_yonelme = float("{:.2f}".format(iha.att_heading_deg))
        iha_yatis = float("{:.2f}".format(iha.att_roll_deg))
        iha_hiz = float("{:.2f}".format(iha.groundspeed))
        iha_batarya = iha.get_battery()
        mesaj = [iha_enlem, iha_boylam, iha_irtifa, iha_dikilme, iha_yonelme, iha_yatis, iha_hiz, iha_batarya]
        while True:
            for i in range(1, 9):
                sayfa.cell(row=row, column=i, value=mesaj[i - 1])
            break
        row += 1
        time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        dosya.save("./123.xlsx")
