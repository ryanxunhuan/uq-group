#!/usr/bin/env python3
"""Check generated static pages using only Python's standard library."""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit


SITE_ROOT = Path(__file__).resolve().parent
MIN_NEWS = 240
MIN_BIBLIOGRAPHY = 101
STORY_COUNT = 9
BASES = ("https://example.github.io/", "https://example.github.io/group-site/")
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
REVIEW_PATTERNS = (
    r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?=[:/])",
    r"customize_changeset_uuid",
    r"(?:\?|&|&amp;)(?:preview|page_id|preview_id)=",
    r"/wp-admin/",
    r"draft\s+review\s+index",
    r"saved\s+offline\s+snapshot",
    r"offline\s+(?:WordPress\s+)?(?:draft|review\s+copy)",
    r"(?:href|src)=[\"'][^\"']*(?:review|directory)\.html",
)


class Page(HTMLParser):
    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.ids: Counter[str] = Counter()
        self.refs: list[tuple[str, str]] = []
        self.images = 0
        self.missing_alts = 0
        self.h1s = 0
        self.title_parts: list[str] = []
        self.description = ""
        self.news = 0
        self.bibliography = 0
        self.stories = 0
        self.base_tags = 0
        self.css: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if attributes.get("id"):
            self.ids[attributes["id"]] += 1
        if tag == "a" and attributes.get("name"):
            self.ids[attributes["name"]] += 1
        if tag == "base":
            self.base_tags += 1
        if tag == "h1":
            self.h1s += 1
        if tag == "meta" and (attributes.get("name") or "").lower() == "description":
            self.description = (attributes.get("content") or "").strip()
        if tag == "img":
            self.images += 1
            if "alt" not in attributes:
                self.missing_alts += 1
        for name in ("href", "src", "poster"):
            value = attributes.get(name)
            if value:
                self.refs.append((name, value))
        if attributes.get("srcset"):
            for part in attributes["srcset"].split(","):
                value = part.strip().split()
                if value:
                    self.refs.append(("srcset", value[0]))
        if attributes.get("style"):
            self.css.append(attributes["style"])
        if tag == "li" and (attributes.get("id") or "").startswith("news-"):
            self.news += 1
        if tag == "li" and any("bibliography" in (a.get("class") or "").split() for _, a in self.stack):
            self.bibliography += 1
        if tag == "article" and "project-card" in classes:
            self.stories += 1
        if tag not in VOID_TAGS:
            self.stack.append((tag, attributes))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if any(tag == "title" for tag, _ in self.stack):
            self.title_parts.append(data)
        if self.stack and self.stack[-1][0] == "style":
            self.css.append(data)


