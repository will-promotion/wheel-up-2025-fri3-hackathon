# 時間割アプリ（初心者向け）

美しいWebインターフェースを持つ時間割管理アプリケーションです。

## 📋 目次

1. [概要](#概要)
2. [機能](#機能)
3. [必要な環境](#必要な環境)
4. [インストール方法](#インストール方法)
5. [実行方法](#実行方法)
6. [使い方](#使い方)
7. [ファイル構成](#ファイル構成)
8. [トラブルシューティング](#トラブルシューティング)
9. [学習のポイント](#学習のポイント)

## 🎯 概要

このアプリケーションは、学生向けの時間割管理ツールです。既存のSQLiteデータベース（`sql.py`）を活用して、美しいWebインターフェースで時間割を管理できます。

### 主な特徴
- ✨ モダンで美しいデザイン
- 📱 スマートフォン対応（レスポンシブデザイン）
- 🔄 リアルタイム更新
- 📝 科目の追加・削除・詳細表示
- 💾 データベースでの永続化

## 🚀 機能

### 基本機能
- **時間割表示**: 月〜金の6時限分の時間割を表示
- **科目追加**: 新しい科目を時間割に追加
- **科目詳細**: 科目をクリックして詳細情報を表示
- **科目削除**: 不要な科目を削除

### 科目情報
- 教科名
- 曜日・時限
- 教室
- 教員名
- 単位数
- 楽さ（1-5段階評価）
- 授業内容
- メモ

## 💻 必要な環境

### 必須ソフトウェア
1. **Python 3.8以上**
   - [Python公式サイト](https://www.python.org/downloads/)からダウンロード
   - インストール時に「Add Python to PATH」にチェックを入れる

2. **テキストエディタ**
   - Visual Studio Code（推奨）
   - メモ帳でも可能

3. **Webブラウザ**
   - Google Chrome（推奨）
   - Firefox、Safari、Edgeでも動作

### 推奨環境
- Windows 10/11
- 4GB以上のメモリ
- インターネット接続（フォントとアイコンの読み込み用）

## 📦 インストール方法

### 1. プロジェクトの準備
```bash
# プロジェクトフォルダに移動
cd wheel-up-2025-fri3-hackathon

# 現在のファイル構成を確認
dir
```

### 2. 必要なライブラリのインストール
```bash
# 必要なPythonライブラリをインストール
pip install -r requirements.txt
```

**注意**: 初回実行時は少し時間がかかる場合があります。

## ▶️ 実行方法

### 1. サーバーの起動
```bash
# サーバーを起動
python app.py
```

### 2. ブラウザでアクセス
サーバーが起動すると、以下のようなメッセージが表示されます：

```
データベースを初期化中...
データベース初期化完了！
必要なディレクトリを作成中...
ディレクトリ作成完了！
サーバーを起動中...
ブラウザで http://localhost:5000 にアクセスしてください
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### 3. ブラウザでアクセス
ブラウザを開いて以下のURLにアクセス：
```
http://localhost:5000
```

## 📖 使い方

### 基本操作

#### 1. 時間割の確認
- ページを開くと、現在の時間割が表示されます
- 科目がある場合は、カラフルなカードで表示されます

#### 2. 科目の追加
1. 「科目追加」ボタンをクリック
2. フォームに必要事項を入力：
   - **必須項目**: 曜日、時限、教科名、教室
   - **任意項目**: 教員名、単位数、楽さ、授業内容、メモ
3. 「追加」ボタンをクリック
4. 時間割に新しい科目が追加されます

#### 3. 科目の詳細確認
- 時間割の科目カードをクリック
- 詳細情報がポップアップで表示されます

#### 4. 科目の削除
1. 科目カードをクリックして詳細を表示
2. 「削除」ボタンをクリック
3. 確認ダイアログで「OK」をクリック

### 高度な操作

#### 楽さの評価
- 1: とても難しい
- 2: 難しい
- 3: 普通
- 4: 楽
- 5: とても楽

#### データの永続化
- 追加した科目は自動的にデータベースに保存されます
- サーバーを再起動してもデータは保持されます

## 📁 ファイル構成

```
時間割アプリ/
├── app.py              # メインサーバー（Flask）
├── sql.py              # データベース処理（既存）
├── school.db           # データベースファイル（既存）
├── requirements.txt    # 必要なライブラリ一覧
├── README.md           # このファイル
├── WhatFrontendIs.md   # フロントエンド解説
├── templates/          # HTMLファイル
│   └── index.html      # メインページ
└── static/             # CSS・JavaScriptファイル
    ├── css/
    │   └── style.css   # デザイン
    └── js/
        └── app.js      # 動作
```

### 各ファイルの役割

| ファイル | 役割 | 説明 |
|---------|------|------|
| `app.py` | サーバー | ブラウザからのリクエストを処理 |
| `sql.py` | データベース | 既存のデータベース操作 |
| `index.html` | ページ構造 | 時間割の表示とフォーム |
| `style.css` | デザイン | 見た目とレイアウト |
| `app.js` | 動作 | ボタンクリックやデータ送信 |

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. サーバーが起動しない
**エラー**: `ModuleNotFoundError: No module named 'flask'`

**解決方法**:
```bash
pip install flask flask-cors
```

#### 2. ポートが使用中
**エラー**: `Address already in use`

**解決方法**:
```bash
# 別のポートで起動
python app.py --port 5001
```

#### 3. データベースエラー
**エラー**: `database is locked`

**解決方法**:
- 他のプログラムでデータベースを使用していないか確認
- サーバーを再起動

#### 4. ブラウザでアクセスできない
**確認事項**:
- サーバーが正常に起動しているか
- URLが正しいか（`http://localhost:5000`）
- ファイアウォールの設定

### デバッグ方法

#### 1. コンソールログの確認
ブラウザの開発者ツール（F12）を開いて、コンソールタブでエラーメッセージを確認

#### 2. サーバーログの確認
ターミナルでサーバーの起動メッセージを確認

#### 3. データベースの確認
```bash
# SQLiteデータベースを直接確認
sqlite3 school.db
.tables
SELECT * FROM subjects;
.quit
```

## 🎓 学習のポイント

### 初心者向け学習ステップ

#### 1. 基本概念の理解
- **HTML**: ページの構造
- **CSS**: 見た目のデザイン
- **JavaScript**: 動的な動作
- **Python**: サーバー処理
- **SQLite**: データの保存

#### 2. 実践的な学習
1. **HTMLの編集**: `templates/index.html`を編集してページ構造を変更
2. **CSSの編集**: `static/css/style.css`を編集してデザインを変更
3. **JavaScriptの編集**: `static/js/app.js`を編集して動作を変更
4. **Pythonの編集**: `app.py`を編集してサーバー処理を変更

#### 3. 発展的な学習
- **データベース設計**: 新しいテーブルやカラムの追加
- **API設計**: 新しい機能のAPI追加
- **UI/UX改善**: ユーザビリティの向上
- **セキュリティ**: 入力値の検証や認証機能

### おすすめの学習リソース
- [MDN Web Docs](https://developer.mozilla.org/ja/) - HTML/CSS/JavaScript
- [Flask公式ドキュメント](https://flask.palletsprojects.com/) - Python Flask
- [SQLite公式サイト](https://www.sqlite.org/) - データベース

## 📞 サポート

問題が発生した場合や質問がある場合は、以下の方法でサポートを受けられます：

1. **エラーメッセージの確認**: コンソールやターミナルのエラーメッセージを確認
2. **ログの確認**: サーバーの起動ログを確認
3. **ファイルの確認**: 各ファイルが正しく作成されているか確認

## 🎉 次のステップ

このアプリケーションを基に、以下のような機能を追加できます：

- **ユーザー認証**: ログイン機能
- **時間割エクスポート**: PDFやExcel出力
- **通知機能**: 授業開始前のアラート
- **統計機能**: 単位数や楽さの統計
- **テーマ機能**: ダークモード対応

---

**Happy Coding! 🚀**