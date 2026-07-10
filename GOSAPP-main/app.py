# -*- coding: utf-8 -*-
"""
Веб-приложение «Куда обратиться?»
Запуск: pip install flask
         python app.py
Открыть: http://localhost:5000
"""
import sqlite3
import os
from flask import Flask, request, render_template_string, redirect, url_for
from matcher import classify
from data import CATEGORIES

DB_PATH = os.path.join(os.path.dirname(__file__), "stats.db")
app = Flask(__name__)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            category_id TEXT,
            category_title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def log_request(text: str, category: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO requests (text, category_id, category_title) VALUES (?, ?, ?)",
        (text, category["id"], category["title"]),
    )
    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT category_title, COUNT(*) as cnt FROM requests GROUP BY category_title ORDER BY cnt DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


PAGE = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Куда обратиться?</title>
  <style>
    body { font-family: -apple-system, Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 16px; background:#f5f6f8; color:#1a1a1a;}
    h1 { font-size: 22px; }
    textarea { width: 100%; min-height: 90px; font-size: 16px; padding: 10px; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box;}
    button { margin-top: 10px; padding: 10px 20px; font-size: 16px; background:#1a73e8; color:#fff; border:none; border-radius:8px; cursor:pointer;}
    button:hover { background:#1558b0; }
    .card { background:#fff; border-radius: 10px; padding: 18px 20px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.1); white-space: pre-wrap; line-height: 1.5;}
    .examples { font-size: 13px; color: #666; margin-top: 6px;}
    .examples span { background:#eee; padding: 3px 8px; border-radius: 12px; margin-right:6px; cursor:pointer; display:inline-block; margin-bottom:6px;}
    a.statlink { font-size: 13px; color:#1a73e8; }
  </style>
</head>
<body>
  <h1>📍 Куда обратиться?</h1>
  <p>Опишите проблему — система подскажет, в какой государственный орган обратиться.</p>
  <form method="post">
    <textarea name="text" placeholder="Например: не выплачивают алименты">{{ query or '' }}</textarea><br>
    <button type="submit">Узнать, куда обратиться</button>
  </form>
  <div class="examples">
    Примеры:
    <span onclick="document.querySelector('textarea').value=this.innerText">Соседи шумят ночью</span>
    <span onclick="document.querySelector('textarea').value=this.innerText">Не убирают мусор во дворе</span>
    <span onclick="document.querySelector('textarea').value=this.innerText">Работодатель не выплачивает зарплату</span>
  </div>

  {% if result %}
  <div class="card">{{ result }}</div>
  {% endif %}

  <p style="margin-top:30px;"><a class="statlink" href="{{ url_for('stats') }}">📊 Статистика обращений →</a></p>
</body>
</html>
"""

STATS_PAGE = """
<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Статистика</title>
<style>
 body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; }
 table { width:100%; border-collapse: collapse; }
 td, th { padding: 8px 10px; border-bottom: 1px solid #ddd; text-align:left;}
</style>
</head>
<body>
<h1>📊 Самые частые обращения</h1>
<table>
<tr><th>Категория</th><th>Количество</th></tr>
{% for title, cnt in rows %}
<tr><td>{{ title }}</td><td>{{ cnt }}</td></tr>
{% endfor %}
</table>
<p><a href="{{ url_for('index') }}">← Назад</a></p>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    query = None
    if request.method == "POST":
        query = request.form.get("text", "").strip()
        if query:
            from matcher import format_response
            cat = classify(query)[0]
            log_request(query, cat)
            result = format_response(cat)
    return render_template_string(PAGE, result=result, query=query)


@app.route("/stats")
def stats():
    rows = get_stats()
    return render_template_string(STATS_PAGE, rows=rows)


if name == "__main__":
    init_db()
    app.run(debug=True, port=5000)