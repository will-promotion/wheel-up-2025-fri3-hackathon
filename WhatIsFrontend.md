# ウェブアプリケーションの作り方（初心者向け）

## 1. ウェブアプリケーションとは？

ウェブアプリケーションは、インターネットブラウザ（Chrome、Firefox、Safariなど）で動作するアプリケーションです。

### 基本的な仕組み
```
ユーザー → ブラウザ → インターネット → サーバー → データベース
   ↑                                                      ↓
   ← ブラウザ ← インターネット ← サーバー ← データベース ←
```

## 2. ウェブアプリケーションの構成要素

### フロントエンド（ブラウザ側）
- **HTML**: ページの構造（骨組み）
- **CSS**: 見た目のデザイン（色、レイアウト）
- **JavaScript**: 動的な動作（ボタンクリック、データ送信）

### バックエンド（サーバー側）
- **Python + Flask**: サーバー処理
- **SQLite**: データの保存
- **API**: フロントエンドとバックエンドの通信

## 3. 時間割アプリのファイル構造

```
時間割アプリ/
├── app.py              # メインのサーバー（Flask）
├── sql.py              # データベース処理（既存）
├── school.db           # データベースファイル（既存）
├── requirements.txt    # 必要なライブラリ一覧
├── templates/          # HTMLファイル
│   └── index.html      # メインページ
└── static/             # CSS・JavaScriptファイル
    ├── css/
    │   └── style.css   # デザイン
    └── js/
        └── app.js      # 動作
```

## 4. 各ファイルの役割

### app.py（サーバー）
- ブラウザからのリクエストを受け取る
- データベースから情報を取得
- HTMLページを表示
- APIを提供

### templates/index.html（メインページ）
- 時間割の表示
- 科目追加フォーム
- ユーザーインターフェース

### static/css/style.css（デザイン）
- ページの見た目
- レイアウト
- 色やフォント

### static/js/app.js（動作）
- ボタンクリックの処理
- データの送受信
- ページの動的な更新

## 5. 開発の流れ

1. **サーバー作成** (app.py)
2. **HTMLページ作成** (index.html)
3. **デザイン作成** (style.css)
4. **動作作成** (app.js)
5. **テスト・改善**

## 6. 必要な知識

### HTML（構造）
```html
<div class="container">
    <h1>タイトル</h1>
    <p>テキスト</p>
</div>
```

### CSS（デザイン）
```css
.container {
    background-color: #f0f0f0;
    padding: 20px;
}
```

### JavaScript（動作）
```javascript
function buttonClick() {
    alert('ボタンがクリックされました！');
}
```

### Python（サーバー）
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'
```

## 7. 開発環境の準備

1. **Python**のインストール
2. **Flask**ライブラリのインストール
3. **テキストエディタ**（VS Code推奨）
4. **ブラウザ**（Chrome推奨）

## 8. 実行方法

```bash
# 必要なライブラリをインストール
pip install -r requirements.txt

# サーバーを起動
python app.py

# ブラウザで http://localhost:5000 にアクセス
```

## 9. 学習のポイント

- **段階的に**: まずは簡単なものから始める
- **実践的に**: 実際にコードを書いて動かす
- **繰り返し**: 同じことを何度も練習する
- **調べる**: わからないことは積極的に調べる

## 10. 次のステップ

1. 基本的なHTML/CSS/JavaScriptの学習
2. Flaskの基本概念の理解
3. データベース操作の学習
4. APIの概念理解
5. 実践的なプロジェクト作成
