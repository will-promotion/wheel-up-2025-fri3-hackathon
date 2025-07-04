"""
recommend.py
────────────
・事前学習済み ja.vec/ja.bin を一度だけロード
・CSV トークン列も一度だけ生成してキャッシュ
・DB 講義ごとに最も類似度が高い CSV 講義 (Top1) を返す
"""

import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path
from gensim.models import KeyedVectors, FastText
from sklearn.metrics.pairwise import cosine_similarity
from janome.tokenizer import Tokenizer

# ---------- 設定 ----------
CSV_PATH   = "search/with_class_method.csv"
DB_PATH    = "school.db"
VEC_PATH   = "model.vec"          # .vec(テキスト) or .bin(Word2Vec/FastText)
IS_BINARY  = VEC_PATH.endswith(".bin")
DB_COLUMNS = ["name", "teacher"]  # ← DB列
CSV_TO_DB_MAP = {
    "科目名": "name",
    "担当教員": "teacher",
    "曜日": "day", "時限": "period",
    "使用教室": "room", "単位数": "credits",
    "成績評価方法": "evaluation",
    "授業形態": "style", "授業方法": "description",
}
WEIGHTS = {"name": 7, "teacher": 3}

tokenizer = Tokenizer(wakati=True)

# ---------- キャッシュ ----------
_kv: KeyedVectors | None           = None
_csv_df: pd.DataFrame | None       = None
_csv_tokens: list[list[str]] | None = None

# ---------- ユーティリティ ----------
def tokenize(text: str) -> list[str]:
    return list(tokenizer.tokenize(str(text)))

def load_kv() -> KeyedVectors:
    if VEC_PATH.endswith(".bin") and "fasttext" in VEC_PATH.lower():
        ft = FastText.load_facebook_model(VEC_PATH)
        return ft.wv
    return KeyedVectors.load_word2vec_format(VEC_PATH, binary=IS_BINARY)

def load_csv() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH).rename(columns=lambda c: c.strip())
    return pd.DataFrame({en: df[jp] for jp, en in CSV_TO_DB_MAP.items() if jp in df.columns})

def load_db() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql_query(f"SELECT {', '.join(DB_COLUMNS)} FROM subjects", conn)
    conn.close()
    return df

def tokens_from_row(row: pd.Series) -> list[str]:
    toks = []
    for col, rep in WEIGHTS.items():
        toks.extend(tokenize(row.get(col, "")) * rep)
    return toks

def sentence_vec(tokens: list[str], kv: KeyedVectors) -> np.ndarray:
    hits = [kv[t] for t in tokens if t in kv]
    return np.mean(hits, axis=0) if hits else np.zeros(kv.vector_size)

# ---------- 初期化 (一度だけ) ----------
def init_similarity_resources():
    global _kv, _csv_df, _csv_tokens
    if _kv is not None:
        return  # 既にロード済み
    _kv        = load_kv()
    _csv_df    = load_csv()
    _csv_tokens = [tokens_from_row(r) for _, r in _csv_df.iterrows()]

# ---------- 類似度検索 ----------
def search_similarity():
    init_similarity_resources()          # 必要ならロード
    db_df  = load_db()
    result = []

    csv_vecs = [sentence_vec(toks, _kv) for toks in _csv_tokens]

    for _, db_row in db_df.iterrows():
        db_vec = sentence_vec(tokens_from_row(db_row), _kv)

        best_idx, best_score = max(
            ((i, cosine_similarity([db_vec], [csv_vec])[0][0])
             for i, csv_vec in enumerate(csv_vecs)),
            key=lambda x: x[1]
        )

        result.append((db_row, _csv_df.iloc[best_idx], best_score))
    return result

# ---------- API 用 ----------
def get_similar_subjects():
    matches = search_similarity()
    output = []
    for db_row, csv_row, score in matches:
        output.append({
            "db": {
                "name":    db_row["name"],
                "teacher": db_row["teacher"]
            },
            "matched_csv": {
                "name":       csv_row.get("name", ""),
                "teacher":    csv_row.get("teacher", ""),
                "day":        csv_row.get("day", ""),
                "period":     csv_row.get("period", ""),
                "room":       csv_row.get("room", ""),
                "credits":    csv_row.get("credits", ""),
                "evaluation": csv_row.get("evaluation", ""),
                "style":      csv_row.get("style", "")
            },
            "score": round(float(score), 3)
        })
    return output

# ---------- テスト実行 ----------
if __name__ == "__main__":
    for item in get_similar_subjects():
        print(item)