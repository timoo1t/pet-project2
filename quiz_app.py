# -*- coding: utf-8 -*-
"""Викторина на Flask. Запуск: python quiz_app.py или dist\\QuizApp.exe"""

import json
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

def _resource_dir() -> Path:
    """Папка с шаблонами, CSS и questions.json (в EXE — временная _MEIPASS)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _writable_dir() -> Path:
    """Папка для results.txt (рядом с EXE или со скриптом)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_DIR = _resource_dir()
DATA_DIR = _writable_dir()
QUESTIONS_FILE = APP_DIR / "questions.json"
RESULTS_FILE = DATA_DIR / "results.txt"

app = Flask(
    __name__,
    template_folder=str(APP_DIR / "templates"),
    static_folder=str(APP_DIR / "static"),
)
app.secret_key = "quiz-secret-change-in-production"


def load_questions():
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_topics():
    return list(load_questions().keys())


def get_questions(topic: str):
    return load_questions().get(topic, [])


def save_result(player_name: str, topic: str, score: int, total: int):
    line = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"{player_name or 'Гость'} | {topic} | {score}/{total} "
        f"({round(100 * score / total) if total else 0}%)\n"
    )
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(line)


@app.route("/")
def index():
    session.clear()
    return render_template("index.html", topics=get_topics())


@app.route("/start", methods=["POST"])
def start():
    topic = request.form.get("topic", "").strip()
    if topic not in get_topics():
        return redirect(url_for("index"))

    session["player_name"] = request.form.get("player_name", "").strip() or "Гость"
    session["topic"] = topic
    session["index"] = 0
    session["score"] = 0
    session["answers"] = []
    session["total"] = len(get_questions(topic))
    return redirect(url_for("question"))


@app.route("/question")
def question():
    topic = session.get("topic")
    if not topic:
        return redirect(url_for("index"))

    questions = get_questions(topic)
    idx = session.get("index", 0)
    if idx >= len(questions):
        return redirect(url_for("result"))

    return render_template(
        "question.html",
        question=questions[idx],
        number=idx + 1,
        total=len(questions),
        player_name=session.get("player_name", "Гость"),
        topic=topic,
    )


@app.route("/answer", methods=["POST"])
def answer():
    topic = session.get("topic")
    if not topic:
        return redirect(url_for("index"))

    questions = get_questions(topic)
    idx = session.get("index", 0)
    if idx >= len(questions):
        return redirect(url_for("result"))

    try:
        chosen = int(request.form.get("answer", -1))
    except ValueError:
        chosen = -1

    correct = questions[idx]["correct"]
    is_correct = chosen == correct
    if is_correct:
        session["score"] = session.get("score", 0) + 1

    answers = session.get("answers", [])
    answers.append(
        {
            "question": questions[idx]["question"],
            "chosen": chosen,
            "correct": correct,
            "is_correct": is_correct,
        }
    )
    session["answers"] = answers
    session["index"] = idx + 1
    return redirect(url_for("question"))


@app.route("/result")
def result():
    topic = session.get("topic")
    if not topic:
        return redirect(url_for("index"))

    questions = get_questions(topic)
    total = len(questions)
    score = session.get("score", 0)
    player = session.get("player_name", "Гость")
    answers = session.get("answers", [])

    if len(answers) == total and total > 0:
        save_result(player, topic, score, total)

    return render_template(
        "result.html",
        player_name=player,
        topic=topic,
        score=score,
        total=total,
        answers=answers,
        questions=questions,
    )


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not QUESTIONS_FILE.exists():
        raise SystemExit(f"Не найден файл вопросов: {QUESTIONS_FILE}")

    print("Викторина: http://127.0.0.1:5000/")
    print("Остановка: Ctrl+C")
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000/")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
