"""Generate the site from content/ into HTML pages."""

from __future__ import annotations

import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
PROJECTS_SRC = CONTENT / "projects"


def load_site() -> dict:
    page = parse_page(CONTENT / "home.md")
    return {
        "name": page.get("name", "Naysan Munje"),
        "role": page.get("role", "Engineer"),
        "email": page.get("email", ""),
        "github": page.get("github", ""),
        "linkedin": page.get("linkedin", ""),
        "phone": page.get("phone", ""),
        "resume": page.get("resume", "Naysan_Munje_Resume.pdf?v=2"),
        "bio": page["body"],
    }


def parse_page(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        frontmatter = re.match(
            r"^---\s*\n(.*?)\n---\s*(?:\n|$)(.*)$",
            text,
            re.DOTALL,
        )
        if not frontmatter:
            raise ValueError(f"Invalid page header in {path}")
        header, body = frontmatter.groups()
        for line in header.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    meta["body"] = body.strip()
    meta["slug"] = path.parent.name
    meta.setdefault("title", meta["slug"])
    meta.setdefault("subtitle", "")
    meta.setdefault("preview", "")
    meta.setdefault("date", "")
    meta.setdefault("github", "")
    meta.setdefault("thumbnail", "")
    meta.setdefault("order", "100")
    return meta


def inline_md(text: str) -> str:
    text = escape(text)
    text = re.sub(r"!\[(.*?)\]\((.*?)\)", r'<img alt="\1" src="\2" />', text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def is_video_url(line: str) -> bool:
    return bool(
        re.match(
            r"https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|vimeo\.com/)",
            line.strip(),
        )
    )


def video_embed(url: str) -> str:
    url = url.strip()
    yt = re.search(r"(?:v=|youtu\.be/)([\w-]+)", url)
    if yt:
        src = f"https://www.youtube.com/embed/{yt.group(1)}"
        return f'<iframe src="{src}" title="Project video" allowfullscreen></iframe>'
    vimeo = re.search(r"vimeo\.com/(\d+)", url)
    if vimeo:
        src = f"https://player.vimeo.com/video/{vimeo.group(1)}"
        return f'<iframe src="{src}" title="Project video" allowfullscreen></iframe>'
    return f'<p><a href="{escape(url)}">{escape(url)}</a></p>'


def is_solo_image(block: str) -> re.Match[str] | None:
    return re.fullmatch(r"!\[(.*?)\]\((.*?)\)", block.strip())


def render_blocks(body: str) -> str:
    chunks: list[str] = []
    for block in re.split(r"\n\s*\n", body.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith(":::text-columns\n") and block.endswith(":::"):
            column_html = []
            inner = block.removeprefix(":::text-columns\n").removesuffix(":::").strip()
            for column in inner.split("\n|||\n"):
                lines = column.splitlines()
                heading = inline_md(lines[0])
                items = "".join(
                    f"<li>{inline_md(line[2:])}</li>"
                    for line in lines[1:]
                    if line.startswith("- ")
                )
                column_html.append(
                    f"<section><h2>{heading}</h2><ul>{items}</ul></section>"
                )
            chunks.append(f'<div class="text-columns">{"".join(column_html)}</div>')
            continue
        if block.startswith(":::grid-with-image ") and block.endswith(":::"):
            sources = block.splitlines()[0].removeprefix(":::grid-with-image ").split()
            grid_images = "".join(
                f'<img alt="" src="{escape(source)}" />' for source in sources[:-1]
            )
            side_image = escape(sources[-1])
            chunks.append(
                f'<div class="grid-with-image">'
                f'<div class="media-gallery media-gallery-compact">{grid_images}</div>'
                f'<img class="grid-side-image" alt="" src="{side_image}" />'
                f"</div>"
            )
            continue
        if block.startswith(":::gallery") and block.endswith(":::"):
            directive, *sources = block.splitlines()[0].split()
            modifiers = {
                ":::gallery-small-second": " media-gallery-small-second",
                ":::gallery-equal": " media-gallery-equal",
                ":::gallery-compact": " media-gallery-compact",
                ":::gallery-contained": " media-gallery-contained",
            }
            modifier = modifiers.get(directive, "")
            images = "".join(
                f'<img alt="" src="{escape(source)}" />' for source in sources
            )
            chunks.append(f'<div class="media-gallery{modifier}">{images}</div>')
            continue
        if is_video_url(block):
            chunks.append(video_embed(block))
            continue
        image = is_solo_image(block)
        if image:
            alt, src = image.group(1), image.group(2)
            chunks.append(
                f'<figure class="media-below">'
                f'<img alt="{escape(alt)}" src="{escape(src)}" />'
                f"</figure>"
            )
            continue
        if block.startswith("### "):
            chunks.append(f"<h3>{inline_md(block[4:])}</h3>")
            continue
        if block.startswith("## "):
            chunks.append(f"<h2>{inline_md(block[3:])}</h2>")
            continue
        if block.startswith("# "):
            chunks.append(f"<h1>{inline_md(block[2:])}</h1>")
            continue
        lines = block.splitlines()
        if all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{inline_md(line[2:])}</li>" for line in lines)
            chunks.append(f"<ul>{items}</ul>")
            continue
        chunks.append(f"<p>{inline_md(block).replace('\n', '<br />')}</p>")
    return "\n".join(chunks)


BESIDE_RE = re.compile(
    r"^:::beside(?:-(left|right))?\s+([^\n]+)\s*\n(.*?):::\s*$",
    re.MULTILINE | re.DOTALL,
)


def render_md(body: str) -> str:
    chunks: list[str] = []
    pos = 0
    for match in BESIDE_RE.finditer(body):
        chunks.append(render_blocks(body[pos : match.start()]))
        side = match.group(1) or "right"
        sources = match.group(2).split()
        text = render_blocks(match.group(3))
        images = "".join(
            f'<img alt="" src="{escape(source)}" />' for source in sources
        )
        chunks.append(
            f'<div class="beside beside-{side}">'
            f'<div class="beside-text">{text}</div>'
            f'<div class="beside-media">{images}</div>'
            f"</div>"
        )
        pos = match.end()
    chunks.append(render_blocks(body[pos:]))
    return "\n".join(chunk for chunk in chunks if chunk)


def load_projects() -> list[dict]:
    projects = []
    if not PROJECTS_SRC.exists():
        return projects
    for folder in PROJECTS_SRC.iterdir():
        page = folder / "index.md"
        if folder.is_dir() and page.exists():
            projects.append(parse_page(page))
    projects.sort(key=lambda p: (int(p["order"]), p["title"]))
    return projects


def extras(slug: str) -> list[dict]:
    folder = PROJECTS_SRC / slug
    pages = []
    for path in sorted(folder.glob("*.md")):
        if path.name == "index.md":
            continue
        page = parse_page(path)
        page["slug"] = path.stem
        pages.append(page)
    return pages


def chrome(site: dict, depth: int) -> tuple[str, str, str]:
    prefix = "../" * depth
    name = escape(site["name"])
    resume = escape(site["resume"])
    home = f"{prefix}index.html"
    projects = f"{prefix}projects/index.html"
    resume_href = f"{prefix}{resume}"
    header = f"""      <header>
        <a class="logo" href="{home}">{name}</a>
        <nav>
          <a href="{home}">Home</a>
          <a href="{projects}">Projects</a>
          <a href="{resume_href}" target="_blank" rel="noopener">Resume</a>
        </nav>
      </header>"""
    footer_bits = [f'<a href="mailto:{escape(site["email"])}">{escape(site["email"])}</a>']
    if site.get("linkedin"):
        footer_bits.append(
            f'<a href="{escape(site["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>'
        )
    if site.get("phone"):
        phone = site["phone"]
        footer_bits.append(
            f'<a href="tel:{escape(phone.replace("-", ""))}">{escape(phone)}</a>'
        )
    footer = f"""      <footer>
        {" ".join(footer_bits)}
      </footer>"""
    style_version = int((ROOT / "src" / "style.css").stat().st_mtime)
    css = f"{prefix}src/style.css?v={style_version}"
    return header, footer, css


def wrap(title: str, css: str, header: str, main: str, footer: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{css}" />
  </head>
  <body>
    <div class="page">
{header}

      <main>
{main}
      </main>

{footer}
    </div>
  </body>
</html>
"""


def project_card(project: dict, href: str) -> str:
    subtitle = escape(project["subtitle"])
    preview = escape(project["preview"])
    thumbnail = ""
    if project["thumbnail"]:
        project_path = href.rsplit("/", 1)[0]
        thumbnail_src = escape(f"{project_path}/{project['thumbnail']}")
        thumbnail = (
            f'<span class="project-thumb">'
            f'<img src="{thumbnail_src}" alt="" />'
            f"</span>"
        )
    return f"""          <li>
            <a href="{href}">
              {thumbnail}
              <span class="title">{escape(project["title"])}</span>
              <span class="subtitle">{subtitle}</span>
              <span class="preview">{preview}</span>
            </a>
          </li>"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def copy_assets(slug: str) -> None:
    src = PROJECTS_SRC / slug
    dest = ROOT / "projects" / slug
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.suffix.lower() in {".md", ".pdf", ".docx", ".txt"}:
            continue
        target = dest / item.name
        if item.is_file():
            shutil.copy2(item, target)
        elif item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)


def extra_links(pages: list[dict]) -> str:
    if not pages:
        return ""
    items = "".join(
        f'<li><a href="{escape(p["slug"])}/index.html">{escape(p["title"])}</a></li>'
        for p in pages
    )
    return f"<h2>More</h2>\n        <ul>{items}</ul>"


def github_line(url: str) -> str:
    if not url:
        return ""
    return f'          <p><a href="{escape(url)}">GitHub</a></p>'


def build() -> None:
    site = load_site()
    projects = load_projects()

    header, footer, css = chrome(site, 0)
    bio = "\n".join(
        f"        {line}" if line else ""
        for line in render_md(site["bio"]).splitlines()
    )
    cards = "\n".join(
        project_card(p, f"projects/{p['slug']}/index.html") for p in projects
    )
    home_main = f"""        <h1>{escape(site["name"])}</h1>
        <p class="role">{escape(site["role"])}</p>
{bio}
        <h2>Projects</h2>
        <ul class="project-grid">
{cards}
        </ul>
        <ul class="contact-list">
          <li><a href="{escape(site["github"])}">GitHub</a></li>
          <li><a href="{escape(site["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a></li>
          <li><a href="tel:{escape(site["phone"].replace("-", ""))}">{escape(site["phone"])}</a></li>
          <li><a href="{escape(site["resume"])}" target="_blank" rel="noopener">Resume</a></li>
        </ul>"""
    write(ROOT / "index.html", wrap(site["name"], css, header, home_main, footer))

    header, footer, css = chrome(site, 1)
    cards = "\n".join(project_card(p, f"{p['slug']}/index.html") for p in projects)
    list_main = f"""        <h1>Projects</h1>
        <ul class="project-grid">
{cards}
        </ul>"""
    write(
        ROOT / "projects" / "index.html",
        wrap(f"Projects — {site['name']}", css, header, list_main, footer),
    )

    for project in projects:
        copy_assets(project["slug"])
        more = extras(project["slug"])
        header, footer, css = chrome(site, 2)
        date = (
            f'          <span class="date">{escape(project["date"])}</span>\n'
            if project["date"]
            else ""
        )
        body = render_md(project["body"])
        indented = "\n".join(
            f"          {line}" if line else "" for line in body.splitlines()
        )
        main = f"""        <article>
          <h1>{escape(project["title"])}</h1>
{date}{indented}
{github_line(project["github"])}
          {extra_links(more)}
        </article>"""
        write(
            ROOT / "projects" / project["slug"] / "index.html",
            wrap(
                f"{project['title']} — {site['name']}",
                css,
                header,
                main,
                footer,
            ),
        )
        for page in more:
            header, footer, css = chrome(site, 3)
            body = render_md(page["body"])
            indented = "\n".join(
                f"          {line}" if line else "" for line in body.splitlines()
            )
            main = f"""        <article>
          <p><a href="../index.html">Back to {escape(project["title"])}</a></p>
          <h1>{escape(page["title"])}</h1>
{indented}
        </article>"""
            write(
                ROOT / "projects" / project["slug"] / page["slug"] / "index.html",
                wrap(
                    f"{page['title']} — {site['name']}",
                    css,
                    header,
                    main,
                    footer,
                ),
            )


if __name__ == "__main__":
    build()
    print("Built site from content/")
