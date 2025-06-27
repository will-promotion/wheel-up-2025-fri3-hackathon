from flask import Flask, render_template, request, jsonify
import sqlite3
from sql import init_db, get_all_subjects, add_subject_web, delete_subject

app = Flask(__name__)

# データベースの初期化
init_db()

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """全ての科目を取得するAPI"""
    subjects = get_all_subjects()
    return jsonify(subjects)

@app.route('/api/subjects', methods=['POST'])
def create_subject():
    """新しい科目を追加するAPI"""
    data = request.get_json()
    name = data.get('name')
    day = data.get('day')
    period = data.get('period')
    room = data.get('room', '')
    credits = data.get('credits')
    teacher = data.get('teacher', '')
    evaluation = data.get('evaluation', '')
    style = data.get('style', '')
    description = data.get('description', '')
    memo = data.get('memo', '')
    ease = data.get('ease')
    
    if name and day and period:
        # 数値フィールドの変換
        credits_int = int(credits) if credits else None
        ease_int = int(ease) if ease else None
        
        add_subject_web(name, day, period, room, 
                       credits=credits_int,
                       teacher=teacher,
                       evaluation=evaluation,
                       style=style,
                       description=description,
                       memo=memo,
                       ease=ease_int)
        return jsonify({'message': '科目が追加されました'}), 201
    else:
        return jsonify({'error': '科目名、曜日、時限は必須項目です'}), 400

@app.route('/api/subjects/<int:subject_id>', methods=['DELETE'])
def remove_subject(subject_id):
    """科目を削除するAPI"""
    delete_subject(subject_id)
    return jsonify({'message': '科目が削除されました'})

@app.route('/api/subjects/<int:subject_id>/move', methods=['PUT'])
def move_subject(subject_id):
    """科目を移動するAPI"""
    data = request.get_json()
    new_day = data.get('day')
    new_period = data.get('period')
    
    if not new_day or not new_period:
        return jsonify({'error': '新しい曜日と時限が必要です'}), 400
    
    try:
        # 移動先に既に科目があるかチェック
        from sql import list_subjects
        existing_subjects = list_subjects()
        for subject in existing_subjects:
            if subject[1] == new_day and subject[2] == int(new_period) and subject[0] != subject_id:
                return jsonify({'error': f'{new_day}曜日{new_period}限には既に科目が存在します'}), 400
        
        # 科目を移動
        from sql import update_subject_time
        update_subject_time(subject_id, new_day, int(new_period))
        return jsonify({'message': '科目が移動されました'})
    except Exception as e:
        return jsonify({'error': '科目の移動に失敗しました'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 