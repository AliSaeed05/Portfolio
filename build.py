#!/usr/bin/env python3
"""Builds index.html from index.template.html + projects.json.

Usage:  python3 build.py
No dependencies (Python 3.7+). Re-run after editing projects.json,
adding images, or editing index.template.html.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
warnings = []


def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """Escape text; **bold** becomes <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(s))


def exists(rel):
    return os.path.isfile(os.path.join(ROOT, rel))


def body_html(lines):
    """Tiny markup: '- ' bullet, '> ' context note, anything else a paragraph."""
    out, bullets = [], []

    def flush():
        if bullets:
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for line in lines:
        if line.startswith("- "):
            bullets.append(line[2:])
            continue
        flush()
        if line.startswith("> "):
            out.append(f'<p class="context">{inline(line[2:])}</p>')
        else:
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return "".join(out)


VIDEO_OK = (".mp4", ".m4v", ".webm", ".ogv", ".mov")
VIDEO_BAD = (".wmv", ".avi", ".mkv", ".flv", ".mpg", ".mpeg", ".3gp")


def is_video(path):
    return path.lower().endswith(VIDEO_OK)


def normalize_images(p):
    """Accept 'file.jpg' or {file, alt, caption}; drop files that do not exist."""
    imgs = []
    for i, item in enumerate(p.get("images", []), 1):
        d = {"file": item} if isinstance(item, str) else dict(item)
        f = d.get("file", "")
        path = f if "/" in f else "images/" + f
        if f.lower().endswith(VIDEO_BAD):
            warnings.append(f"{p['id']}: {f} cannot play in web browsers. Convert it to MP4 (H.264); see README. Skipped.")
            continue
        if not exists(path):
            warnings.append(f"{p['id']}: image not found, skipped: {path}")
            continue
        d["path"] = path
        d["video"] = is_video(path)
        size_mb = os.path.getsize(os.path.join(ROOT, path)) / 1e6
        if d["video"] and size_mb > 25:
            warnings.append(f"{p['id']}: {f} is {size_mb:.0f} MB; compress it (README) so the page stays fast. GitHub blocks files over 100 MB.")
        elif not d["video"] and size_mb > 2:
            warnings.append(f"{p['id']}: {f} is {size_mb:.1f} MB; consider resizing to about 1600 px wide.")
        d.setdefault("alt", "")
        if not d["alt"]:
            warnings.append(f"{p['id']}: {f} has no alt text (describe it in projects.json)")
            d["alt"] = f"{p['title']}, {'video' if d['video'] else 'image'} {i}"
        d.setdefault("caption", "")
        imgs.append(d)
    return imgs


def lb_link(img, cls=""):
    cap = f' data-caption="{esc(img["caption"])}"' if img["caption"] else ""
    if img["video"]:
        poster = ""
        src = esc(img["path"])
        if img.get("poster") and exists("images/" + img["poster"] if "/" not in img["poster"] else img["poster"]):
            pp = img["poster"] if "/" in img["poster"] else "images/" + img["poster"]
            poster = f' poster="{esc(pp)}"'
            src_attr = src
        else:
            src_attr = src + "#t=0.1"
        return (
            f'<figure class="slot {cls}"><a class="lb is-video" href="{src}" data-type="video" data-alt="{esc(img["alt"])}"{cap}'
            f' aria-label="Play video: {esc(img["alt"])}">'
            f'<video src="{src_attr}"{poster} muted playsinline preload="metadata" tabindex="-1" aria-hidden="true"></video>'
            f'<span class="play" aria-hidden="true"></span></a></figure>'
        )
    return (
        f'<figure class="slot {cls}"><a class="lb" href="{esc(img["path"])}" data-alt="{esc(img["alt"])}"{cap}>'
        f'<img src="{esc(img["path"])}" alt="{esc(img["alt"])}" loading="lazy" decoding="async"></a></figure>'
    )


def media_html(p, imgs):
    if imgs:
        main = lb_link(imgs[0])
        rest = imgs[1:]
        thumbs = ""
        if rest:
            n = len(rest)
            cols = 1 if n == 1 else 2 if n in (2, 4) else 3
            thumbs = f'<div class="thumbs cols{cols}">' + "".join(lb_link(i, "thumb") for i in rest) + "</div>"
        return f'<div class="media">{main}{thumbs}</div>'
    d = p.get("diagram", "")
    if d and exists(d):
        label = p.get("diagram_label", "Illustrative diagram")
        return (
            f'<div class="media"><figure class="slot diagram"><img src="{esc(d)}" alt="" loading="lazy">'
            f'<figcaption class="tag">{esc(label)}</figcaption></figure></div>'
        )
    return ""


