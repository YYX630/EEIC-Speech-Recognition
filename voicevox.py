import requests
import urllib.parse as up
import json
import wave

text='明日の横浜の天気は、晴れのち曇りでしょう'
text_code = up.quote(text)
speaker = 0
response = requests.post(f'http://localhost:50021/audio_query?text={text_code}&speaker={speaker}')
print(response.status_code)    # HTTPのステータスコード取得
query = json.loads(response.text)
print(type(query))    # レスポンスのHTMLを文字列で取得
response = requests.post(f'http://localhost:50021/synthesis?speaker={speaker}', data = json.dumps(query))

file = wave.open("out.wav", "wb") # open file
# setting parameters
file.setnchannels(1)
file.setsampwidth(2)
file.setframerate(24000)
file.writeframes(response.content)
file.close() # close file