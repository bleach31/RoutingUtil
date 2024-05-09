1. instal python 3.10
1. make python virtual env
    * `py -3.10 -m venv env`
    * `.\env\Scripts\activate`
1. run `pip install -r requirements.txt`


やりたいこと
### 住所リストからマイマップを作成

マイマップの制御はGoogle MAP JavaScript APIが必要、基本的にはブラウザで動的に制御するためのAPI群になっていてPythonAPIでは提供されてない。
これを使うのはちょっと大げさなので諦める。代わりにPython を使って KML ファイルを生成し、それを手動で Google マイマップにインポートすることで、Google Drive API を使わずにマイマップを作成することができる。