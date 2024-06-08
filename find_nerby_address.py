"""
このプログラムは、エクセルファイルから住所と座標を読み込み、指定された直線距離の閾値に基づいて
住所をグループ化するものです。エクセルファイルのスキーマは以下の通りです。

ID      latitude    longitude   address     count

設定セクションでエクセルファイルのパスと直線距離の閾値を指定します。
.envファイルからGoogle Maps APIキーを読み込み、geopyライブラリを使用して距離計算を行います。
グループ化された住所はコンソールに出力されます。
"""
import os
import googlemaps
from os.path import join, dirname
from dotenv import load_dotenv
import pandas as pd
from geopy.distance import geodesic

###################################################################
# 設定セクション
class Config:
    excel_path: str = "route.xlsx" # エクセルファイルパス
    distance_threshold: int = 250 # 直線距離の閾値を設定（メートル単位）
###################################################################

# APIキーを.envファイルから読み込み
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

# エクセルファイルからデータを読み込み
df = pd.read_excel(Config.excel_path)

# 住所と座標をリストに格納
addresses = []
for index, row in df.iterrows():
    id = row['ID']
    address = row['address']
    count = row['count']
    coordinates = (row['latitude'], row['longitude'])
    addresses.append((id, address, coordinates, count))

# 重心を計算する関数
def calculate_centroid(coordinates_list):
    lat_sum = sum(lat for _, (lat, _) in coordinates_list)
    lng_sum = sum(lng for _, (_, lng) in coordinates_list)
    count = len(coordinates_list)
    return (lat_sum / count, lng_sum / count)

# 住所をグループ化
grouped_addresses = []
for id, address, coordinates, count in addresses:
    # 既存のグループに属するかを確認
    found_group = False
    for group in grouped_addresses:
        # グループ内の住所との最大距離を計算
        max_distance = max(geodesic(coordinates, group_coordinates).meters for _, _, group_coordinates, _ in group)
        if max_distance <= Config.distance_threshold:
            group.append((id, address, coordinates, count))
            found_group = True
            break
    
    # 新しいグループを作成
    if not found_group:
        grouped_addresses.append([(id, address, coordinates, count)])

# グループ化された住所を表示
for i, group in enumerate(grouped_addresses):
    if len(group) >= 2:
        print(f"Group {i + 1}:")
        for id, address, _, count in group:
            print(f"  - ID: {id}, Address: {address}, Kids_Count: {count}")
        print()








