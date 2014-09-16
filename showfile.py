'''Render file contents using file type driven renderer'''

import os.path
import cgi
import yaml
import pygments.lexers

from code import highlight
from md import md
from rst import rst
from txtl import txtl
from tmpl import render_ext, render_sys

EXT_MAP = {
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
        return render_ext(fpath, root, **d)
    # attempt to render requested template in .yml file
    if ext == '.yml':
        d = yaml.load(unicode(open(fpath).read(), encoding='utf-8'))
        if 'template' in d:
            return render_ext(d['template'], root, **d)
    # check if file contains template tags (for templating non-html files)
    buf = open(fpath).read(1024)
    if '{%' in buf or '{{' in buf:
        return render_ext(fpath, root)
    # render file based on file ext
    if ext in EXT_MAP:
        title, body = EXT_MAP[ext](fpath)
        h1 = title if title else ''
        title = title if title else fpath
        return render_sys('page.html', root, title=title, body=body, h1=h1)
    try:
        lexer = pygments.lexers.get_lexer_for_filename(fpath)
        body = highlight(lexer, fpath)
        return render_sys('page.html', root, title=fpath, body=body)
    except:
        # just try for text as <pre> block
        buf = unicode(open(fpath).read(), encoding='utf-8')
        body = u'<pre>%s</pre>' % cgi.escape(buf)
        return render_sys('page.html', root, title=fpath, body=body)

