from flask import Flask, render_template, request, jsonify
import json
import sys
import os

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
        
        print(f"検索条件: 科目={subject_keyword}, 曜日・時限={period_keyword}, 授業方法={ondemand_keyword}")
        
        # search.pyの関数を呼び出し
        results = search_subjects_from_csv(subject_keyword, period_keyword, ondemand_keyword)
        
        print(f"検索結果数: {len(results)}")
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        print(f"検索エラー: {e}")
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 