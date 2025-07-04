import sqlite3
import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
# ============================
# 定数と設定
# ============================
DB_COLUMNS = ["name", "teacher"]
CSV_TO_DB_MAP = {
    "科目名": "name",
    "担当教員": "teacher",
    "曜日": "day",
    "時限": "period",
    "使用教室": "room",
    "単位数": "credits",
    "成績評価方法": "evaluation",
    "授業形態": "style",
    "授業方法": "description",
}
WEIGHTS = {"name": 0.7, "teacher": 0.3}

# ============================
# トークナイザ（文字単位）
# ============================
def tokenize(text):
    return list(str(text))

# ============================
# 文ベクトルの取得（加重平均）
# ============================
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

# ============================
# 文リストを生成
# ============================
def dataframe_to_sentences(df):
    return [
        [token for col in WEIGHTS.keys() for token in tokenize(row[col])]
        for _, row in df.iterrows()
    ]

# ============================
# データ読み込み
# ============================
def load_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip() for col in df.columns]
    return pd.DataFrame({CSV_TO_DB_MAP[jp]: df[jp] for jp in CSV_TO_DB_MAP if jp in df.columns})

def load_db(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT {', '.join(DB_COLUMNS)} FROM subjects", conn)
    conn.close()
    return df

# ============================
# 類似度比較
# ============================
def compute_similarity(db_df, csv_df, model):
    results = []
    csv_vecs = [sentence_vector(row, model) for _, row in csv_df.iterrows()]
    for i, db_row in db_df.iterrows():
        db_vec = sentence_vector(db_row, model)
        sims = [(j, cosine_similarity([db_vec], [csv_vec])[0][0])
                for j, csv_vec in enumerate(csv_vecs)]
        sims.sort(key=lambda x: x[1], reverse=True)
        top3 = sims[:3]
        results.append((db_row, [(csv_df.iloc[j], score) for j, score in top3]))
    return results

# ============================
# メイン処理
# ============================

def search_similarity():
    # CSVとDBの読み込み
    csv_path = "search/with_class_method.csv"
    db_path = "school.db"

    csv_df = load_csv(csv_path)
    db_df = load_db(db_path)

    # 文リストの生成
    sentences = dataframe_to_sentences(pd.concat([csv_df, db_df], ignore_index=True))

    # Word2Vecモデルの学習
    model = Word2Vec(sentences=sentences, vector_size=100, window=5, min_count=1, workers=4)

    # 類似度計算
    results = compute_similarity(db_df, csv_df, model)

    # Top1 のみ抽出
    similarity = []
    for db_row, top_matches in results:
        if top_matches:  # 念のため空チェック
            csv_row, score = top_matches[0]  # 最もスコアが高いものだけ
            similarity.append((db_row, csv_row, score))

    return similarity
    
def get_similar_subjects():
    """
    DB内の講義それぞれに対して、最も類似するCSV講義を取得するAPI
    """
    from reccomend import search_similarity  # 必要に応じてファイル名を変更
    results = search_similarity()

    # JSON形式に整形
    output = []
    for db_row, csv_row, score in results:
        output.append({
            "db": {
                "name": db_row.get("name", ""),
                "teacher": db_row.get("teacher", "")
            },
            "matched_csv": {
                "name": csv_row.get("name", ""),
                "teacher": csv_row.get("teacher", ""),
                "day": csv_row.get("day", ""),
                "period": csv_row.get("period", ""),
                "room": csv_row.get("room", ""),
                "credits": csv_row.get("credits", ""),
                "evaluation": csv_row.get("evaluation", ""),
                "style": csv_row.get("style", ""),
            },
            "score": round(float(score), 3)
        })

    return output

if __name__ == "__main__":
    results = get_similar_subjects()
    print(results)
