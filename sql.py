#!/usr/bin/env python3
"""
school_db.py
曜日・時限分離 + 拡張項目版の時間割データベース（SQLite）

列一覧
  id          INTEGER  主キー
  weekday     TEXT     曜日 (月, Tue ...)
  period      INTEGER  時限 (1, 2 ...)
  name        TEXT     教科名
  room        TEXT     教室名
  credits     INTEGER  単位数
  teacher     TEXT     教員名
  evaluation  TEXT     評価割合
  style       TEXT     授業形態
  description TEXT     授業内容
  memo        TEXT     メモ
  ease        INTEGER  楽さ (1‒5 等)
  timetable   TEXT     旧まとめ列（互換用）
"""

import sqlite3
from contextlib import closing
from pathlib import Path

# ────────────────────────────────────────────────────────────────
# 基本設定
# ────────────────────────────────────────────────────────────────
_DB_PATH = Path("school.db").expanduser()


# ────────────────────────────────────────────────────────────────
# 1. DB 初期化 & スキーマ拡張
# ────────────────────────────────────────────────────────────────
def init_db() -> None:
    """subjects テーブルを作成 or 不足列を自動追加"""
    expected_cols = {
        "weekday":     "TEXT",
        "period":      "INTEGER",
        "name":        "TEXT",
        "room":        "TEXT",
        "credits":     "INTEGER",
        "teacher":     "TEXT",
        "evaluation":  "TEXT",
        "style":       "TEXT",
        "description": "TEXT",
        "memo":        "TEXT",
        "ease":        "INTEGER",
        "timetable":   "TEXT",  # 旧列
    }

    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute("PRAGMA table_info(subjects)")
        existing = {row[1] for row in cur.fetchall()}

        if not existing:
            # 新規 DB
            cols_sql = ",\n".join(
                ["id INTEGER PRIMARY KEY AUTOINCREMENT"] +
                [f"{c} {t}" for c, t in expected_cols.items()]
            )
            con.executescript(f"CREATE TABLE subjects (\n{cols_sql}\n);")
            return

        # 既存 DB: 不足列を追加
        for col, coltype in expected_cols.items():
            if col not in existing:
                con.execute(f"ALTER TABLE subjects ADD COLUMN {col} {coltype};")


def migrate_old_timetable() -> None:
    """旧 timetable='月3' を weekday='月', period=3 へ補完（不足行のみ）"""
    with sqlite3.connect(_DB_PATH) as con, con:
        con.execute("""
            UPDATE subjects
            SET weekday = SUBSTR(timetable, 1, 1),
                period  = CAST(SUBSTR(timetable, 2) AS INTEGER)
            WHERE timetable IS NOT NULL AND weekday IS NULL;
        """)


# ────────────────────────────────────────────────────────────────
# 2. CRUD 関数
# ────────────────────────────────────────────────────────────────
def add_subject(
    weekday: str,
    period: int,
    name: str,
    room: str,
    credits: int | None = None,
    teacher: str | None = None,
    evaluation: str | None = None,
    style: str | None = None,
    description: str | None = None,
    memo: str | None = None,
    ease: int | None = None,
) -> int:
    """科目を追加し、挿入IDを返す"""
    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            """
            INSERT INTO subjects
              (weekday, period, name, room, credits, teacher, evaluation,
               style, description, memo, ease, timetable)
            VALUES (?,?,?,?,?,?,?,?,?,?,?, NULL)
            """,
            (
                weekday, period, name, room, credits, teacher,
                evaluation, style, description, memo, ease,
            ),
        )
        return cur.lastrowid


def delete_by_id(id_: int) -> bool:
    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute("DELETE FROM subjects WHERE id = ?", (id_,))
        return cur.rowcount > 0


def delete_by_name(name: str, delete_all: bool = True) -> int:
    sql = (
        "DELETE FROM subjects WHERE id IN "
        "(SELECT id FROM subjects WHERE name = ? ORDER BY id LIMIT 1)"
        if not delete_all
        else "DELETE FROM subjects WHERE name = ?"
    )
    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(sql, (name,))
        return cur.rowcount


def list_subjects() -> list[tuple]:
    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            """
            SELECT id, weekday, period, name, room,
                   credits, teacher, ease
            FROM subjects
            ORDER BY weekday, period, id
            """
        )
        return cur.fetchall()


def detail_subject(id_: int) -> tuple | None:
    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute("SELECT * FROM subjects WHERE id = ?", (id_,))
        return cur.fetchone()


