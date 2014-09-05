'''Render file contents using file type driven renderer'''

import os.path
import cgi
import yaml

from code import EXT_MAP as map1
from md import EXT_MAP as map2
from rst import EXT_MAP as map3
from txtl import EXT_MAP as map4
from tmpl import render
from marks import marks

EXT_MAP = {}
EXT_MAP.update(map1)
EXT_MAP.update(map2)
EXT_MAP.update(map3)
EXT_MAP.update(map4)

def showfile(root, fpath):
    # special case if file is in 'marks' dir
    if os.path.basename(os.path.dirname(os.path.abspath(fpath))) == 'marks':
        return marks(root, fpath)
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

