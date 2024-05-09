1. instal python 3.10
1. make python virtual env
    * `py -3.10 -m venv env`
    * `.\env\Scripts\activate`
1. run `pip install -r requirements.txt`


やりたいこと
### 住所リストからマイマップを作成

マイマップの制御はGoogle MAP JavaScript APIが必要、基本的にはブラウザで動的に制御するためのAPI群になっていてPythonAPIでは提供されてない。
これを使うのはちょっと大げさなので諦める。代わりにPython を使って KML ファイルを生成し、それを手動で Google マイマップにインポートすることでマイマップを作成することができる。

### 何度もgeocodeをたたかないようにローカルにキャッシュする仕組み
要る?無料枠200ドル分なので、geocodeだけなら40k回まで無料ってことかな

https://mapsplatform.google.com/intl/ja/pricing/

###　住所リストから直線距離300m以内の住所の組み合わせを見つけ出す



### 8件または16件の住所リストから時間・距離が最短になる順序を見つけ出す
単純にやると料金爆発する
* 8P8=40,320
* 16P16=20,922,789,888,000

これは手動でやるとして、調査した順列の結果は検討用に残したい
順列、距離、時間、GoogleURLみたいなリスト

Compute Routes Matrixを使えばいいっぽい？
    怪しい、マトリックスで出されても困る
 
最終的にはマイマップじゃなくて通常のGoogleMAPのリンクがほしい。これは文字列生成でできそう


