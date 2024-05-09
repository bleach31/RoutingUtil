import os
import googlemaps
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from urllib.parse import quote
import simplekml

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

#################################
# 住所を指定
""" 
address = '東京都港区芝公園４丁目２−８'
# ジオコーディングを実行 :TODO try-catch必要
result = gmaps.geocode(address)

# 結果から緯度と経度を取得
lat = result[0]['geometry']['location']['lat']
lng = result[0]['geometry']['location']['lng']

# 結果を表示
print(f'住所: {address}')
print(f'緯度: {lat}')
print(f'経度: {lng}')
 """
##################################

# KMLオブジェクトを作成
kml = simplekml.Kml()

# 住所リスト
addresses = [
    {"address": "東京都港区芝公園４丁目２−８", "name": "東京タワー"},
    {"address": "東京都新宿区西新宿２丁目８−１", "name": "東京都庁"},
    {"address": "東京都墨田区押上１丁目１−２", "name": "東京スカイツリー"}
]

# 住所リストからプレースマークを作成
for i, address in enumerate(addresses):
    # プレースマークを作成
    placemark = kml.newpoint(name=address["name"], description=address["address"])
    
    # 住所から座標を取得（ジオコーディング）
    result = gmaps.geocode(address["address"])
    # 結果から緯度と経度を取得
    lat = result[0]['geometry']['location']['lat']
    lng = result[0]['geometry']['location']['lng']

    
    # 座標をプレースマークに設定
    placemark.coords = [(result[0]['geometry']['location']['lng'], result[0]['geometry']['location']['lat'])]
    
    # ラベルを設定
    placemark.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
    placemark.style.iconstyle.scale = 1.0
    placemark.style.labelstyle.scale = 0.7
    placemark.style.labelstyle.color = simplekml.Color.black
    placemark.style.balloonstyle.text = f'<b>{address["name"]}</b><br>{address["address"]}'

# KMLファイルを保存
kml.save(".mymap.kml")