def css_urls(text):
    for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", text, re.S):
        yield match.group(2).strip()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("directory", nargs="?", type=Path, default=SITE_ROOT / "public")
    args = cli.parse_args()
    public = args.directory.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks = Counter()
    html_files = sorted(public.glob("*.html"))
    pages: dict[Path, Page] = {}

    def fail(message):
        errors.append(message)

    if not public.is_dir():
        fail(f"Output directory is missing: {public}. Run python3 build.py first.")

    expected = {p.name for p in (SITE_ROOT / "content" / "pages").glob("*.html")}
    # The homepage is assembled from content/home.html and the news archive.
    expected.update(("index.html", "404.html"))
    actual = {p.name for p in html_files}
    if expected != actual:
        fail(f"Page inventory differs: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    if len(expected) < 23:
        fail(f"Expected at least 22 content pages and 404.html; found {len(expected)} source page names.")

    titles = Counter()
    for path in html_files:
        source = path.read_text(encoding="utf-8")
        page = Page(path)
        page.feed(source)
        pages[path.resolve()] = page
        title = "".join(page.title_parts).strip()
        titles[title] += 1
        if not title:
            fail(f"{path.name}: missing page title")
        if page.h1s != 1:
            fail(f"{path.name}: expected one h1, found {page.h1s}")
        if not page.description:
            fail(f"{path.name}: missing meta description")
        if page.missing_alts:
            fail(f"{path.name}: {page.missing_alts} images have no alt attribute")
        if page.base_tags:
            fail(f"{path.name}: base tag can break repository-relative links")
        for identity, count in page.ids.items():
            if count > 1:
                fail(f"{path.name}: duplicate anchor id {identity!r}")
        for pattern in REVIEW_PATTERNS:
            if re.search(pattern, source, re.I):
                fail(f"{path.name}: development-only content matches {pattern!r}")
        checks["images"] += page.images

    for title, count in titles.items():
        if title and count > 1:
            fail(f"Page title used {count} times: {title!r}")

    def check_ref(owner: Path, attribute: str, value: str):
        value = value.strip()
        parts = urlsplit(value)
        if parts.scheme or parts.netloc:
            if parts.scheme == "javascript":
                fail(f"{owner.name}: javascript URL in {attribute}")
            checks["external_or_special_urls"] += 1
            return
        if value.startswith("/"):
            # A 404 is served at the missing URL, potentially in any directory.
            # Its single home link is configured by --base-path at build time.
            if owner.name == "404.html" and attribute == "href" and parts.path.endswith("/index.html"):
                if not (public / "index.html").is_file():
                    fail("404.html: configured home link has no generated index.html")
                elif any(part in (".", "..") for part in unquote(parts.path).split("/")):
                    fail("404.html: configured home link contains path traversal")
                else:
                    checks["configured_404_home_links"] += 1
                return
            fail(f"{owner.name}: root-relative {attribute} {value!r} breaks repository hosting")
            return
        for base in BASES:
            owner_url = urljoin(base, owner.relative_to(public).as_posix())
            resolved = urlsplit(urljoin(owner_url, value))
            base_path = urlsplit(base).path
            if not resolved.path.startswith(base_path):
                fail(f"{owner.name}: {value!r} escapes site prefix {base_path}")
                return
            relative = unquote(resolved.path[len(base_path):])
            target = (public / relative).resolve()
            if target.is_dir():
                target = target / "index.html"
            try:
                target.relative_to(public)
            except ValueError:
                fail(f"{owner.name}: {value!r} resolves outside site directory")
                return
            if not target.is_file():
                fail(f"{owner.name}: missing local {attribute} target {value!r}")
                return
            if resolved.fragment and target.suffix.lower() == ".html":
                fragment = unquote(resolved.fragment)
                target_page = pages.get(target)
                # Text-fragment navigation need not name an element id.
                if not fragment.startswith(":~:text=") and (not target_page or fragment not in target_page.ids):
                    fail(f"{owner.name}: missing anchor in {value!r}")
                    return
            checks["resolved_local_urls"] += 1

    for path, page in pages.items():
        for attribute, ref in page.refs:
            check_ref(path, attribute, ref)
        for css in page.css:
            for ref in css_urls(css):
                check_ref(path, "inline CSS url", ref)
    for path in sorted(public.rglob("*.css")):
        for ref in css_urls(path.read_text(encoding="utf-8")):
            check_ref(path, "CSS url", ref)
        checks["stylesheets"] += 1

    news = pages.get(public / "news.html")
    homepage = pages.get(public / "index.html")
    bibliography = pages.get(public / "bibliography.html")
    stories = pages.get(public / "stories.html")
    counts = {
        "news_entries": news.news if news else 0,
        "bibliography_entries": bibliography.bibliography if bibliography else 0,
        "research_stories": stories.stories if stories else 0,
        "homepage_news_entries": homepage.news if homepage else 0,
    }
    if counts["news_entries"] < MIN_NEWS:
        fail(f"News archive has {counts['news_entries']} entries; preservation minimum is {MIN_NEWS}.")
    if counts["bibliography_entries"] < MIN_BIBLIOGRAPHY:
        fail(f"Bibliography has {counts['bibliography_entries']} entries; preservation minimum is {MIN_BIBLIOGRAPHY}.")
    if counts["research_stories"] != STORY_COUNT:
        fail(f"Story index has {counts['research_stories']} story cards; expected {STORY_COUNT}.")
    if counts["homepage_news_entries"] != 5:
        fail(f"Homepage has {counts['homepage_news_entries']} news entries; expected the latest five.")
    if homepage and news:
        latest_archive_ids = [identity for identity in news.ids if identity.startswith("news-")][:5]
        homepage_news_ids = [identity for identity in homepage.ids if identity.startswith("news-")]
        if homepage_news_ids != latest_archive_ids:
            fail("Homepage news entries differ from the first five entries in the archive.")
    checks["html_pages"] = len(pages)
    checks["hosting_prefixes"] = len(BASES)
    result = {
        "ok": not errors,
        "output": str(public),
        "checks": dict(checks),
        "preserved_content": counts,
        "errors": errors,
        "warnings": warnings,
        "limits": ["External URL availability and visual layout require separate review."],
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
