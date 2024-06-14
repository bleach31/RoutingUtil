# RoutingUtil

RoutingUtilは、小学校のバスルート策定の補助を行うPythonスクリプトのコレクションです。

## 機能

### geocode_and_count_kids.py
- 所定のエクエルで与えられた住所をジオコーディングし、座標情報をエクセルに書き出す
- 同時にマイマップにインポート可能なKMLファイルを保存する
- 同一座標の住所について、重複している数（子供の数）をカウントする

### find_nerby_address.py
- `geocode_and_count_kids.py`の結果生成されたエクセルファイルにおいて、指定した半径内の近隣住所をコンソールに書き出す

### calculate_route_info.py
- 所定のExcelフォーマットで与えられた住所を通るルートの距離と時間を計算し、エクセルに書き出す

## 環境づくり
1. GoogleMap APIの登録およびAPIキーの取得、
1. API_KEYを`.env`ファイルに保存

        API_KEY = "{YOUR_API_KEY}"

1. instal python 3.10
1. make python virtual env
    * `py -3.10 -m venv env`
    * `.\env\Scripts\activate`
1. run `pip install -r requirements.txt`


## 機能検討時のメモ
### 住所リストからマイマップを作成する
* 視覚的に眺められるようにする。
* マイマップの制御はGoogle MAP JavaScript APIが必要、基本的にはブラウザで動的に制御するためのAPI群になっていてPythonAPIでは提供されてない。
* これを使うのはちょっと大げさなので諦める。
* 代わりにPython を使って KML ファイルを生成し、それを手動で Google マイマップにインポートすることでマイマップを作成することができる。
* あとでわかったが、エクセルからもインポートできるので、KMLを使う意味はなかった。

### 何度もgeocodeをたたかないようにローカルにキャッシュする
* 無料枠200ドル分なので、geocodeだけなら40k回まで無料っぽいができれば欲しい
* https://mapsplatform.google.com/intl/ja/pricing/

### 住所リストから直線距離Xメートル以内の住所の組み合わせを見つけ出す
* 実装上の問題なし
* 距離計算の時、一番離れている住所がXメートル以下になるようにする

### 8件または16件の住所リスト(Waypoint)から時間・距離が最短になる順序を見つけ出す
* 0ベースで単純にやるとAPIの料金が爆発するし、最適化を実装は大変すぎる。最適化は人間がやる。
  * 重み付き（子供の数）の約100のWaypointから、バス（8人乗りまた16人乗り）の台数、距離・時間を最小化する。どうやって定式化すんの...
* 人間がWaypoint（順序含め）を検討し、それを入力すると距離、時間、GoogleURLを計算する補助スクリプトとする



