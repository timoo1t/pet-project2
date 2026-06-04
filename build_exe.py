"""Сборка EXE: python build_exe.py → dist\\QuizApp.exe"""

import subprocess
import sys


def main():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    sep = ";" if sys.platform == "win32" else ":"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--console",
        "--name",
        "QuizApp",
        "--add-data",
        f"questions.json{sep}.",
        "--add-data",
        f"templates{sep}templates",
        "--add-data",
        f"static{sep}static",
        "quiz_app.py",
    ]
    print("Запуск:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(__import__("pathlib").Path(__file__).resolve().parent))
    print("\nГотово: dist\\QuizApp.exe")


if __name__ == "__main__":
    main()
