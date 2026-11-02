---
name: X Article Paste
description: Produces draft text plus a paste-ready HTML file so headings and bold survive being copied into the X (Twitter) Articles editor. Use when the user wants a long-form post organized or rewritten for an X Article, asks for something to "copy-paste into X", asks why formatting disappeared after pasting, or wants an article/thread draft exported to a file.
---

# X Article Paste

X Articles is a Draft.js rich-text editor. It reads the clipboard's `text/html`
flavor and maps tags to blocks: `<h2>` becomes a heading, `<strong>` becomes
bold. Anything the user copies from a `.txt`, `.md`, or TextEdit window carries
only `text/plain`, so it always pastes flat — that is never a bug in the draft,
it is the clipboard missing a flavor.

So the deliverable is never just "a text file". It is an **HTML file the user
copies from a browser**, plus the draft itself.

## Workflow

1. **Get the source.** If the source is an existing article, fetch it before
   editing anything. For an X long-form Article the status text is only a
   `t.co` link — the body is a separate document, and the X API returns just
   `article.title`. Read the body with Moli:
   `moli fetch --dump markdown --wait-until domstable "<x.com status URL>"`.
   The article body renders without login.
2. **Restructure before formatting.** Formatting cannot rescue a wall of text.
   Apply the shaping rules below first, and get the user's agreement on the cut.
3. **Write the draft** to `~/Downloads/<descriptive-name>.md`. Never the
   Desktop unless the user names a Desktop path.
4. **Convert it** with the bundled script (Python 3 stdlib only):

   ```bash
   python3 scripts/article_to_paste_html.py \
     ~/Downloads/"My Article.md" \
     --out ~/Downloads/"My Article - X Article formatted.html" \
     --open
   ```

   The script maps `## ` → `<h2>`, `### ` → `<h3>`, blank-line-separated blocks
   → `<p>`, `**bold**` → `<strong>`, `_italic_` → `<em>`, and drops `---`.
   It wraps the body in a page styled for reading and prefixes a yellow
   instruction box that sits outside the selection the user should copy.
5. **Tell the user the copy gesture precisely:** click just before the first
   heading, Shift-click just after the last line, `⌘C`, then paste into the
   Article body. Selecting the whole page (`⌘A`) would drag the instruction box
   in too.
6. **Title goes in the separate Title field**, not the body. Never emit an
   `<h1>`; X renders it far too large next to the title field.
7. **Report the path and the fallback** in the same message.

## Shaping the draft

A collection of lines and an essay fail the same way: no entrance point. Before
exporting:

- **One idea per paragraph.** A blank line between every aphorism, quote, or
  point. Never join them with `·`, `|`, or run them together to save space.
- **Cap the sections.** Around seven headings is the ceiling for a short piece;
  each should hold five to eight blocks so one section fits on one screen.
- **Cut hard and say what you cut.** 100+ items is a 10-minute read most people
  abandon. Offer the trim, keep the rejected lines in the chat so the user can
  pull them back.
- **No sub-headings, no italic subtitles, no epigraph per section.** They read
  as an essay; the user asked for something scannable.
- **Bold sparingly.** One phrase per section, as an eye anchor. Bold everything
  and nothing is emphasized.
- Keep the user's own wording. Fix punctuation, typos, and recasing; do not
  quietly rewrite their sentences.

## HTML rules that matter

| Do | Why |
| --- | --- |
| `<h2>` for sections | `<h1>` fights the Title field; `<h3>` is too small to scan |
| `<p>` per block, blank line between | Becomes separate paragraphs with real spacing |
| `<strong>` for at most one phrase per section | Survives the paste; drives the eye |
| Body text at 19px/1.6, `max-width: 640px` | Matches X's reading column, so the copy looks like the result |
| Instruction box outside the copy range | Prevents the how-to text landing in the article |
| Straight apostrophes and quotes | Curly quotes can arrive mangled |

Avoid: tables, `<blockquote>`, `<code>`, `<ul>` for prose, images, inline
styles on every element (X strips most of them), and any literal markdown
syntax — `#`, `*`, and `---` show up as characters in the editor.

## Fallback ladder

1. **Browser copy** (default) — `open` the HTML in Safari or Chrome, select the
   body range, copy. Cleanest `text/html` payload.
2. **Pages or Word** — open the draft there and copy; the clipboard carries RTF,
   which X also understands. Use when no browser is available.
3. **Manual styling** — if headings arrive as paragraphs (X changes its paste
   handling from time to time), everything else still carries. Select each
   heading line and apply the heading style once; with ~7 headings that is
   under a minute. Say this explicitly instead of letting the user discover it.
4. **Plain text is the last resort** — only if the user says formatting does
   not matter.

## Verifying the clipboard

`pbpaste` only shows the plain flavor, so it cannot confirm a formatted copy.
Check for the HTML flavor instead:

```bash
osascript -e 'clipboard info' | grep -i html
```

A match means the browser copy worked and the paste will keep its structure.
No match means the user copied from a text editor.

## Reporting

State the file path, its size and word count, the exact copy gesture, where the
title goes, and what to do if headings come through flat. Describe saved state
plainly — which files are on disk — and do not mention git, commits, or
version-control state.

## Note on duplication

This skill is installed identically under `~/.config/opencode/skills`,
`~/.claude/skills`, and `~/.grok/skills`. Keep the three copies in sync: edit
one, then mirror it to the other two.
