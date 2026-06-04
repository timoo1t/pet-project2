"""Генерация PNG из .puml (локальный plantuml.jar или сервер plantuml.com)."""

import re
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
JAR = DOCS / "plantuml.jar"


def split_diagrams(puml_path: Path) -> list[tuple[str, str]]:
    text = puml_path.read_text(encoding="utf-8")
    blocks = re.findall(r"(@startuml.*?@enduml)", text, flags=re.DOTALL)
    result = []
    for block in blocks:
        name_match = re.search(r"@startuml\s+(\S+)", block)
        name = name_match.group(1) if name_match else puml_path.stem
        result.append((name, block.strip() + "\n"))
    return result


def render_local(source: str, out_png: Path) -> bool:
    tmp = DOCS / "_tmp_render.puml"
    tmp.write_text(source, encoding="utf-8")
    cmd = ["java", "-jar", str(JAR), "-tpng", "-charset", "UTF-8", str(tmp)]
    proc = subprocess.run(cmd, cwd=str(DOCS), capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    generated = DOCS / f"{out_png.stem}.png"
    if generated.exists() and generated != out_png:
        generated.replace(out_png)
    if proc.returncode != 0:
        err = DOCS / f"{out_png.stem}_error.txt"
        err.write_text(proc.stderr or proc.stdout, encoding="utf-8")
        print(f"  ОШИБКА: {err.name}")
        return False
    return out_png.exists()


def render_remote(source: str, out_png: Path) -> bool:
    from plantuml import PlantUML

    server = PlantUML(url="http://www.plantuml.com/plantuml/png/")
    try:
        content = server.processes(source)
    except Exception as exc:
        (DOCS / f"{out_png.stem}_error.txt").write_text(str(exc), encoding="utf-8")
        print(f"  ОШИБКА сервера: {exc}")
        return False
    out_png.write_bytes(content)
    return True


def main():
    use_local = JAR.exists()
    if not use_local:
        print("plantuml.jar не найден — используется plantuml.com")

    for puml_file in sorted(DOCS.glob("uml-*.puml")):
        for name, source in split_diagrams(puml_file):
            out = DOCS / f"{name}.png"
            print(f"Генерация {out.name}...")
            ok = (
                render_local(source, out)
                if use_local
                else render_remote(source, out)
            )
            if ok:
                print(f"  OK: {out} ({out.stat().st_size} байт)")


if __name__ == "__main__":
    main()
