#!/usr/bin/env python3
# coding: utf-8
#
# 応答生成モジュール
# 基本的には
# - 入力と応答の対応リスト(argv[1])
# - 話者認識結果ID (argv[2])
# - 音声認識結果 (argv[3])
# を受け取って応答文および音声を生成する
#
# 前の応答への依存性を持たせたい場合は引数を追加すれば良い
import sys, os
import requests
import urllib.parse as up
import json
import wave
import time

# 音声合成エンジンのpath
#jtalkbin = '/usr/local/open_jtalk-1.07/bin/open_jtalk '
#options = ' -m syn/nitech_jp_atr503_m001.htsvoice -ow /tmp/dialogue/out.wav -x /usr/local/open_jtalk-1.07/dic'
"""
places = [
    "北海道",
    "青森",
    "秋田",
    "岩手",
    "山形",
    "宮城",
    "福島",
    "群馬",
    "栃木",
    "茨城",
    "埼玉",
    "東京",
    "神奈川",
    "千葉",
    "新潟",
    "長野",
    "山梨",
    "静岡",
    "富山",
    "岐阜",
    "愛知",
    "石川",
    "福井",
    "滋賀",
    "三重",
    "京都",
    "大阪",
    "奈良",
    "和歌山",
    "兵庫",
    "鳥取",
    "岡山",
    "島根",
    "広島",
    "山口",
    "愛媛",
    "香川",
    "高知",
    "徳島",
    "長崎",
    "佐賀",
    "福岡",
    "熊本",
    "大分",
    "宮崎",
    "鹿児島",
    "沖縄"
]
"""
places = {
    "北海道": "Hokkaido",
    "青森": "Aomori",
    "秋田": "Akita",
    "岩手": "Iwate",
    "山形": "Yamagata",
    "宮城": "Miyagi",
    "福島": "Hukushima",
    "群馬": "Gumma",
    "栃木": "Tochigi",
    "茨城": "Ibaraki",
    "埼玉": "Saitama",
    "東京": "Tokyo",
    "神奈川": "Kanagawa",
    "千葉": "Chiba",
    "新潟": "Nigata",
    "長野": "Nagano",
    "山梨": "Yamanashi",
    "静岡": "Sizuoka",
    "富山": "Toyama",
    "岐阜": "Gifu",
    "愛知": "Aichi",
    "石川": "Ishikawa",
    "福井": "Fukui",
    "滋賀": "Shiga",
    "三重": "Mie",
    "京都": "Kyoto",
    "大阪": "Osaka",
    "奈良": "Nara",
    "和歌山": "Wakayama",
    "兵庫": "Hyogo",
    "鳥取": "Tottori",
    "岡山": "Okayama",
    "島根": "Shimane",
    "広島": "Hiroshima",
    "山口": "Yamagichi",
    "愛媛": "Ehime",
    "香川": "Kagawa",
    "高知": "Kochi",
    "徳島": "Tokushima",
    "長崎": "Nagasaki",
    "佐賀": "Saga",
    "福岡": "Hukuoka",
    "熊本": "Kumamoto",
    "大分": "Oita",
    "宮崎": "Miyazaki",
    "鹿児島": "Kagoshima",
    "沖縄": "Okinawa"
}
dates = [
    "今日",
    "明日",
    "明日",
    "明後日",
    "明々後日",
    "四日後",
    "五日後",
    "六日後",
    "一週間後",
    "昨日",
    "一昨日",
    "三日前",
    "四日前",
    "五日前",
    "六日前",
    "一週間前"
]
names = [
    "天気",
    "気温",
    "最低気温",
    "最高気温"
]
weathers = {
    "Clouds": "曇り",
    "Rainy": "雨",
    "Sunny": "晴れ"
}
jtalkbin = 'open_jtalk '
options = '-m /usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice -ow /tmp/dialogue/out.wav -x /var/lib/mecab/dic/open-jtalk/naist-jdic'

# 音声合成のコマンドを生成 (open jtalk を 使う場合
def mk_jtalk_command(answer):
    text_code = up.quote(answer)
    speaker = 0
    response = requests.post(f'http://localhost:50021/audio_query?text={text_code}&speaker={speaker}')
    query = json.loads(response.text)
    response = requests.post(f'http://localhost:50021/synthesis?speaker={speaker}', data = json.dumps(query))

    file = wave.open("/tmp/dialogue/out.wav", "wb") # open file
    # setting parameters
    file.setnchannels(1)
    file.setsampwidth(2)
    file.setframerate(24000)
    file.writeframes(response.content)
    file.close() # close file
    play = 'play -q /tmp/dialogue/out.wav; rm /tmp/dialogue/out.wav;'
    return play

def returnAnswer(question):
    selected_place = ""
    selected_date = ""
    selected_name = ""
    for place in places:
        if place in question:
            selected_place = place
            break
    for date in dates:
        if date in question:
            selected_date = date
            break
    for name in names:
        if name in question:
            selected_name = name
            break
    place_value = places[place]
    API_KEY = "37f77e90e5a6eef3861d8f2698167581" # xxxに自分のAPI Keyを入力。
    api = "http://api.openweathermap.org/data/2.5/weather?q={place}&APPID={key}"

    url = api.format(place = place_value, key = API_KEY)
    print(url)
    response = requests.get(url)
    data = response.json()
    jsonText = json.dumps(data, indent=4)
    print(jsonText)
    weather = data["weather"][0]["main"]
    return weathers[weather]

if __name__ == '__main__':
    # 応答を辞書 reply に登録
    conf = open(sys.argv[1],'r')
    #conf = codecs.open(sys.argv[1],'r','utf8','ignore')
    reply = []
    for line in conf:
        line = line.rstrip()
        reply.append(line)
    print("reply: ", reply)
    conf.close()

    # 話者ID
    sid = int(sys.argv[2])

    # 認識結果
    asrresult = open(sys.argv[3],'r')
    question = asrresult.read().rstrip()
    print("question: ", question)
    asrresult.close()

    # 話者ID と認識結果を表示
    print("SPK"+str(sid)+": "+question)

    # 応答リストから対応する応答を出力
    if question in reply:
        print("returnAnswer")
        answer = returnAnswer(question)
    else:
        answer = 'もう一度お願いします'
    print("Silly: " + answer)
    os.system(mk_jtalk_command(answer))

