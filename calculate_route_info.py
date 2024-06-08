"""
このプログラムは、スクールバスのルートを計算し、各ルートの距離と所要時間をGoogle Maps Directions APIを使用して求めます。
また、各ルートのGoogle Maps上での確認リンクも生成します。ルート計画のデータはExcelファイルに保存されており、
プログラムはそのデータを読み込み、結果を再度Excelファイルに書き戻します。

主な機能:
- バス停のIDから住所を取得
- バスルートの距離と時間を計算
- Google Maps上でルートを確認するためのURLを生成
- 結果をExcelファイルに保存

使用方法:
1. .envファイルにGoogle Maps APIキーを設定してください。
2. 'LocationData'シートにバス停の情報を記載したExcelファイルを用意してください。
3. 'RoutePlanner'シートに調べたいルートを記載してください。
4. プログラムを実行すると、距離、所要時間、Google Maps URLが計算され、Excelファイルに保存されます。

初回実行時には'RoutePlanner'シートが作成されるため、ルート計画を記載して再度実行してください。

"""

from os.path import join, dirname
from dotenv import load_dotenv
import pandas as pd
import openpyxl
import googlemaps
import os
###################################################################
# 設定セクション
class Config:
    excel_path = "route_bus.xlsx"
    goal_address = "Bleyerstraße 4, 81371 München"
###################################################################
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))


# エクセルファイルを読み込みます
file_path = Config.excel_path
location_data = pd.read_excel(file_path, sheet_name='LocationData')
# 'RoutePlanner' シートが存在するか確認し、存在しない場合は作成
excel_file = pd.ExcelFile(file_path)
if 'RoutePlanner' in excel_file.sheet_names:
    route_planner = pd.read_excel(file_path, sheet_name='RoutePlanner')
else:
    # 'RoutePlanner' シートが存在しない場合は新しく作成
    columns = ['stop1', 'stop2', 'stop3', 'stop4', 'stop5', 'stop6', 'stop7', 'stop8', 'stop9', 'stop10', 'stop11', 'stop12', 'stop13', 'stop14', 'stop15', 'stop16', 'Distance(km)', 'Time(min)', 'googlemap_url', 'googlemap_url(ref)']
    route_planner = pd.DataFrame(columns=columns)
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        # 'LocationData' シートを保持
        location_data.to_excel(writer, sheet_name='LocationData', index=False)
        # 'RoutePlanner' シートを作成
        route_planner.to_excel(writer, sheet_name='RoutePlanner', index=False)
    print("RoutePlannerシートが作られたので、調べたいルートを計画してください。")
    exit()  # 初回実行時はここで終了

# バス停の住所をIDから引く辞書を作成します
address_dict = location_data.set_index('ID')['address'].to_dict()

# バスルートの距離と時間を計算し、URLを生成する関数
def calculate_route_info(row):
    stops = row.dropna().astype(int).tolist()
    if 'Distance(km)' in row.index and not pd.isna(row['Distance(km)']):
        return row  # 既にデータがある行はスキップ
    if len(stops) < 2:
        return row  # バス停が2つ未満の場合もスキップ
    
    addresses = [address_dict[stop] for stop in stops]
    addresses.append(Config.goal_address)  # ゴールアドレスを追加
    directions_result = gmaps.directions(addresses[0], addresses[-1], waypoints=addresses[1:-1], mode='driving')

    # 距離と時間を計算
    distance_km = sum(leg['distance']['value'] for leg in directions_result[0]['legs']) / 1000
    time_min = sum(leg['duration']['value'] for leg in directions_result[0]['legs']) / 60

    # Directions APIの結果から直接URLを生成
    origin_address = addresses[0]
    waypoints_addresses = "|".join(addresses[1:-1])
    googlemap_url = f'https://www.google.com/maps/dir/?api=1&origin={origin_address.replace(" ", "+")}&destination={Config.goal_address.replace(" ", "+")}&waypoints={waypoints_addresses.replace(" ", "+")}'
    
    # Google MapsのURLを生成
    #googlemap_url_ref  = 'https://www.google.de/maps/dir/' + '/'.join(addresses).replace(' ', '+')

    # データを更新
    row['Distance(km)'] = distance_km
    row['Time(min)'] = time_min
    row['googlemap_url'] = str(googlemap_url)
    #row['googlemap_url(ref)'] = str(googlemap_url_ref)
    return row

# データフレームの各行に対して距離と時間を計算
route_planner = route_planner.apply(calculate_route_info, axis=1)

# エクセルファイルに書き戻します
with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
    location_data.to_excel(writer, sheet_name='LocationData', index=False)
    route_planner.to_excel(writer, sheet_name='RoutePlanner', index=False)
