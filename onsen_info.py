import requests
from bs4 import BeautifulSoup
import pandas
import time
import re
from urllib import request, parse
import numpy as np

# スクレイピングを行い、必要な情報をDataFrameとして出力する関数
def get_items(url, df, columns):
    res = requests.get(url)
    res_text = res.text
    soup = BeautifulSoup(res_text, 'html.parser')
    ret = soup.find_all("tr")
    ret.pop(0)
    for item in ret:
        prefecture = item.select("td.kn > a")[0].text
        name = item.select("td.sn > a")[0].text
        onsen_url = item.select("td.sn")[0].find("a").get("href")
        city, lv01Nm, latitude, longitude = get_city(onsen_url)
        try:
            links = item.select("td.hp")[0]
            link = links.find("a").get("href")
        except IndexError:
            link = "なし"
        tanjun, enka, tansan, iou, housya, ryusan, sansei, gantetsu, nisan, youso = def_kounou(item)
        try:
            hyoka = item.select_one("td.rt").text
        except AttributeError:
            hyoka = "なし"
        try:
            comi = item.select_one("td.rc").text
        except AttributeError:
            comi = "不明"
        try:
            yado = item.select_one("td.tl").text
        except AttributeError:
            yado = "不明"
        try:
            onsen_num = item.select_one("td.sp > a").text
        except AttributeError:
            onsen_num = "不明"
        try:
            dai = item.select_one("td.bg > a").text
        except AttributeError:
            dai = "不明"
        try:
            roten = item.select_one("td.ro > a").text
        except AttributeError:
            roten = "不明"
        try:
            sauna = item.select_one("td.sa > a").text
        except AttributeError:
            sauna = "不明"
        try:
            kinen = item.select_one("td.sm > a").text
        except AttributeError:
            kinen = "不明"
        try:
            kokyu = item.select_one("td.hc > a").text
        except AttributeError:
            kokyu = "不明"

        print("{0}番目の情報:{1}をDataFrameに追加します...".format(len(df)+1, name))
        print("温泉名:{0} 県名:{1} 市町村:{2} 丁目:{3} リンク:{4} 評価平均:{5} 口コミ:{6} 宿数:{7} 温泉数:{8} 大浴場:{9} 露天風呂:{10} サウナ:{11} 禁煙:{12} 高級:{13} 単純:{14} 塩化:{15} 炭酸:{16} 硫黄:{17} 放射能:{18} 硫酸:{19} 酸性:{20} 含鉄:{21} 二酸:{22} ヨウ素:{23} 緯度:{24} 経度:{25}" \
            .format(name, prefecture, city, lv01Nm, link, hyoka, comi, yado, onsen_num, dai, roten, sauna, kinen, kokyu, tanjun, enka, tansan, iou, housya, ryusan, sansei, gantetsu, nisan, youso, latitude, longitude))
        se = pandas.Series([name, prefecture, city, lv01Nm, link, hyoka, comi, yado, onsen_num, dai, roten, sauna, kinen, kokyu, tanjun, enka, tansan, iou, housya, ryusan, sansei, gantetsu, nisan, youso, latitude, longitude], columns)
        df = df.append(se, ignore_index = True)
    return df

# 温泉地をクリック＞各施設一覧から得られる位置情報をもとに、詳細な住所を出力
def get_city(url):
    url_re = "https://yadococo.net/" + url
    res = requests.get(url_re)
    res_text = res.text
    soup = BeautifulSoup(res_text, 'html.parser')
    ret = soup.find_all("tr")
    if len(ret) >= 2:
        ret.pop(0)
        ret.pop(-1)
    lat_list = []
    long_list = []
    if len(lat_list) == 0:
        latitude, longitude = "不明", "不明"
    for item in ret:
        try:
            link = item.select("td.mp")[0].find("a").get("href")
            list_mp = link.split("&")
            lalo = list_mp[1].split("=")
            latitude, longitude = lalo[1].split(",")
            lat_list.append(float(latitude))
            long_list.append(float(longitude))
        except:
            latitude, longitude = "不明", "不明"
    time.sleep(1)
    if (len(lat_list) != 0):
        city, lv01Nm = reverse_geocoding(lat_list[0], long_list[0])
    else:
        city, lv01Nm = "不明", "不明"
    return city, lv01Nm, latitude, longitude

# 国土地理院のAPIを用い、緯度経度に対応する地名を出力
def reverse_geocoding(latitude, longitude):
    endpoint_url = 'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress'
    params = {
        'lat':latitude,
        'lon':longitude
    }
    res = requests.get(endpoint_url, params=params)
    data = res.json()
    try:
        d = data["results"]
        muniCd = d["muniCd"]
        lv01Nm = d["lv01Nm"]
        df = pandas.read_csv("municode.csv").astype({'muniCd':str})
        city = df.loc[df["muniCd"] == str(int(muniCd)), "chiriin_city_name"].iloc[-1]
    except KeyError:
        city, lv01Nm = "不明", "不明"
    return city, lv01Nm

# 泉質に関する辞書を作成。含まれていればTrue, 含まれていなければFalseを返す。
def def_kounou(item):
    kounou = {'単純': False, '塩化': False, '炭酸': False, '硫黄': False, '放射能': False, '硫酸': False, '酸性': False, '含鉄': False, '二酸': False, 'ヨウ素': False}
    find_div = item.select("td.qt > div")
    for i in range(len(find_div)):
        if find_div[i].get("class")[1] != "bath_off":
            kounou[find_div[i].text] = True
    return kounou['単純'], kounou['塩化'], kounou['炭酸'], kounou['硫黄'], kounou['放射能'], kounou['硫酸'], kounou['酸性'], kounou['含鉄'], kounou['二酸'], kounou['ヨウ素']

def main():
    url = "https://yadococo.net/onsen.php"
    columns = ["name", "prefecture", "city", "lv01Nm", "link", "hyoka", "comi", "yado", "onsen_num", "dai", "roten", "sauna", "kinen", "kokyu", "tanjun", "enka", "tansan", "iou", "housya", "ryusan", "sansei", "gantetsu", "nisan", "youso", "latitude", "longitude"]
    df = pandas.DataFrame(columns=columns)
    results = get_items(url, df, columns)
    results.to_csv("onsen_info.csv", index= False)

if __name__ == '__main__':
    main()


