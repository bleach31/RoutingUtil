import os
import googlemaps
from os.path import join, dirname
from dotenv import load_dotenv
import fastkml
from geopy.distance import geodesic

# APIキーを.envファイルから読み込み
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

# KMLファイルパス
kml_path = ".mymap.kml"

# KMLオブジェクトを作成
kml = fastkml.kml.KML()

# 直線距離の閾値を設定（メートル単位）
distance_threshold = 250

# 既存のKMLファイルから住所と座標を読み込む
addresses = []
with open(kml_path, 'rb') as kml_file:
    kml.from_string(kml_file.read())
    for pm in list(kml.features())[0].features():
        address = pm.name.split(':')[1]
        lat, lng = pm.geometry.y,pm.geometry.x,
        addresses.append((address,(lat, lng)))
# 重心を計算する関数
def calculate_centroid(coordinates_list):
    lat_sum = sum(lat for _, (lat, _) in coordinates_list)
    lng_sum = sum(lng for _, (_, lng) in coordinates_list)
    count = len(coordinates_list)
    return (lat_sum / count, lng_sum / count)

# 住所をグループ化
grouped_addresses = []
for address, coordinates in addresses:
    # 既存のグループに属するかを確認
    found_group = False
    for group in grouped_addresses:
        # グループ内の住所との最大距離を計算
        max_distance = max(geodesic(coordinates, group_coordinates).meters for _, group_coordinates in group)
        if max_distance <= distance_threshold:
            group.append((address, coordinates))
            found_group = True
            break
    
    # 新しいグループを作成
    if not found_group:
        grouped_addresses.append([(address, coordinates)])

# グループ化された住所を表示
for i, group in enumerate(grouped_addresses):
    if len(group) >= 2:
        print(f"Group {i + 1}:")
        for address, _ in group:
            print(f"  - {address}")
        print()