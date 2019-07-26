#!/usr/bin/env python

# encoding: utf-8

import copy, os, re, sqlite3, string, urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup, NavigableString, Tag

DOCUMENTS_DIR = os.path.join('Slim_Framework.docset', 'Contents', 'Resources', 'Documents')
HTML_DIR = os.path.join('www.slimframework.com/docs')

db = sqlite3.connect('Slim_Framework.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

page = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, 'index.html'), encoding='utf8').read()

soup = BeautifulSoup(page, 'html5lib')

menu = soup.find('div', class_='col-md-3')

headline = ""

for item in menu.find_all():
    if item.name == "h3":
        headline = item.text.strip()

    if item.name == "ul":
        for item in item.find_all('a'):
            title = item.text.strip()

            name = headline + " - " + title

            if item.attrs["href"].startswith("http"):
                continue

            path = os.path.join(HTML_DIR, item.attrs["href"])

            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Guide', path))
            print('name: %s, path: %s' % (name, path))

            continue

main = soup.find('div', class_='section')

for root, dirs, files in os.walk(os.path.join(DOCUMENTS_DIR, HTML_DIR), topdown=True):
    # build search index and tables of contents
    for filename in files:
        if not filename.endswith('.html'):
            continue

        page = open(os.path.join(root, filename), encoding='utf8').read()

        soup = BeautifulSoup(page, 'html5lib')

        main = soup.find('div', class_='docs-content')

        if not main:
            continue

        for tag in main.find_all(['h1', 'h2', 'h3', 'h4']):
            dashAnchor = tag.find('a', class_='dashAnchor')
            if dashAnchor:
                continue

            text = tag.text.strip()

            try: print('adding toc tag for section: %s' % text)
            except: pass

            name = '//apple_ref/cpp/Section/' + urllib.parse.quote(text.encode('utf8'), '')
            dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % name, 'html5lib').a
            tag.insert(0, dashAnchor)

        # strip unecessary javascript
        [t.extract() for t in soup("script")]

        # strip Google-Fonts
        for link in soup.find_all("link", { "rel" : "stylesheet" }):
            test = re.compile("^https?.*googleapis.*", re.IGNORECASE)

            if "href" in link.attrs and test.match(link["href"].strip()):
                link.extract()

        for a in soup.find_all("a"):
            test = re.compile("^https?.*travis-ci.*", re.IGNORECASE)

            if "href" in a.attrs and test.match(a["href"].strip()):
                a.extract()

        # remove header navbar with blog link
        try:
            soup.find('nav', class_='navbar-fixed-top').decompose()
        except AttributeError:
            pass
        # remove Slim logo
        try:
            soup.find('header', class_='site-header').decompose()
        except AttributeError:
            pass
        # remove left menu
        try:
            soup.find('form', class_='searchbox').parent.decompose()
        except AttributeError:
            pass
        # remove version switcher
        try:
            soup.find('button', class_='dropdown-toggle').parent.decompose()
        except AttributeError:
            pass
        # remove link to v2 docs
        try:
            for alert in soup.find_all('div', class_='alert-info'):
                if 'Slim 2 Docs' in str(alert):
                    alert.decompose()
        except (AttributeError, TypeError):
            pass
        # remove license icon
        try:
            soup.find('a', {'rel': 'license'}).decompose()
        except AttributeError:
            pass
        # replace donation icon with a tag
        try:
            donation = soup.find('input', {'type': 'image'}).parent
            id = soup.find('input', {'name': 'hosted_button_id'}).get('value')

            link = BeautifulSoup(
                '<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&amp;hosted_button_id=' + id + '" alt="Donate with PayPal">Donate with PayPal</a>',
                'html.parser'
            )
            donation.replaceWith(link)

        except AttributeError:
            pass

        fp = open(os.path.join(root, filename), 'w', encoding='utf8')
        fp.write(str(soup))
        fp.close()

db.commit()
db.close()
