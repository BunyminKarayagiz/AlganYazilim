
import openpyxl
dosya=openpyxl.load_workbook("./data.xlsx")
sayfa=dosya["notlar"]
sayfa.cell(row=1, column=4, value="ortalama")

dosya.save("./data.xlsx")