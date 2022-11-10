import pyexcel as p
import glob

def convert_xls_to_xlsx():
    it = glob.glob('suisituxls/北海道/*.xls')
    for xls in it:
        xlsx = "{}".format(xls) + "x"
        print(xlsx)
        p.save_book_as(file_name='{}'.format(xls), dest_file_name='{}'.format(xlsx))

convert_xls_to_xlsx()
