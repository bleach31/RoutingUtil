"""
このスクリプトは以下の処理を行います：
1. 指定されたExcelファイルから住所を読み込みます。
2. Google Maps APIを使用して住所をジオコーディングし、緯度と経度を取得します。
3. 取得した緯度・経度に基づき、重複する住所の数（＝子供の数）をカウントします。
4.住所・緯度・経度・子供の数をエクセルファイルおよびKMLファイルに保存します。
"""
import os
import googlemaps
from os.path import join, dirname
from dotenv import load_dotenv
import fastkml
import simplekml
import pandas as pd
import sys
###################################################################
# 設定セクション
class Config:
    xl_path = "Tourenplan_JIS_20240608.xlsx"
    address_col_street = 5 # 住所（Strasse）が記載されたエクセルの列番号、6はG列に、5はF列に相当
    address_col_city = 7     # 住所（市）が記載されたエクセルの列番号、7はH列に相当
    address_row = 3 # 住所が記載されたエクセルの開始行番号
    kml_cache_path = ".mymap.kml" # キャッシュとしてのkmlファイル
    kml_save_path = ".mymap.kml" # 保存されるkmlファイル
    excel_save_path = "route_bus.xlsx" # 保存されるエクセルファイル
###################################################################
# :TODO グーグルのMYMAPはエクセルを読み込めるので、もはやKMLいらない
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

# KMLオブジェクトを作成
kml_cache = fastkml.kml.KML()
kml_save = simplekml.Kml()

# Excelファイルを開く
workbook = pd.read_excel(Config.xl_path)
# Street列とCity列を同時にピックアップして"{street}, {city}"という文字列として結合
addresses_raw = workbook.iloc[Config.address_row:, [Config.address_col_street, Config.address_col_city]].dropna()
addresses = [f"{row[0]}, {row[1]}" for row in addresses_raw.values]

# 既存のKMLファイルから住所と座標を読み込む(キャッシュ用,API呼び出し回数削減目的)
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
        if not result:
            raise ValueError(f"Geocode not found for address: {address}")
            print("The program will now exit.")
            sys.exit(1)
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