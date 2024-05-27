import os
import googlemaps
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from urllib.parse import quote
import fastkml
import simplekml
import openpyxl

###################################################################
# 設定セクション
class Config:
    xl_path = "JIS_20240509.xlsx"
    address_col = 10 # 10はJ列に相当、4の場合D列に相当
    kml_cache_path = ".mymap.kml" # キャッシュとしてのkmlファイル
    kml_save_path = ".mymap.kml" # 保存されるkmlファイル
###################################################################
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

# KMLオブジェクトを作成
kml_cache = fastkml.kml.KML()
kml_save = simplekml.Kml()

# Excelファイルを開く
workbook = openpyxl.load_workbook(Config.xl_path)
sheet = workbook.active

# Excelからのaddress_col列から住所を取得
addresses = []
for row in sheet.iter_rows(min_row=3, min_col=Config.address_col, max_col=Config.address_col, values_only=True):
    address = row[0]
    if address:
        addresses.append(address)

# 既存のKMLファイルから住所と座標を読み込む(キャッシュ用)
address_coords = {}
with open(Config.kml_cache_path, 'rb') as kml_file:
    kml_cache.from_string(kml_file.read())
    for pm in list(kml_cache.features())[0].features():
        address = pm.name.split(':')[1]
        lat, lng = pm.geometry.y,pm.geometry.x,
        address_coords[address] = (lat, lng)

# 重複した住所の件数を数える　:TODO str, strasse, straßeが別住所扱いになる。座標でやるべき
address_count = {}
for address in addresses:
    if address in address_count:
        address_count[address] += 1
    else:
        address_count[address] = 1

# 住所リストからプレースマークを作成
for address, count in address_count.items():
    # プレースマークを作成
    placemark = kml_save.newpoint(name=f"{count}:{address}")
    
    # キャッシュから座標を取得するか、ジオコーディングを行う
    if address in address_coords:
        lat, lng = address_coords[address]
    else:
        result = gmaps.geocode(address)
        lat = result[0]['geometry']['location']['lat']
        lng = result[0]['geometry']['location']['lng']
        address_coords[address] = (lat, lng)
    
    # 座標をプレースマークに設定
    placemark.coords = [(lng, lat)]
    
    # ラベルを設定
    if count <= 10 :
        placemark.style.iconstyle.icon.href = f'http://maps.google.com/mapfiles/kml/paddle/{count}.png'
    else :
        placemark.style.iconstyle.icon.href = f'https://maps.google.com/mapfiles/kml/paddle/pink-stars.png'
    placemark.style.iconstyle.scale = 1.0
    placemark.style.labelstyle.scale = 0.7
    placemark.style.labelstyle.color = simplekml.Color.black
    # placemark.style.balloonstyle.text = f'<b>{address["name"]}</b><br>{address["address"]}'

# KMLファイルを保存
kml_save.save(Config.kml_save_path)