# ────────────────────────────────────────────────────────────────
# 3. インタラクティブ CLI
# ────────────────────────────────────────────────────────────────
def main() -> None:
    init_db()
    migrate_old_timetable()   # ← 旧 timetable 列があれば補完

    help_msg = """
【コマンド】
  add       : 科目を追加
  delid     : id を指定して削除
  delname   : 教科名で削除（全件）
  delone    : 教科名で削除（最初の 1 件）
  list      : 一覧表示
  detail    : id を指定して詳細表示
  help      : ヘルプ
  exit/quit : 終了
"""

    print("=== School DB interactive mode ===")
    print(help_msg)

    while True:
        cmd = input("> ").strip().lower()

        # ────────── 追加 ──────────
        if cmd == "add":
            wd   = input("  曜日 (月/Tue ...) : ").strip()
            per  = input("  時限 (数字)      : ").strip()
            name = input("  教科名           : ").strip()
            room = input("  教室名           : ").strip()

            cred = input("  単位数           : ").strip() or None
            teach = input("  教員             : ").strip() or None
            eval_ = input("  評価割合         : ").strip() or None
            style = input("  授業形態         : ").strip() or None
            desc  = input("  授業内容         : ").strip() or None
            memo  = input("  メモ             : ").strip() or None
            ease  = input("  楽さ(1-5)        : ").strip() or None

            try:
                per_i  = int(per)
                cred_i = int(cred) if cred else None
                ease_i = int(ease) if ease else None
            except ValueError:
                print("  ⚠ 数値欄に数字以外が入っています")
                continue

            new_id = add_subject(
                wd, per_i, name, room, cred_i, teach, eval_,
                style, desc, memo, ease_i
            )
            print(f"  [Add] id={new_id} : {wd}{per_i}限 / {name}")

        # ──────── id 削除 ─────────
        elif cmd == "delid":
            try:
                id_ = int(input("  id: ").strip())
                msg = "[Delete] id={}" if delete_by_id(id_) else "ℹ id={} は見つかりません"
                print("  " + msg.format(id_))
            except ValueError:
                print("  ⚠ 数字を入力してください")

        # ──────── 教科名削除 ────────
        elif cmd == "delname":
            name = input("  教科名: ").strip()
            n = delete_by_name(name, delete_all=True)
            print(f"  [Delete] name={name} rows={n}")

        elif cmd == "delone":
            name = input("  教科名: ").strip()
            n = delete_by_name(name, delete_all=False)
            print(f"  [DeleteOne] name={name} rows={n}")

        # ────────── 一覧 ───────────
        elif cmd == "list":
            rows = list_subjects()
            if not rows:
                print("  (empty)")
            else:
                for (_id, wd, per, name, room, cr, t, es) in rows:
                    wd_s   = wd or "-"                       # None → '-'
                    per_s  = f"{per}限" if per is not None else "-"
                    cr_s   = f"{cr}単位" if cr is not None else "-"
                    es_s   = f"楽さ{es}" if es is not None else "-"
                    t_s    = t or "-"
                    room_s = room or "-"

                    print(f"  {_id:3} | {wd_s:<2} | {per_s:<3} | {name:<16} | "
                          f"{room_s:<8} | {cr_s:<6} | {t_s:<6} | {es_s}")

        # ────────── 詳細 ───────────
        elif cmd == "detail":
            try:
                id_ = int(input("  id: ").strip())
            except ValueError:
                print("  ⚠ 数字を入力してください")
                continue
            row = detail_subject(id_)
            if row:
                cols = [
                    "id", "weekday", "period", "name", "room",
                    "credits", "teacher", "evaluation", "style",
                    "description", "memo", "ease", "timetable"
                ]
                print(" ─── detail ───")
                for c, v in zip(cols, row):
                    print(f" {c:12}: {v}")
            else:
                print("  ℹ 見つかりません")

        # ────────── その他 ──────────
        elif cmd in {"help", "?", ""}:
            print(help_msg)
        elif cmd in {"exit", "quit"}:
            print("bye!")
            break
        else:
            print("  ❓ 未定義コマンドです。'help' で確認してください")


# ────────────────────────────────────────────────────────────────
# エントリポイント
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

# ────────────────────────────────────────────────────────────────
# Webアプリ用の関数
# ────────────────────────────────────────────────────────────────

def get_all_subjects():
    """全ての科目を辞書のリストで返す（Webアプリ用）"""
    with sqlite3.connect(_DB_PATH) as con:
        cur = con.execute(
            """
            SELECT id, weekday, period, name, room,
                   credits, teacher, evaluation, style,
                   description, memo, ease
            FROM subjects
            ORDER BY weekday, period, id
            """
        )
        rows = cur.fetchall()
        
        # 辞書のリストに変換
        subjects = []
        for row in rows:
            subjects.append({
                'id': row[0],
                'day': row[1],  # weekdayをdayとして返す
                'period': str(row[2]),  # periodを文字列として返す
                'name': row[3],
                'room': row[4],
                'credits': row[5],
                'teacher': row[6],
                'evaluation': row[7],
                'style': row[8],
                'description': row[9],
                'memo': row[10],
                'ease': row[11]
            })
        return subjects

def add_subject_web(name: str, day: str, period: str, room: str = "", **kwargs):
    """科目を追加（Webアプリ用の簡易版）"""
    try:
        period_int = int(period)
        return add_subject(day, period_int, name, room, **kwargs)
    except ValueError:
        raise ValueError("時限は数字で入力してください")

def delete_subject(subject_id: int):
    """科目を削除（Webアプリ用）"""
    return delete_by_id(subject_id)

def update_subject_time(subject_id: int, new_day: str, new_period: int):
    """科目の時間を更新（Webアプリ用）"""
    with sqlite3.connect(_DB_PATH) as con:
        con.execute(
            "UPDATE subjects SET weekday = ?, period = ? WHERE id = ?",
            (new_day, new_period, subject_id)
        )
        return con.total_changes > 0