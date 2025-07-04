from flask import Flask, render_template, request, jsonify,Response
import sqlite3
import json
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from recommend import search_similarity
from sql import init_db, get_all_subjects, add_subject_web, delete_subject, list_subjects, update_subject_time

app = Flask(__name__)

init_db()

CSV_PATH = "subjects.csv"
WEIGHTS = {"name": 0.7, "teacher": 0.3}

# トークン化（文字単位）
def tokenize(text):
    return list(str(text))

def sentence_vector(row, model):
    total_vec = np.zeros(model.vector_size)
    total_weight = 0.0
    for col, weight in WEIGHTS.items():
        tokens = tokenize(row.get(col, ""))
        vecs = [model.wv[w] for w in tokens if w in model.wv]
        if vecs:
            total_vec += weight * np.mean(vecs, axis=0)
            total_weight += weight
    return total_vec / total_weight if total_weight > 0 else total_vec

def dataframe_to_sentences(df):
    return [
        [token for col in WEIGHTS.keys() for token in tokenize(row[col])] for _, row in df.iterrows()
    ]

def load_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]
    return pd.DataFrame({"name": df["科目名"], "teacher": df["担当教員"]})

def compute_best_matches(db_df, csv_df, model):
    csv_vecs = [sentence_vector(row, model) for _, row in csv_df.iterrows()]
    all_matches = []
    for _, db_row in db_df.iterrows():
        db_vec = sentence_vector(db_row, model)
        best_score = -1
        best_row = None
        for csv_row, csv_vec in zip(csv_df.itertuples(index=False), csv_vecs):
            score = cosine_similarity([db_vec], [csv_vec])[0][0]
            all_matches.append((score, csv_row))
    all_matches.sort(key=lambda x: x[0], reverse=True)
    return all_matches[:5]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = get_all_subjects()
    return jsonify(subjects)

@app.route('/api/subjects', methods=['POST'])
def create_subject():
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
    delete_subject(subject_id)
    return jsonify({'message': '科目が削除されました'})

@app.route('/api/subjects/<int:subject_id>/move', methods=['PUT'])
def move_subject(subject_id):
    data = request.get_json()
    new_day = data.get('day')
    new_period = data.get('period')

    if not new_day or not new_period:
        return jsonify({'error': '新しい曜日と時限が必要です'}), 400

    existing_subjects = list_subjects()
    for subject in existing_subjects:
        if subject[1] == new_day and subject[2] == int(new_period) and subject[0] != subject_id:
            return jsonify({'error': f'{new_day}曜日{new_period}限には既に科目が存在します'}), 400

    update_subject_time(subject_id, new_day, int(new_period))
    return jsonify({'message': '科目が移動されました'})


def convert_to_serializable(d):
    """
    NumPy / pandas 型を Python 標準型へ変換
    """
    return {
        k: (int(v) if isinstance(v, (np.integer,))
            else float(v) if isinstance(v, (np.floating,))
            else str(v) if isinstance(v, (np.generic,))
            else v)
        for k, v in d.items()
    }

@app.route('/api/similar_subjects', methods=['GET'])
def get_similar_subjects():
    """
    DB内の講義それぞれに対して、最も類似するCSV講義を取得するAPI
    """
    results = search_similarity()

    output = []
    for db_row, csv_row, score in results:
        db_dict  = convert_to_serializable(db_row.to_dict())
        csv_dict = convert_to_serializable(csv_row.to_dict())

        output.append({
            "db": {
                "name": db_dict.get("name", ""),
                "teacher": db_dict.get("teacher", "")
            },
            "matched_csv": {
                "name": csv_dict.get("name", ""),
                "teacher": csv_dict.get("teacher", ""),
                "day": csv_dict.get("day", ""),
                "period": csv_dict.get("period", ""),
                "room": csv_dict.get("room", ""),
                "credits": csv_dict.get("credits", ""),
                "evaluation": csv_dict.get("evaluation", ""),
                "style": csv_dict.get("style", ""),
                "description": csv_dict.get("description", "")
            },
            "score": round(float(score), 3)
        })

    return Response(
    json.dumps(output, ensure_ascii=False, indent=None),
    mimetype="application/json; charset=utf-8"
)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)