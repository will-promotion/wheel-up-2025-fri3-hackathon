"""
similarity_by_n_similarity.py
─────────────────────────────
* 事前学習済み日本語 Word2Vec / FastText ベクトルをロード
* DB(subjects テーブル) 講義ごとに CSV( subjects.csv ) の講義の中で
  n_similarity によりスコア最大の 1 件を出力
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path
from gensim.models import KeyedVectors, FastText
from janome.tokenizer import Tokenizer

# ------------ 設定 ------------
CSV_PATH   = "search/with_class_method.csv"
DB_PATH    = "school.db"
VEC_PATH   = "model.vec"   # テキスト形式 (拡張子 .vec) or Word2Vecバイナリ(.bin)
IS_BINARY  = VEC_PATH.endswith(".bin")  # Trueならバイナリ
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

WEIGHTS = {
    "name": 7,     # token 重複数
    "teacher": 3
}

tokenizer = Tokenizer(wakati=True)

# ------------ ベクトルロード ------------
def load_kv(path: str) -> KeyedVectors:
    if not Path(path).exists():
        raise FileNotFoundError(f"ベクトルファイル {path} が見つかりません")
    # fastTextバイナリの場合
    if path.endswith(".bin") and "fasttext" in path.lower():
        ft = FastText.load_facebook_model(path)
        return ft.wv
    return KeyedVectors.load_word2vec_format(path, binary=IS_BINARY)

# ------------ データ読み込み ------------
def load_csv(path=CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(path).rename(columns=lambda c: c.strip())
    return pd.DataFrame({en: df[jp] for jp, en in CSV_TO_DB_MAP.items() if jp in df.columns})

def load_db(path=DB_PATH) -> pd.DataFrame:
    con = sqlite3.connect(path)
    df  = pd.read_sql_query(f"SELECT {', '.join(DB_COLUMNS)} FROM subjects", con)
    con.close()
    return df

# ------------ 行→トークン ------------
def tokens_from_row(row: pd.Series) -> list[str]:
    tokens = []
    for col, repeat in WEIGHTS.items():
        for _ in range(repeat):
            tokens.extend(tokenizer.tokenize(str(row.get(col, ""))))
    return tokens

# ------------ 類似度計算 ------------
def search_similarity():
    kv      = load_kv(VEC_PATH)
    csv_df  = load_csv()
    db_df   = load_db()

    csv_tokens_list = [tokens_from_row(r) for _, r in csv_df.iterrows()]

    results = []
    for _, db_row in db_df.iterrows():
        db_tokens = tokens_from_row(db_row)

        # 全 CSV と n_similarity
        best_idx, best_score = -1, -1.0
        for idx, csv_tokens in enumerate(csv_tokens_list):
            # Unknown 単語除外
            t1 = [t for t in db_tokens  if t in kv]
            t2 = [t for t in csv_tokens if t in kv]
            if not t1 or not t2:   # どちらか空なら類似度 0
                score = 0.0
            else:
                score = kv.n_similarity(t1, t2)
            if score > best_score:
                best_idx, best_score = idx, score

        results.append((db_row, csv_df.iloc[best_idx], best_score))
    return results


def get_similar_subjects():
    """
    DB内の講義それぞれに対して、最も類似するCSV講義を取得するAPI
    """
    from recommend import search_similarity  # 必要に応じてファイル名を変更
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


# ------------ メイン ------------
if __name__ == "__main__":
    output = get_similar_subjects()
    print(output)