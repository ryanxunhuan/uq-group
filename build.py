#!/usr/bin/env python3
"""Build the group's static website. Requires Python 3.10+; no dependencies."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from calendar import month_abbr
from hashlib import sha256
import argparse
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
NAV = [
    ('Home', 'index.html', []),
    ('Research', 'research.html', [
        ('Research Overview', 'research.html'),
        ('Research Stories', 'stories.html'),
        ('FLOODWARRIOR', 'https://ryanxunhuan.github.io/floodwarrior/'),
        ('C-PRIME', 'https://c-prime.engin.umich.edu/home'),
        ('News Archive', 'news.html'),
    ]),
    ('Applications', 'applications.html', []),
    ('Publications', 'publications.html', [
        ('Selected Publications', 'publications.html'),
        ('Full Bibliography', 'bibliography.html'),
    ]),
    ('People', 'people.html', [
        ('Current Members', 'people.html'),
        ('Xun Huan', 'xun-huan.html'),
        ('Alumni', 'alumni.html'),
        ('Group Outings', 'outings.html'),
    ]),
    ('Teaching', 'teaching.html', []),
    ('Contact', 'contact.html', []),
]


class NewsExcerpt(HTMLParser):
    """Take complete announcements, including any nested conference lists."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.items, self.parts, self.depth = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag == 'li' and (self.depth or dict(attrs).get('id', '').startswith('news-')):
            self.depth += 1
        if self.depth:
            self.parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.depth:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            self.parts.append('</'+tag+'>')
            if tag == 'li':
                self.depth -= 1
                if not self.depth:
                    self.items.append(''.join(self.parts))
                    self.parts = []

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data('&'+name+';')

    def handle_charref(self, name):
        self.handle_data('&#'+name+';')


def display_dates(markup):
    return re.sub(r'(<li\b[^>]*>)\((\d{4})/(\d{2})\)\s*',
                  lambda m: m[1]+'<span class="news-date">'+month_abbr[int(m[3])]+' '+m[2]+'</span>', markup)


def home_content():
    archive = NewsExcerpt()
    archive.feed((ROOT / 'content/pages/news.html').read_text())
    body = (ROOT / 'content/home.html').read_text()
    body = body.replace('{{LATEST_NEWS}}', display_dates(''.join(archive.items[:5])))
    return body.replace('{{UPCOMING_EVENTS}}', display_dates((ROOT / 'content/events.html').read_text()))


def render_navigation(key, active):
    current_url = key + '.html'

    def link(label, url, main=False):
        css_class = ' class="nav-link"' if main else ''
        current = ' aria-current="page"' if url == current_url else ''
        external = url.startswith(('https://', 'http://'))
        target = ' target="_blank" rel="noopener noreferrer"' if external else ''
        suffix = ' <span aria-hidden="true">↗</span><span class="sr-only"> (opens in a new tab)</span>' if external else ''
        return '<a' + css_class + ' href="' + escape(url, quote=True) + '"' + current + target + '>' + escape(label) + suffix + '</a>'

    items = []
    for label, url, children in NAV:
        classes = ['nav-item']
        if children:
            classes.append('nav-group')
        if label == active:
            classes.append('is-active')
        item = '<li class="' + ' '.join(classes) + '">' + link(label, url, main=True)
        if children:
            item += '<details class="nav-disclosure"><summary aria-label="' + escape('More ' + label + ' pages', quote=True) + '"><span class="nav-chevron" aria-hidden="true"></span></summary><ul class="nav-submenu">'
            item += ''.join('<li>' + link(child_label, child_url) + '</li>' for child_label, child_url in children)
            item += '</ul></details>'
        items.append(item + '</li>')
    return '<ul class="nav-list">' + ''.join(items) + '</ul>'


def render_page(key, body, meta):
    shell = (ROOT / 'templates/page.html').read_text()
    links = render_navigation(key, meta.get('active'))
    style_version = sha256((ROOT / 'static/styles.css').read_bytes()).hexdigest()[:12]
    replacements = {'title': escape(meta['title']), 'description': escape(meta['description'], quote=True), 'page': key, 'navigation': links, 'body': body, 'style_version': style_version}
    for name, value in replacements.items():
        shell = shell.replace('{{'+name+'}}', value)
    return shell


def search_controls(full=False):
    return '''<div class="search-tools" data-search-tools hidden><label class="sr-only" for="paper-search">Search '''+('the Bibliography' if full else 'Selected Publications')+'''</label><div class="search-line"><input id="paper-search" type="search" placeholder="Title, author, year, or topic" autocomplete="off"><button id="clear-search" type="button" hidden>Clear</button><p id="paper-count" role="status" aria-live="polite"></p></div><p id="search-empty" hidden>No matching publications. Try another search.</p></div>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path', default='', help='GitHub repository path, used by the 404 home link only.')
    args = parser.parse_args()
    base = '/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
    if not re.fullmatch(r'(?:/[A-Za-z0-9_.-]+)*', base):
        parser.error('base-path must contain only URL-safe path components')
    PUBLIC.mkdir(exist_ok=True)
    # Copy over generated files; never modify the reviewed sources or another site.
    shutil.copytree(ROOT / 'assets', PUBLIC / 'assets', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'static', PUBLIC, dirs_exist_ok=True)
    meta = json.loads((ROOT / 'content/page-meta.json').read_text())
    meta['index'] = {'title':'UQ–SciML Group', 'description':'Xun Huan’s research group at the University of Michigan. Bayesian experimental design, scientific machine learning, and computational uncertainty quantification.', 'active':'Home'}
    for key, info in meta.items():
        source = ROOT / ('content/home.html' if key == 'index' else 'content/pages/'+key+'.html')
        body = home_content() if key == 'index' else source.read_text()
        if key == 'publications':
            body = body.replace('<div class="publication-list">', '<div class="publication-list">'+search_controls())
        elif key == 'bibliography':
            position = body.index('</section>') + len('</section>')
            body = body[:position] + search_controls(full=True) + body[position:]
        (PUBLIC / (key+'.html')).write_text(render_page(key,body,info))
    (PUBLIC / '.nojekyll').write_text('')
    # Inline CSS makes the error page independent of the missing URL's depth.
    error = (ROOT/'templates/404.html').read_text().replace('{{home}}',escape(base+'/index.html',quote=True))
    (PUBLIC/'404.html').write_text(error)
    print(f'Built {len(meta)} content pages and 404.html in {PUBLIC}')

if __name__ == '__main__':
    main()
