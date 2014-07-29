'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import string
import cgi
import urllib

import docutils.core
import markdown
import pygments
import pygments.lexers
import pygments.formatters

import tag as t

DIR = os.path.dirname(os.path.abspath(__file__))
THEME = '.'
from page import page
#__import__("page")
#page = page.page

def application(env, start_response):
    resp_code, doc = handle(env)
    ctype, content = doc
    start_response(resp_code, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def handle(env):
    if env['REQUEST_METHOD'] != 'GET':
        return '501 Not Implemented', not_impl(root)
    root, fpath = env['SCRIPT_NAME'], resolve(env['REQUEST_URI'])
    if os.path.isdir(fpath):
        return '200 OK', listdir(root, fpath)
    if os.path.isfile(fpath):
        return '200 OK', showfile(root, fpath)
    else:
        return '404 Not Found', not_found(root)

def resolve(uri):
    '''resolve URI -> fpath, w/ special case for "/static" stem'''
    fpath = urllib.unquote_plus(uri)
    if fpath.startswith('/static/'):
        fpath = os.path.normpath(fpath.replace('/static', os.path.join(DIR, THEME)))
        if fpath == DIR:
            fpath = '.'
    elif fpath == '/':
        fpath = '.'
    else:
        fpath = fpath[1:]
    return fpath

# --- files ---

def showfile(root, fpath):
    ext = '.' + fpath.rsplit('.', -1)[1] if '.' in fpath else ''
    if ext in EXT_MAP:
        return EXT_MAP[ext](root, fpath)
    else:
        return txt(root, fpath)

def txt(root, fpath):
    buf = unicode(open(fpath).read(), encoding='utf-8')
    return page(root, t.title(fpath), t.pre(cgi.escape(buf)))

def rst(root, fpath):
    parts = docutils.core.publish_parts(source=open(fpath).read(), writer_name='html',
        settings_overrides={'syntax_highlight': 'short', 'math_output': 'MathML'})
    return page(root, parts['head'], parts['html_body'])

def md(root, fpath):
    return page(root, t.title(fpath), markdown.markdown(open(fpath).read()))

def cat(ctype):
    def f(root, fpath):
        return (ctype, open(fpath).read())
    return f

def highlight(lexer):
    def f(root, fpath):
        body = pygments.highlight(open(fpath).read(), lexer, FORMATTER)
        return page(root, t.title(fpath), body)
    return f

# --- directories ---

def listdir(root, fpath):
    body = [t.h1(fpath), t.table(rows(root, fpath))]
    return page(root, t.title(fpath), body)

def rows(root, fpath):
    names = [ n for n in os.listdir(fpath) if not n.startswith('.') ]
    if fpath == '.':
        fpath = ''
    else:
        url = '%s/%s' % (root, os.path.dirname(fpath))
        a = t.a('[..]', [('href', urllib.quote_plus(url, '/'))])
        yield t.tr(t.td(a))
    for name in sorted(names, cmp_name):
        url = '%s/%s' % (root, os.path.join(fpath, name))
        a = t.a(name, [('href', urllib.quote_plus(url, '/'))])
        yield t.tr(t.td(a))

def cmp_name(a, b):
    return cmp(os.path.isdir(b), os.path.isdir(a)) or cmp(a.lower(), b.lower())

# --- etc ---

EXT_MAP = {
    '.txt': txt,
    '.rst': rst,
    '.rest': rst,
    '.md': md,
    '.css': cat('text/css'),
    '.html': cat('text/html'),
    '.gif': cat('image/gif'),
    '.png': cat('image/png'),
    '.jpg': cat('image/jpeg'),
    '.json': highlight(pygments.lexers.JavascriptLexer()),
    '.js': highlight(pygments.lexers.JavascriptLexer()),
    '.sh': highlight(pygments.lexers.BashLexer()),
    '.pl': highlight(pygments.lexers.PerlLexer()),
    '.py': highlight(pygments.lexers.PythonLexer()),
}
FORMATTER = pygments.formatters.HtmlFormatter(linenos=False, style='vs')

def not_found(root):
    return page(root, t.title('File not found'), t.h2('File not found'))

def not_impl(root):
    return page(root, t.title('Not Implemented'), t.h2('Not Implemented'))

