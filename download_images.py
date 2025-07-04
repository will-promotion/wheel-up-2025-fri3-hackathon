import os
import urllib.request

os.makedirs('img', exist_ok=True)

images = [
    ("student_think.png", "https://1.bp.blogspot.com/-QwQn6v7k1nA/Xy1Qn6v7k1nA/AAAAAAABc1A/悩む学生.png"),  # いらすとや等のフリー素材は手動で
    ("ui_icon.png", "https://cdn-icons-png.flaticon.com/512/1828/1828884.png"),
    ("search_icon.png", "https://cdn-icons-png.flaticon.com/512/622/622669.png"),
    ("mobile_icon.png", "https://cdn-icons-png.flaticon.com/512/747/747376.png"),
    ("realtime_icon.png", "https://cdn-icons-png.flaticon.com/512/189/189792.png"),
    ("python_logo.png", "https://www.python.org/static/community_logos/python-logo.png"),
    ("flask_logo.png", "https://flask.palletsprojects.com/en/2.3.x/_images/flask-logo.png"),
    ("pandas_logo.png", "https://pandas.pydata.org/static/img/pandas_mark.svg"),
    ("sqlite_logo.png", "https://www.sqlite.org/images/sqlite370_banner.gif"),
    ("html_logo.png", "https://upload.wikimedia.org/wikipedia/commons/6/61/HTML5_logo_and_wordmark.svg"),
    ("css_logo.png", "https://upload.wikimedia.org/wikipedia/commons/d/d5/CSS3_logo_and_wordmark.svg"),
    ("js_logo.png", "https://upload.wikimedia.org/wikipedia/commons/6/6a/JavaScript-logo.png"),
]

for filename, url in images:
    path = os.path.join('img', filename)
    try:
        print(f"Downloading {filename} ...")
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("\n手動で保存が必要な画像:")
print("student_think.png（いらすとや等のフリー素材は著作権の都合で自動DL不可。公式サイトから保存してください）")
print("screenshot.png（ご自身のスクリーンショットをimgフォルダに保存してください）") 