import pandas as pd

# CSVファイルのパス
csv_file = 'with_class_method.csv'

# CSVを読み込む
df = pd.read_csv(csv_file)

# ユーザーに検索条件を入力させる（空欄ならスキップ）
subject_keyword = input("科目名のキーワードを入力してください（空欄でスキップ）: ")
period_keyword = input("学期曜日時限のキーワードを入力してください（空欄でスキップ）: ")
ondemand_keyword = input("授業形態のキーワードを入力してください（空欄でスキップ）: ")

# 条件を順に適用（空欄は無視）
if subject_keyword.strip():
    df = df[df['科目名'].astype(str).str.contains(subject_keyword, na=False)]
if period_keyword.strip():
    df = df[df['学期曜日時限'].astype(str).str.contains(period_keyword, na=False)]
if ondemand_keyword.strip():
    df = df[df['授業方法'].astype(str).str.contains(ondemand_keyword, na=False)]

# 結果を表示
print("\n一致したデータ:")
print(df)
