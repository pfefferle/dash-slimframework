#!/usr/bin/env python

import copy, os, re, sqlite3, string, urllib
from bs4 import BeautifulSoup, NavigableString, Tag

DOCUMENTS_DIR = os.path.join('SlimFramework.docset', 'Contents', 'Resources', 'Documents')
HTML_DIR = os.path.join('docs.slimframework.com')

db = sqlite3.connect('SlimFramework.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')


# build search index and tables of contents
page = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, 'index.html')).read()

soup = BeautifulSoup(page, 'html5lib')

# add each "main" headline to the search index as "Category"
for li in soup.find_all('li', { 'class' : 'nav-header' }):
    a = li.a
    name = a.text.strip()
    path = os.path.join(HTML_DIR, 'index.html', a.get('href').strip())

    if len(name) > 0:
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Category', path))
        print 'name: %s, path: %s' % (name, path)

# add each "sub" headline to the search index as "Guide"
for li in soup.find_all('li', { 'class' : 'nav-page' }):
    a = li.a
    name = a.text.strip()
    path = os.path.join(HTML_DIR, 'index.html', a.get('href').strip())

    if len(name) > 0:
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Guide', path))
        print 'name: %s, path: %s' % (name, path)

db.commit()
db.close()


# build index file
index = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, 'index.html')).read()
soup = BeautifulSoup(index)

# strip unecessary javascript
[t.extract() for t in soup('script')]
nav = soup.find('ul', { 'class' : 'pull-right' })
if nav:
    nav.extract()

fp = open(os.path.join(DOCUMENTS_DIR, HTML_DIR, 'index.html'), 'w')
fp.write(str(soup))
fp.close()