def project_html(p):
    imgs = normalize_images(p)
    media = media_html(p, imgs)
    if not imgs:
        warnings.append(f"{p['id']}: no images yet (showing {'diagram' if media else 'no visual'})")
    rows = [("Role", p.get("role")), ("Status", p.get("status")), ("Dates", p.get("dates")), ("Tools", p.get("tools"))]
    spec = "".join(
        f'<div><dt>{k}</dt><dd>{"<span class=status>" + esc(v) + "</span>" if k == "Status" else esc(v)}</dd></div>'
        for k, v in rows if v
    )
    sections = "".join(
        f'<div class="cs"><h4>{esc(s["heading"])}</h4>{body_html(s.get("body", []))}</div>'
        for s in p.get("sections", [])
    )
    case = ""
    if sections:
        case = (
            f'<details class="case"><summary><span>Case study: {esc(p["title"])}</span>'
            f'<span class="toggle-icon" aria-hidden="true"></span></summary>'
            f'<div class="case-body">{sections}<p class="permalink"><a href="#{esc(p["id"])}">Link to this project</a></p></div></details>'
        )
    cls = "proj-grid" + ("" if media else " no-media")
    summary = f'<p class="oneline">{esc(p["summary"])}</p>' if p.get("summary") else ""
    return (
        f'\n<article class="project" id="{esc(p["id"])}" aria-labelledby="{esc(p["id"])}-h">'
        f'<div class="{cls}">{media}<div class="info"><h3 id="{esc(p["id"])}-h">{esc(p["title"])}</h3>'
        f'{summary}<dl class="spec">{spec}</dl></div></div>{case}</article>'
    )


def index_html(projects):
    rows = ""
    for p in projects:
        status = esc(p.get("status", ""))
        if p.get("dates"):
            status += f'<br><span class="small">{esc(p["dates"])}</span>'
        rows += (
            f'<tr><td><a href="#{esc(p["id"])}">{esc(p["title"])}</a></td>'
            f'<td class="hide-sm">{esc(p.get("role", ""))}</td><td>{status}</td>'
            f'<td class="hide-sm">{esc(p.get("tools", ""))}</td></tr>'
        )
    return (
        '<table class="index"><caption class="sr-only">Project index</caption><thead><tr>'
        '<th scope="col">Project</th><th scope="col" class="hide-sm">Role</th><th scope="col">Status</th>'
        '<th scope="col" class="hide-sm">Tools</th></tr></thead><tbody>' + rows + "</tbody></table>"
    )


def site_slot(name, alt, label):
    for ext in ("jpg", "jpeg", "png", "webp"):
        rel = f"images/{name}.{ext}"
        if exists(rel):
            return f'<figure class="slot tall"><img src="{rel}" alt="{esc(alt)}"></figure>'
    warnings.append(f"{name}: no images/{name}.jpg|png|webp yet (placeholder box is showing)")
    return (
        f'<figure class="slot tall"><div class="ph empty" aria-hidden="true"><span class="tag">{esc(label)}</span>'
        f'<span class="file">images/{name}.jpg</span></div></figure>'
    )


def main():
    with open(os.path.join(ROOT, "projects.json"), encoding="utf-8") as f:
        data = json.load(f)
    site = data.get("site", {})
    projects = [p for p in data["projects"] if not p.get("hidden")]

    seen = set()
    for p in projects:
        for key in ("id", "title"):
            if not p.get(key):
                sys.exit(f"ERROR: a project is missing '{key}': {p}")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", p["id"]):
            sys.exit(f"ERROR: id '{p['id']}' must be lowercase letters, numbers, and hyphens only")
        if p["id"] in seen:
            sys.exit(f"ERROR: duplicate id '{p['id']}'")
        seen.add(p["id"])

    feat = [p for p in projects if p.get("group", "featured") == "featured"]
    supp = [p for p in projects if p.get("group") == "supporting"]
    parts = ""
    if feat:
        parts += '<h3 class="group">Featured projects</h3>' + "".join(project_html(p) for p in feat)
    if supp:
        parts += '<h3 class="group">Supporting projects</h3>' + "".join(project_html(p) for p in supp)

    with open(os.path.join(ROOT, "index.template.html"), encoding="utf-8") as f:
        t = f.read()
    t = (
        t.replace("{{INDEX}}", index_html(feat + supp))
        .replace("{{PROJECTS}}", parts)
        .replace("{{HERO_SLOT}}", site_slot("hero", site.get("hero_alt", ""), "Hero photo"))
        .replace("{{ABOUT_SLOT}}", site_slot("about", site.get("about_alt", ""), "Portrait or workspace photo"))
    )
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(t)
    print(f"Built index.html with {len(projects)} projects ({len(feat)} featured, {len(supp)} supporting).")
    for w in warnings:
        print("  note:", w)


if __name__ == "__main__":
    main()
