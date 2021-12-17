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
import urllib
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
dates = [
    "今日",
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
    "Rain": "雨",
    "Clear": "晴れ",
    "Snow": "雪"
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
    selected_date_index = -1
    selected_name = ""
    for place in places:
        if place in question:
            selected_place = place
            break
    for i in range(len(dates)):
        if dates[i] in question:
            selected_date = dates[i]
            selected_date_index = i
            break
    for name in names:
        if name in question:
            selected_name = name
            break
    api = "https://msearch.gsi.go.jp/address-search/AddressSearch?q={city}"
    if place == "東京":
        place = place + "都"
    elif place == "大阪" or place == "京都":
        place = place + "府"
    elif place != "北海道":
        place = place + "県"
    s_quote = urllib.parse.quote(place)
    url2 = api.format(city = s_quote)
    response = requests.get(url2)
    coordinates = response.json()[0]["geometry"]["coordinates"]
    jsonText = json.dumps(coordinates, indent=4)

    API_KEY = "37f77e90e5a6eef3861d8f2698167581" # xxxに自分のAPI Keyを入力。
    api = "http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&APPID={key}"
    time = selected_date_index
    url = api.format(lat=coordinates[1],lon=coordinates[0], key = API_KEY)
    print(url)
    response = requests.get(url)
    data = ""
    if selected_name == "天気":
        data = response.json()["daily"][time]["weather"][0]["main"]
        data = weathers[data]
    elif selected_name == "気温":
        data = str(response.json()["daily"][time]["temp"]["day"])
    elif selected_name == "最高気温":
        data = str(response.json()["daily"][time]["temp"]["max"])
    elif selected_name == "最低気温":
        data = str(response.json()["daily"][time]["temp"]["min"])
    print(data)
    answer = selected_date + "の" + selected_name + "は" + data + "です"
    return answer

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
