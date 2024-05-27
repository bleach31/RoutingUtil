"""
このスクリプトは以下の処理を行います：
1. 指定されたExcelファイルから住所を読み込みます。
2. Google Maps APIを使用して住所をジオコーディングし、緯度と経度を取得します。
3. 取得した緯度・経度に基づき、重複する住所の数（＝子供の数）をカウントします。
3. 結果に対してID（連番）を付与します
4. 結果をエクセルファイルおよびKMLファイルに保存します。
"""
import os
import googlemaps
from datetime import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from urllib.parse import quote
import fastkml
import simplekml
import pandas as pd
###################################################################
# 設定セクション
class Config:
    xl_path = "JIS_20240509.xlsx"
    address_col = 10 # 住所が記載されたエクセルの列番号、10はJ列に相当、4の場合D列に相当
    kml_cache_path = ".mymap.kml" # キャッシュとしてのkmlファイル
    kml_save_path = ".mymap.kml" # 保存されるkmlファイル
    excel_save_path = "route.xlsx" # 保存されるエクセルファイル
###################################################################
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

# KMLオブジェクトを作成
kml_cache = fastkml.kml.KML()
kml_save = simplekml.Kml()

# Excelファイルを開く
workbook = pd.read_excel(Config.xl_path)
addresses = workbook.iloc[2:, Config.address_col - 1].dropna().tolist() # 住所リストを取得


# 既存のKMLファイルから住所と座標を読み込む(キャッシュ用)
cached_location_data = {}
with open(Config.kml_cache_path, 'rb') as kml_file:
    kml_cache.from_string(kml_file.read())
    for pm in list(kml_cache.features())[0].features():
        address = pm.name.split(':')[1]
        lat, lng = pm.geometry.y,pm.geometry.x,
        cached_location_data[address] = (lat, lng)
        

# データを格納するための空のリストを初期化
df_data = []
# 住所をジオコーディングし、座標を取得
for address in addresses:
    # キャッシュから座標を取得するか、GoogleMAP APIにてジオコーディングを行う
    if address in cached_location_data:
        lat, lng = cached_location_data[address]
    else:
        result = gmaps.geocode(address)
        lat = result[0]['geometry']['location']['lat']
        lng = result[0]['geometry']['location']['lng']
        cached_location_data[address] = (lat, lng)

    # データフレーム用のデータを追加
    df_data.append((lat, lng, address))

# DataFrameを作成
df = pd.DataFrame(df_data, columns=["latitude", "longitude", "address"])

# 重複した座標の件数をカウント
df["count"] = df.groupby(["latitude", "longitude"])["latitude"].transform("count")

# 重複する行を削除
df_unique = df.drop_duplicates(subset=["latitude", "longitude"])

# ID列を先頭列に追加
df_unique.insert(0, 'ID', range(1, len(df_unique) + 1))

# Excelファイルに保存
df_unique.to_excel(Config.excel_save_path, index=False, sheet_name="Location Data")

## 以下、KMLファイル作成
# プレースマークを作成
for _, row in df_unique.iterrows():
    lat = row["latitude"]
    lng = row["longitude"]
    count = row["count"]
    address = row["address"]
    ID = row["ID"]  # IDを取得
    placemark = kml_save.newpoint(name=f"{ID}:(kids:{count}){address}:")
    placemark.coords = [(lng, lat)]

    # ラベルを設定
    if count <= 10:
        placemark.style.iconstyle.icon.href = f'http://maps.google.com/mapfiles/kml/paddle/{count}.png'
    else:
        placemark.style.iconstyle.icon.href = f'https://maps.google.com/mapfiles/kml/paddle/pink-stars.png'
    placemark.style.iconstyle.scale = 1.0
    placemark.style.labelstyle.scale = 0.7
    placemark.style.labelstyle.color = simplekml.Color.black

# KMLファイルを保存
kml_save.save(Config.kml_save_path)