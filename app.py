from flask import Flask, render_template, request, jsonify
import json
import sys
import os
import pandas as pd
import ast

# search.pyのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'search'))
from search import search_subjects_from_csv

app = Flask(__name__)

# 時間割データ（初期状態）
schedule_data = {
    '月': ['', '', '', '', '', ''],
    '火': ['', '', '', '', '', ''],
    '水': ['', '', '', '', '', ''],
    '木': ['', '', '', '', '', ''],
    '金': ['', '', '', '', '', ''],
    '土': ['', '', '', '', '', '']
}

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html', schedule=schedule_data)

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    global schedule_data
    data = request.get_json()
    day = data.get('day')
    period = data.get('period')
    subject = data.get('subject')
    
    print(f"update_schedule called with: day={day}, period={period}, subject={subject}")
    
    # periodがNoneまたは無効な値の場合の処理
    if period is None:
        return jsonify({'success': False, 'message': '時限が無効です'})
    
    try:
        period = int(period)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '時限が数値ではありません'})
    
    if day in schedule_data and 0 <= period < len(schedule_data[day]):
        schedule_data[day][period] = subject
        print(f"Updated schedule: {day}曜日{period}限 = {subject}")
        return jsonify({'success': True, 'message': '時間割を更新しました'})
    
    return jsonify({'success': False, 'message': '無効なデータです'})

@app.route('/search_subjects', methods=['POST'])
def search_subjects():
    """教科検索API"""
    try:
        data = request.get_json()
        subject_keyword = data.get('subject', '')
        period_keyword = data.get('period', '')
        ondemand_keyword = data.get('ondemand', '')
        try:
            page = int(data.get('page') or 1)
        except Exception:
            page = 1
        try:
            per_page = int(data.get('per_page') or 10)
        except Exception:
            per_page = 10
        results = search_subjects_from_csv(subject_keyword, period_keyword, ondemand_keyword)
        total_count = len(results)
        total_pages = (total_count + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paged_results = results[start:end]
        if total_count > 15:
            return jsonify({
                'success': False,
                'error': '検索結果が多すぎます。条件を絞ってください（最大9件まで）。',
                'results': []
            })
        return jsonify({
            'success': True,
            'results': paged_results,
            'count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'results': []
        })

@app.route('/get_schedule', methods=['GET'])
def get_schedule():
    return jsonify(schedule_data)

@app.route('/get_subject_detail')
def get_subject_detail():
    name = request.args.get('name', '')
    day = request.args.get('day', '')
    period = request.args.get('period', '')
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'search', 'with_class_method.csv')
        df = pd.read_csv(csv_path)
        result = None
        for _, row in df.iterrows():
            # 科目名一致
            if str(row.get('科目名', '')).strip() != name.strip():
                continue
            # 曜日一致
            period_info = str(row.get('学期曜日時限', ''))
            day_match = False
            if day in period_info:
                day_match = True
            if not day_match:
                continue
            # 時限一致
            period_match = False
            # 時限列が配列形式の場合も考慮
            time_period = row.get('時限', '')
            if time_period and time_period != 'nan':
                if isinstance(time_period, str) and time_period.startswith('['):
                    try:
                        period_list = ast.literal_eval(time_period)
                        if period_list and str(period_list[0]) == str(int(period)+1):
                            period_match = True
                    except:
                        pass
                else:
                    if str(time_period) == str(int(period)+1):
                        period_match = True
            else:
                # 学期曜日時限から数字抽出
                import re
                m = re.search(r'(\d+)', period_info)
                if m and m.group(1) == str(int(period)+1):
                    period_match = True
            if not period_match:
                continue
            result = row.to_dict()
            break
        if result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'success': False, 'data': None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 