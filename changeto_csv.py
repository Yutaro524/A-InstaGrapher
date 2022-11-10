import os
import csv
import openpyxl
from natsort import natsorted


# visualizationに作った任意のフォルダ名称

folder_path = "suisituxls/北海道"
folder_2_path = "suisitucsv"


# # 定数
# visualization_path = "/suisitu"
# folder_path = os.path.join(visualization_path, folder_name)
# folder_2_path = os.path.join(visualization_path, folder_name)


# Excelファイル名リストを自然順で取得
files = natsorted(os.listdir(folder_path))
            
#ファイル名リストをfor文でまわして各ファイルの絶対パスを構築
for filename in files:
    if not filename.endswith('.xlsx'):
        continue
    filepath = os.path.join(folder_path, filename)

    # xlsxファイルにアクセス→先頭シートのオブジェクトを取得
    wb = openpyxl.load_workbook(filepath)
    ws_name = wb.sheetnames[0]
    ws = wb[ws_name]

    # csvに変換して、folder2に保存
    savecsv_path = os.path.join(folder_2_path, filename.rstrip(".xlsx")+".csv")
    with open(savecsv_path, 'w', newline="") as csvfile:
        writer = csv.writer(csvfile)
        for row in ws.rows:
            writer.writerow([cell.value for cell in row])

