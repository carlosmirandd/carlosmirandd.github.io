#!/usr/bin/env python3
"""Gera o /journal estático a partir de journal/src/*.md.

Uso (na raiz do repositório):
    pip install markdown      # uma vez
    python3 journal/build.py

Cada post é um arquivo journal/src/<slug>.md começando com:
    ---
    title: título do post
    date: 2026-11-16
    description: uma linha que aparece na lista e no feed
    tags: tag-um, tag-dois
    draft: true               # opcional: não publica
    ---
Arquivos que começam com "_" são ignorados (ex.: _modelo.md).

Saída: journal/index.html, journal/<slug>/index.html e journal/index.xml (RSS).
Imagens dos posts ficam em img/journal/<slug>/ e entram no texto como
![legenda](/img/journal/<slug>/arquivo.webp).
"""
import email.utils
import datetime as dt
import html
import math
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("falta a biblioteca: pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
J = ROOT / "journal"
SRC = J / "src"
SITE = "https://carlosmirandd.github.io"
AUTHOR = "miranda"
SUBTITLE = "textos e anotações."
MARK = "<!-- gerado por journal/build.py -->"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

esc = html.escape


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        sys.exit(f"{path.name}: faltou o bloco --- no começo do arquivo")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    for k in ("title", "date"):
        if not meta.get(k):
            sys.exit(f"{path.name}: falta '{k}' no cabeçalho")
    try:
        date = dt.date.fromisoformat(meta["date"])
    except ValueError:
        sys.exit(f"{path.name}: a data deve ser AAAA-MM-DD")
    body = m.group(2).strip()
    words = len(re.findall(r"\w+", re.sub(r"```.*?```", " ", body, flags=re.S)))
    return {
        "slug": meta.get("slug") or path.stem,
        "title": meta["title"],
        "date": date,
        "description": meta.get("description", ""),
        "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "draft": meta.get("draft", "").lower() in ("1", "true", "sim", "yes"),
        "body": body,
        "minutes": max(1, math.ceil(words / 200)),
    }


def pt_date(d):
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def render_md(body):
    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "footnotes", "sane_lists", "attr_list", "md_in_html"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    out = md.convert(body)
    out = out.replace("<img ", '<img loading="lazy" ')
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener"', out)
    return out, md.toc_tokens


def toc_html(tokens):
    if sum(1 + len(t.get("children", [])) for t in tokens) < 2:
        return ""
    def li(t):
        kids = "".join(li(c) for c in t.get("children", []))
        kids = f"<ul>{kids}</ul>" if kids else ""
        return f'<li><a href="#{esc(t["id"])}">{esc(t["name"])}</a>{kids}</li>'
    return '<aside class="toc"><p class="tl">nesta página</p><ul>' + "".join(li(t) for t in tokens) + "</ul></aside>"


THEME_BTN = (
    '<button id="theme" type="button" aria-label="Alternar tema claro e escuro" title="Alternar tema">'
    '<svg class="i-sun" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
    '<svg class="i-moon" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>'
)
THEME_JS = (
    '<script>(function(){var r=document.documentElement,b=document.getElementById("theme");'
    'function cur(){return r.dataset.theme||"dark"}'
    'b.addEventListener("click",function(){var n=cur()==="dark"?"light":"dark";r.dataset.theme=n;'
    'try{localStorage.setItem("theme",n)}catch(e){}});})();</script>'
)


def page(title, description, body, path, wide=False, og_type="website"):
    url = f"{SITE}{path}"
    return f"""<!doctype html>
{MARK}
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/carlos.webp">
<meta name="theme-color" content="#070707">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/rss+xml" title="{AUTHOR}" href="/journal/index.xml">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='34' fill='%23ffd23f'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;1,400&family=Syne:wght@800&display=swap" rel="stylesheet">
<script>try{{var s=localStorage.getItem("theme");if(s==="light"||s==="dark")document.documentElement.dataset.theme=s}}catch(e){{}}</script>
<link rel="stylesheet" href="/journal/journal.css">
</head>
<body>
<div class="wrap{' wide' if wide else ''}">
  <header>
    <a class="home" href="/">~/{AUTHOR}</a>
    <nav><a href="/#projetos">projetos</a><a href="/journal/" aria-current="page">journal</a><a href="/journal/index.xml">rss</a>{THEME_BTN}</nav>
  </header>
{body}
  <footer>© {dt.date.today().year} {AUTHOR} · <a href="/journal/index.xml">rss</a></footer>
</div>
{THEME_JS}
</body>
</html>
"""


def list_page(posts):
    if posts:
        rows = "\n".join(
            f'      <li><a href="/journal/{esc(p["slug"])}/"><time datetime="{p["date"].isoformat()}">{pt_date(p["date"])}</time>'
            f'<span class="t"><b>{esc(p["title"])}</b>'
            + (f'<span class="d">{esc(p["description"])}</span>' if p["description"] else "")
            + f'</span><span class="r">{p["minutes"]} min</span></a></li>'
            for p in posts
        )
        lst = f'    <ul class="posts">\n{rows}\n    </ul>'
    else:
        lst = '    <p class="m">nada publicado ainda.</p>'
    body = f"""  <main class="col">
    <h1 class="jt">Journal</h1>
    <div class="rule"><i></i><b></b><i></i></div>
    <p class="sub">{esc(SUBTITLE)}</p>
    <h2>publicações</h2>
{lst}
  </main>"""
    return page(f"journal · {AUTHOR}", SUBTITLE, body, "/journal/")


def post_page(p, prev, nxt):
    content, tokens = render_md(p["body"])
    p["html"] = content
    tags = ", ".join(esc(t) for t in p["tags"])
    meta = f'<time datetime="{p["date"].isoformat()}">{pt_date(p["date"])}</time> · {p["minutes"]} min de leitura' + (f" · {tags}" if tags else "")
    nav = ""
    if prev or nxt:
        a = f'<a class="p" href="/journal/{esc(prev["slug"])}/"><span>← mais antigo</span>{esc(prev["title"])}</a>' if prev else "<span></span>"
        b = f'<a class="n" href="/journal/{esc(nxt["slug"])}/"><span>mais novo →</span>{esc(nxt["title"])}</a>' if nxt else "<span></span>"
        nav = f'\n      <nav class="pn">{a}{b}</nav>'
    sub = f'\n      <p class="sub">{esc(p["description"])}</p>' if p["description"] else ""
    body = f"""  <div class="post-grid">
    <article>
      <p class="meta">{meta}</p>
      <h1 class="pt">{esc(p["title"])}</h1>{sub}
      <hr>
      <div class="prose">
{content}
      </div>{nav}
    </article>
    {toc_html(tokens)}
  </div>"""
    return page(f'{p["title"]} · {AUTHOR}', p["description"] or p["title"], body, f'/journal/{p["slug"]}/', wide=True, og_type="article")


def absolutize(h):
    h = re.sub(r'(src|href)="/(?!/)', rf'\1="{SITE}/', h)
    return h


def feed(posts):
    now = email.utils.format_datetime(dt.datetime.now(dt.timezone.utc))
    last = email.utils.format_datetime(dt.datetime.combine(posts[0]["date"], dt.time(), dt.timezone.utc)) if posts else now
    items = []
    for p in posts:
        link = f'{SITE}/journal/{p["slug"]}/'
        pub = email.utils.format_datetime(dt.datetime.combine(p["date"], dt.time(), dt.timezone.utc))
        cats = "".join(f"\n  <category>{esc(t)}</category>" for t in p["tags"])
        items.append(
            f"""<item>
  <title>{esc(p["title"])}</title>
  <dc:creator>{AUTHOR}</dc:creator>
  <link>{link}</link>
  <description><![CDATA[ {p["description"]} ]]></description>{cats}
  <guid>{link}</guid>
  <pubDate>{pub}</pubDate>
  <content:encoded><![CDATA[ {absolutize(p["html"]).replace("]]>", "]]&gt;")} ]]></content:encoded>
</item>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     version="2.0">
<channel>
<title>{AUTHOR}</title>
<link>{SITE}/journal/</link>
<atom:link href="{SITE}/journal/index.xml" rel="self" type="application/rss+xml"/>
<description>{esc(SUBTITLE)}</description>
<generator>journal/build.py</generator>
<language>pt-BR</language>
<lastBuildDate>{last}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""


def main():
    posts = []
    for f in sorted(SRC.glob("*.md")):
        if f.name.startswith("_"):
            continue
        p = parse(f)
        if not p["draft"]:
            posts.append(p)
    slugs = [p["slug"] for p in posts]
    if len(slugs) != len(set(slugs)):
        sys.exit("dois posts com o mesmo slug")
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)

    # remove páginas geradas que não existem mais
    for d in J.iterdir():
        idx = d / "index.html"
        if d.is_dir() and d.name != "src" and idx.exists() and MARK in idx.read_text(encoding="utf-8") and d.name not in slugs:
            idx.unlink()
            d.rmdir()
            print("removido:", d.name)

    for i, p in enumerate(posts):
        nxt = posts[i - 1] if i > 0 else None            # mais novo
        prev = posts[i + 1] if i + 1 < len(posts) else None  # mais antigo
        out = J / p["slug"]
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(post_page(p, prev, nxt), encoding="utf-8")
    (J / "index.html").write_text(list_page(posts), encoding="utf-8")
    (J / "index.xml").write_text(feed(posts), encoding="utf-8")
    print(f"{len(posts)} post(s) publicados")


if __name__ == "__main__":
    main()
