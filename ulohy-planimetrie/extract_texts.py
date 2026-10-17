"""Vytáhne všechny namluvené texty ze scén (volání say/intro/summary) do texts.json."""
import ast
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def default_final():
    tree = ast.parse(open(os.path.join(ROOT, "common.py"), encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "summary":
            for arg, d in zip(reversed(node.args.args), reversed(node.args.defaults)):
                if arg.arg == "final":
                    return d.value
    return None


def texts_in(path):
    out = []
    tree = ast.parse(open(path, encoding="utf-8").read())
    has_summary = False
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        name = node.func.attr
        pos = {"say": 0, "intro": 1, "summary": 2}.get(name)
        if pos is None:
            continue
        if name == "summary":
            has_summary = True
            for kw in node.keywords:
                if kw.arg == "final" and isinstance(kw.value, ast.Constant) and kw.value.value:
                    out.append((node.lineno, kw.value.value))
                    has_summary = "custom"
        args = node.args
        if len(args) > pos and isinstance(args[pos], ast.Constant) and isinstance(args[pos].value, str):
            out.append((node.lineno, args[pos].value))
        for kw in node.keywords:
            if kw.arg in ("narration", "text") and isinstance(kw.value, ast.Constant):
                out.append((node.lineno, kw.value.value))
    out.sort()
    texts = [t for _, t in out]
    if has_summary is True:
        texts.append(default_final())
    return texts


if __name__ == "__main__":
    from common import audio_key, norm_text
    files = sorted(glob.glob(os.path.join(ROOT, "scenes", "s*.py")))
    items, seen = [], set()
    for f in files:
        for t in texts_in(f):
            k = audio_key(t)
            if k not in seen:
                seen.add(k)
                items.append({"key": k, "text": norm_text(t), "scene": os.path.basename(f)})
    json.dump(items, open(os.path.join(ROOT, "texts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    have = sum(os.path.exists(os.path.join(ROOT, "audio", i["key"] + ".wav")) for i in items)
    chars = sum(len(i["text"]) for i in items)
    print(f"{len(items)} textů, {chars} znaků (~{chars / 15 / 60:.1f} min), audio hotové: {have}")
