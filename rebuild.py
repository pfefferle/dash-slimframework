#!/usr/bin/env python

import copy, os, re, sqlite3, string, urllib
from bs4 import BeautifulSoup, NavigableString, Tag

DOCUMENTS_DIR = os.path.join('Slim_Framework.docset', 'Contents', 'Resources', 'Documents')
HTML_DIR = os.path.join('docs.slimframework.com')

db = sqlite3.connect('Slim_Framework.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

for root, dirs, files in os.walk(os.path.join(DOCUMENTS_DIR, HTML_DIR), topdown=True):
    # build search index and tables of contents
    for filename in files:
        if not filename.endswith('.html'):
            continue

        page = open(os.path.join(root, filename)).read()

        soup = BeautifulSoup(page, 'html5lib')

        menu = soup.find('div', class_='wy-menu')

        if not menu:
            continue

        headline = ""

        for item in menu.find_all():
            path = os.path.relpath(os.path.join(root, filename), DOCUMENTS_DIR)

            if item.name == "span":
                headline = item.text.strip()

            if item.name == "li":
                for item in item.find_all('a', class_='current'):
                    title = item.text.strip()

                    name = headline + " - " + title

                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Guide', path))
                    print 'name: %s, path: %s' % (name, path)

                    continue

        main = soup.find('div', class_='section')

        for tag in main.find_all(['h1', 'h2', 'h3', 'h4'], attrs = {'id' : True}):
            dashAnchor = tag.find('a', class_='dashAnchor')
            if dashAnchor:
                continue

            text = tag.text.strip()

            print 'adding toc tag for section: %s' % text
            name = '//apple_ref/cpp/Section/' + urllib.quote(text, '')
            dashAnchor = BeautifulSoup('<a name="%s" class="dashAnchor"></a>' % name).a
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

        fp = open(os.path.join(root, filename), 'w')
        fp.write(str(soup))
        fp.close()

db.commit()
db.close()
