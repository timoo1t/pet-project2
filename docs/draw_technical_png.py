# -*- coding: utf-8 -*-
"""Рисует technical.png без PlantUML: только квадраты, ромбики, стрелки."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "technical.png"
FONT_PATH = Path(r"C:\Windows\Fonts\arial.ttf")

W = 480
MARGIN = 24
BOX_W = W - 2 * MARGIN
BOX_FILL = "#DAE8FC"
BOX_BORDER = "#6C8EBF"
DIAMOND_FILL = "#FFF2CC"
DIAMOND_BORDER = "#D6B656"
BG = "#F5F5F5"
GRID = "#E0E0E0"
TEXT = "#333333"
ARROW = "#6C8EBF"


def load_font(size: int):
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size)
    return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            test = f"{line} {word}"
            if draw.textlength(test, font=font) <= max_w:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def text_block_height(lines, font, line_gap=3):
    ascent, descent = font.getmetrics()
    h = ascent + descent
    return len(lines) * (h + line_gap) - line_gap


def draw_grid(img):
    draw = ImageDraw.Draw(img)
    for x in range(0, W, 20):
        draw.line([(x, 0), (x, img.height)], fill=GRID, width=1)
    for y in range(0, img.height, 20):
        draw.line([(0, y), (W, y)], fill=GRID, width=1)


class Chart:
    def __init__(self):
        self.font = load_font(11)
        self.font_b = load_font(12)
        self.title_font = load_font(14)
        self.y = 20
        self.img = Image.new("RGB", (W, 4000), BG)
        self.draw = ImageDraw.Draw(self.img)
        self.cx = W // 2

    def arrow(self, gap=12):
        x = self.cx
        y1 = self.y
        self.y += gap
        y2 = self.y
        self.draw.line([(x, y1), (x, y2)], fill=ARROW, width=1)
        self.draw.polygon([(x, y2), (x - 5, y2 - 8), (x + 5, y2 - 8)], fill=ARROW)

    def box(self, text: str, min_h: int = 44):
        font = self.font
        pad = 10
        lines = wrap(self.draw, text, font, BOX_W - 2 * pad)
        th = text_block_height(lines, font)
        h = max(min_h, th + 2 * pad)
        x1 = MARGIN
        y1 = self.y
        x2 = MARGIN + BOX_W
        y2 = y1 + h
        self.draw.rectangle([x1, y1, x2, y2], fill=BOX_FILL, outline=BOX_BORDER, width=1)
        ty = y1 + pad
        for line in lines:
            self.draw.text((x1 + pad, ty), line, fill=TEXT, font=font)
            ty += font.getmetrics()[0] + font.getmetrics()[1] + 3
        self.y = y2
        return y2

    def diamond(self, text: str):
        font = self.font
        pad = 8
        lines = wrap(self.draw, text, font, BOX_W - 80)
        th = text_block_height(lines, font)
        size = max(70, th + 2 * pad)
        cx, cy = self.cx, self.y + size // 2
        pts = [(cx, cy - size // 2), (cx + size // 2, cy), (cx, cy + size // 2), (cx - size // 2, cy)]
        self.draw.polygon(pts, fill=DIAMOND_FILL, outline=DIAMOND_BORDER, width=1)
        ty = cy - th // 2
        for line in lines:
            lw = self.draw.textlength(line, font=font)
            self.draw.text((cx - lw / 2, ty), line, fill=TEXT, font=font)
            ty += font.getmetrics()[0] + font.getmetrics()[1] + 2
        self.y = cy + size // 2

    def label(self, text: str):
        font = self.font_b
        lw = self.draw.textlength(text, font=font)
        self.draw.text(((W - lw) / 2, self.y), text, fill=TEXT, font=font)
        self.y += font.getmetrics()[0] + font.getmetrics()[1] + 8

    def save(self):
        crop = self.img.crop((0, 0, W, self.y + 30))
        draw_grid(crop)
        crop.save(OUT, "PNG")
        print(f"OK: {OUT} ({OUT.stat().st_size} bytes, {crop.size[0]}x{crop.size[1]})")


def main():
    c = Chart()
    title = "Техническая блок-схема quiz_app.py"
    tw = c.draw.textlength(title, font=c.title_font)
    c.draw.text(((W - tw) / 2, c.y), title, fill=TEXT, font=c.title_font)
    c.y += 28

    c.label("1. Импорты")
    c.box("json, sys, threading, webbrowser\ndatetime, Path\nFlask, redirect, render_template\nrequest, session, url_for")
    c.arrow()

    c.label("2. Конфигурация")
    c.box("_resource_dir()  _writable_dir()\nAPP_DIR, DATA_DIR\nQUESTIONS_FILE, RESULTS_FILE\nFlask: template_folder, static_folder, secret_key")
    c.arrow()

    c.label("3. Данные")
    c.box("questions.json → Question (question, options, correct)\nSessionState (player_name, topic, index, score, total, answers)\nAnswerRecord (question, chosen, correct, is_correct)\nresults.txt — лог")
    c.arrow()

    c.label("4. Запуск __main__")
    c.diamond("questions.json\nесть?")
    c.arrow(8)
    c.box("Timer → браузер\napp.run(127.0.0.1:5000)")
    c.arrow()

    c.label("5. index  GET /")
    c.box("session.clear()\nload_questions(), get_topics()\nrender index.html")
    c.arrow()

    c.label("6. start  POST /start")
    c.diamond("topic в списке\nтем?")
    c.arrow(8)
    c.box("session: player_name, topic\nindex=0, score=0, answers=[]\ntotal = len(questions)\nredirect /question")
    c.arrow()

    c.label("7. ЦИКЛ (пока index < total)")
    c.box("GET /question\nget_questions, idx = index")
    c.arrow(6)
    c.diamond("idx >= len\nвопросов?")
    c.arrow(8)
    c.box("render question.html")
    c.arrow(6)
    c.box("POST /answer\nchosen vs correct, score++\nanswers.append, index++\nredirect /question")
    c.arrow(6)
    c.diamond("index < total?")
    c.arrow()

    c.label("8. result  GET /result")
    c.diamond("все ответы\nданы?")
    c.arrow(8)
    c.box("save_result → results.txt\nrender result.html")
    c.arrow()

    c.label("9. restart  GET /restart")
    c.box("session.clear()\nredirect /  → снова шаг 5")

    c.save()


if __name__ == "__main__":
    main()
