import requests
from bs4 import BeautifulSoup
import pandas
import time



def get_items(url, df, columns):
    res = requests.get(url)
    res_text = res.text
    soup = BeautifulSoup(res_text, 'html.parser')
    ret = soup.find_all("tr")
    ret.pop(0)
    for item in ret:
        prefecture = item.select("td.kn > a")[0].text
        name = item.select("td.sn > a")[0].text
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
        print("県名:{0} 温泉名:{1} リンク:{2} 効能:{3} 評価平均:{4} 口コミ:{5} 宿数:{6} 温泉数:{7} 大浴場:{8} 露天風呂:{9} サウナ:{10} 禁煙:{11} 高級:{12}" \
            .format(prefecture, name, link, kounou, hyoka, comi, yado, onsen_num, dai, roten, sauna, kinen, kokyu))
        se = pandas.Series([prefecture, name, link, kounou, hyoka, comi, yado, onsen_num, dai, roten, sauna, kinen, kokyu], columns)
        df = df.append(se, ignore_index = True)
    return df

def main():
    url = "https://yadococo.net/onsen.php"
    columns = ["prefecture", "name", "link", "kounou", "hyoka", "comi", "yado", "onsen_num", "dai", "roten", "sauna", "kinen", "kokyu"]
    df = pandas.DataFrame(columns=columns)
    results = get_items(url, df, columns)
    results.to_csv("onsen_info.csv", index= False)

if __name__ == '__main__':
    main()


