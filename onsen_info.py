import requests
from bs4 import BeautifulSoup
import pandas
import time
import re
from urllib import request, parse
import numpy as np


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
        latitude, longitude = get_latlong(onsen_url)
        city, lv01Nm = reverse_geocoding(latitude, longitude)
        try:
            links = item.select("td.hp")[0]
            link = links.find("a").get("href")
        except IndexError:
            link = "なし"
        kounou = {}
        find_div = item.select("td.qt > div")
        for i in range(len(find_div)):
            if find_div[i].get("class")[1] != "bath_off":
                kounou[find_div[i].text] = 1
            else:
                kounou[find_div[i].text] = 0
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
        print("県名:{0} 温泉名:{1} リンク:{2} 効能:{3} 評価平均:{4} 口コミ:{5} 宿数:{6} 温泉数:{7} 大浴場:{8} 露天風呂:{9} サウナ:{10} 禁煙:{11} 高級:{12} 市町村:{13} 丁名:{14}" \
            .format(prefecture, name, link, kounou, hyoka, comi, yado, onsen_num, dai, roten, sauna, kinen, kokyu, city, lv01Nm))
        se = pandas.Series([prefecture, name, link, kounou, hyoka, comi, yado, onsen_num, dai, roten, sauna, kinen, kokyu, city, lv01Nm], columns)
        df = df.append(se, ignore_index = True)
    return df

def get_latlong(url):
    url_re = "https://yadococo.net/" + url
    res = requests.get(url_re)
    res_text = res.text
    soup = BeautifulSoup(res_text, 'html.parser')
    ret = soup.find_all("tr")
    ret.pop(0)
    ret.pop(-1)
    lat_list = []
    long_list = []
    for item in ret:
        try:
            links = item.select("td.mp")[0]
            link = links.find("a").get("href")
        except IndexError:
            print("Error\n")
        list_mp = link.split("&")
        try:
            lalo = list_mp[1].split("=")
            latitude, longitude = lalo[1].split(",")
            lat_list.append(float(latitude))
            long_list.append(float(longitude))
        except:
            pass
    time.sleep(1)
    if len(lat_list) == 0:
        return [0, 0]
    else:
        return np.mean(lat_list), np.mean(long_list)

def reverse_geocoding(latitude, longitude):
    endpoint_url = 'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress'
    params = {
        'lat':latitude,
        'lon':longitude
    }
    res = requests.get(endpoint_url, params=params)
    data = res.json()
    d = data["results"]
    muniCd = d["muniCd"]
    lv01Nm = d["lv01Nm"]
    df = pandas.read_csv("municode.csv").astype({'muniCd':str})
    city = df.loc[df["muniCd"] == str(int(muniCd)), "chiriin_city_name"].iloc[-1]
    return city, lv01Nm

def main():
    url = "https://yadococo.net/onsen.php"
    columns = ["prefecture", "name", "link", "kounou", "hyoka", "comi", "yado", "onsen_num", "dai", "roten", "sauna", "kinen", "kokyu", "city", "lv01Nm"]
    df = pandas.DataFrame(columns=columns)
    results = get_items(url, df, columns)
    results.to_csv("onsen_info.csv", index= False)

if __name__ == '__main__':
    main()


