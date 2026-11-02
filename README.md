# X Article Paste

A skill for coding agents. It turns a long-form draft into an HTML file you copy from a browser, so headings and bold survive a paste into the X Articles editor.

X Articles reads the clipboard's `text/html` flavor. A copy from a `.txt`, `.md`, or TextEdit window is plain text, so the paste lands flat.

## What's here

- `SKILL.md` — when to use the skill and how the draft should be shaped
- `scripts/article_to_paste_html.py` — Python 3 standard-library converter

## Convert a draft

```bash
python3 scripts/article_to_paste_html.py \
  "My Article.md" \
  --out "My Article - X Article formatted.html" \
  --open
```

The script maps `## ` to `<h2>`, `### ` to `<h3>`, `**bold**` to `<strong>`, and `_italic_` to `<em>`. Horizontal rules are dropped. The page includes a yellow instruction box above the article. Select only the article text below that box, then copy.

Put the title in X's Title field. The HTML does not include an `<h1>`.

## Install as a skill

Copy this folder into your agent's skills directory, for example `~/.grok/skills/x-article-paste`.
