#!/usr/bin/env python3
"""Convert a plain-text/markdown draft into paste-ready HTML for X Articles.

X Articles (a Draft.js editor) keeps formatting only when the clipboard carries
the text/html flavor, which it maps as <h2> -> heading, <strong> -> bold.
Copying from a .txt or TextEdit window gives it plain text and everything lands
flat. This script produces an HTML page whose body can be selected in a browser
and pasted into the editor with its structure intact.

Usage:
    python3 article_to_paste_html.py DRAFT.md [--out OUT.html] [--open] [--title T]

Supported source syntax:
    ## Heading          -> <h2>
    ### Heading         -> <h3>
    **bold**            -> <strong>
    _italic_            -> <em>
    - item              -> <ul><li>
    blank line          -> paragraph break
    ---                 -> dropped (no rule survives as a paragraph)
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

PAGE_CSS = """
  body { max-width: 640px; margin: 40px auto; padding: 0 20px;
         font: 19px/1.6 -apple-system, "Helvetica Neue", Arial, sans-serif;
         color: #0f1419; }
  h2 { font-size: 24px; line-height: 1.25; margin: 44px 0 18px; }
  h3 { font-size: 20px; line-height: 1.3; margin: 32px 0 14px; }
  p  { margin: 0 0 20px; }
  ul { margin: 0 0 20px; padding-left: 22px; }
  li { margin: 0 0 10px; }
  strong { font-weight: 700; }
  .note { max-width: 640px; margin: 0 auto 32px; padding: 12px 16px;
          background: #fff8dc; border: 1px solid #e6d9a2; border-radius: 8px;
          font-size: 14px; line-height: 1.5; color: #4a4433; }
""".strip()

NOTE_BOX = """<div class="note">
  <b>How to use:</b> select only the article text below this box
  (click just before the first heading, then Shift-click after the last line),
  copy, and paste into the X Article editor. Headings and bold survive the paste.
</div>"""

BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC = re.compile(r"(?<!\w)_([^_]+?)_(?!\w)", re.S)


def inline(text: str) -> str:
    """Escape HTML, then re-apply bold and italic as real tags."""
    out = html.escape(text, quote=False)
    out = BOLD.sub(r"<strong>\1</strong>", out)
    out = ITALIC.sub(r"<em>\1</em>", out)
    return out


def blocks_from(source: str) -> list[str]:
    """Split on blank lines, dropping horizontal rules."""
    chunks: list[str] = []
    current: list[str] = []

    for raw in source.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if current:
                chunks.append("\n".join(current))
                current = []
            continue
        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", line.strip()):
            continue
        current.append(line)

    if current:
        chunks.append("\n".join(current))
    return chunks


def render_body(source: str) -> tuple[str, list[str]]:
    """Return (html body, list of section headings found)."""
    parts: list[str] = []
    headings: list[str] = []

    for chunk in blocks_from(source):
        lines = chunk.splitlines()
        first = lines[0]

        if first.startswith("### "):
            parts.append(f"<h3>{inline(first[4:].strip())}</h3>")
            headings.append(first[4:].strip())
            rest = lines[1:]
            if rest:
                parts.append(f"<p>{inline(' '.join(l.strip() for l in rest))}</p>")
            continue

        if first.startswith("## "):
            text = first[3:].strip()
            parts.append(f"<h2>{inline(text)}</h2>")
            headings.append(text)
            rest = lines[1:]
            if rest:
                parts.append(f"<p>{inline(' '.join(l.strip() for l in rest))}</p>")
            continue

        if all(l.lstrip().startswith(("- ", "* ")) for l in lines):
            items = "".join(
                f"<li>{inline(l.lstrip()[2:].strip())}</li>" for l in lines
            )
            parts.append(f"<ul>{items}</ul>")
            continue

        parts.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")

    return "\n\n".join(parts), headings


def build_html(source: str, title: str) -> tuple[str, list[str]]:
    body, headings = render_body(source)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
{PAGE_CSS}
</style>
</head>
<body>

{NOTE_BOX}

{body}

</body>
</html>
"""
    return doc, headings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build a paste-ready HTML file for the X Articles editor."
    )
    parser.add_argument("source", type=Path, help="draft file (.md or .txt)")
    parser.add_argument("--out", type=Path, help="output .html path")
    parser.add_argument("--title", help="page <title>; defaults to first heading")
    parser.add_argument("--open", action="store_true", help="open in the browser")
    args = parser.parse_args(argv)

    if not args.source.is_file():
        print(f"error: no such file: {args.source}", file=sys.stderr)
        return 1

    source = args.source.read_text(encoding="utf-8")
    doc, headings = build_html(source, args.title or "X Article draft")

    out = args.out or args.source.with_name(
        args.source.stem + " - X Article formatted.html"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")

    words = len(source.split())
    print(f"wrote {out}")
    print(f"  {words} words, {len(headings)} section headings")
    if headings:
        print("  headings: " + " / ".join(headings))
    print("  copy in browser: click before the first heading,")
    print("  Shift-click after the last line, then copy.")

    if args.open:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        try:
            subprocess.run([opener, str(out)], check=False)
        except FileNotFoundError:
            print(f"  (open manually: {out})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
