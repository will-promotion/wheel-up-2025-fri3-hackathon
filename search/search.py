import pandas as pd
import re
import os

# CSVファイルのパス（絶対パスに修正）
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(current_dir, 'with_class_method.csv')

def search_subjects_from_csv(subject_keyword='', period_keyword='', ondemand_keyword=''):
    """CSVファイルから教科を検索する関数"""
    try:
        # CSVを読み込む
        df = pd.read_csv(csv_file)
        
        # 条件を順に適用（空欄は無視）
        if subject_keyword.strip():
            df = df[df['科目名'].astype(str).str.contains(subject_keyword, na=False)]
        if period_keyword.strip():
            df = df[df['学期曜日時限'].astype(str).str.contains(period_keyword, na=False)]
        if ondemand_keyword.strip():
            df = df[df['授業方法'].astype(str).str.contains(ondemand_keyword, na=False)]
        
        # 結果を辞書のリストに変換
        results = []
        for _, row in df.iterrows():
            # 曜日と時限を抽出
            period_info = str(row.get('学期曜日時限', ''))
            day = ''
            period = ''
            
            # 曜日の抽出
            if '月' in period_info:
                day = '月'
            elif '火' in period_info:
                day = '火'
            elif '水' in period_info:
                day = '水'
            elif '木' in period_info:
                day = '木'
            elif '金' in period_info:
                day = '金'
            elif '土' in period_info:
                day = '土'
            
            # 時限の抽出（数字を探す）
            period_match = re.search(r'(\d+)', period_info)
            if period_match:
                period = period_match.group(1)
            
            subject_data = {
                'name': row.get('科目名', ''),
                'teacher': row.get('担当教員', ''),
                'day': day,
                'period': period,
                'room': row.get('使用教室', ''),
                'credits': row.get('単位数', ''),
                'style': row.get('授業形態', ''),
                'description': f"{row.get('科目区分', '')} - {row.get('授業方法', '')}",
                'memo': f"キャンパス: {row.get('キャンパス', '')}",
                'ease': row.get('単位取得難易度', ''),
                'evaluation': row.get('成績評価方法', ''),
                'url': row.get('URL', '')
            }
            results.append(subject_data)
        
        return results
    except Exception as e:
        print(f"検索エラー: {e}")
        return []

# 元のコマンドライン用のコード（原型を保持）
if __name__ == "__main__":
    # ユーザーに検索条件を入力させる（空欄ならスキップ）
    subject_keyword = input("科目名のキーワードを入力してください（空欄でスキップ）: ")
    period_keyword = input("学期曜日時限のキーワードを入力してください（空欄でスキップ）: ")
    ondemand_keyword = input("授業形態のキーワードを入力してください（空欄でスキップ）: ")

    # 検索実行
    results = search_subjects_from_csv(subject_keyword, period_keyword, ondemand_keyword)
    
    # 結果を表示
    print("\n一致したデータ:")
    for result in results:
        print(f"科目名: {result['name']}")
        print(f"担当教員: {result['teacher']}")
        print(f"曜日・時限: {result['day']}曜日 {result['period']}限")
        print(f"教室: {result['room']}")
        print(f"単位数: {result['credits']}")
        print(f"授業形態: {result['style']}")
        print(f"説明: {result['description']}")
        print(f"メモ: {result['memo']}")
        print(f"楽さ: {result['ease']}")
        print(f"評価方法: {result['evaluation']}")
        print(f"URL: {result['url']}")
        print("-" * 50)
