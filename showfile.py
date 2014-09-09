'''Render file contents using file type driven renderer'''

import os.path
import cgi
import yaml

from code import highlight
from md import md
from rst import rst
from txtl import txtl
from tmpl import render

EXT_MAP = {
    '.json': highlight,
    '.sh': highlight,
    '.pl': highlight,
    '.py': highlight,
    '.sql': highlight,
    '.vim': highlight,
    '.yml': highlight,
    '.md': md,
    '.rst': rst,
    '.rest': rst,
    '.txtl': txtl,
    '.textile': txtl,
}

def showfile(root, fpath):
    ext = '.' + fpath.rsplit('.', 1)[1] if '.' in fpath else ''
    # attempt to load corresponding .yml file if .html
    if ext == '.html':
        yml, d = fpath.replace('.html', '.yml'), {}
        if os.path.isfile(yml):
            buf = unicode(open(yml).read(), encoding='utf-8')
            d = yaml.load(buf)
        return render(fpath, root, '', **d)
    # reality resumes, render file based on file ext
    if ext in EXT_MAP:
        title, body = EXT_MAP[ext](fpath)
        title = title if title else fpath
        h1 = title if title else ''
        return render('page.html', root, title, body=body, h1=h1)
    # just try for text as <pre> block
    else:
        buf = unicode(open(fpath).read(), encoding='utf-8')
        body = u'<pre>%s</pre>' % cgi.escape(buf)
        return render('page.html', root, fpath, body=body)

