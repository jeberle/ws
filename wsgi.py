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

DIR = os.path.dirname(os.path.abspath(__file__))
TMPL = string.Template(open(os.path.join(DIR, 'page.html')).read())

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
        return '501 Not Implemented', not_impl()
    fpath = resolve(env['REQUEST_URI'])
    if os.path.isdir(fpath):
        return '200 OK', listdir(fpath, env['SCRIPT_NAME'])
    if os.path.isfile(fpath):
        return '200 OK', showfile(fpath)
    else:
        return '404 Not Found', not_found()

def resolve(uri):
    '''resolve URI -> fpath, w/ special case for "/static" stem'''
    fpath = urllib.unquote_plus(uri)
    if fpath.startswith('/static/'):
        fpath = os.path.normpath(fpath.replace('/static', DIR))
        if fpath == DIR:
            fpath = '.'
    elif fpath == '/':
        fpath = '.'
    else:
        fpath = fpath[1:]
    return fpath

# --- files ---

def showfile(fpath):
    ext = '.' + fpath.rsplit('.', -1)[1] if '.' in fpath else ''
    if ext in EXT_MAP:
        return EXT_MAP[ext](fpath)
    else:
        return txt(fpath)

def txt(fpath):
    return page(title(fpath), '<pre>%s</pre>\n' % cgi.escape(open(fpath).read()))

def rst(fpath):
    parts = docutils.core.publish_parts(source=open(fpath).read(), writer_name='html',
        settings_overrides={'syntax_highlight': 'short'})
    return page(parts['head'], parts['html_body'])

def md(fpath):
    return page(title(fpath), markdown.markdown(open(fpath).read()))

def cat(ctype):
    def f(fpath):
        return (ctype, open(fpath).read())
    return f

def code(lexer):
    def f(fpath):
        body = pygments.highlight(open(fpath).read(), lexer, FORMATTER)
        return page(title(fpath), body)
    return f

# --- directories ---

def listdir(fpath, script_name):
    m = h1(fpath)
    m += '<table id="dirlist">\n'
    names = [ n for n in os.listdir(fpath) if not n.startswith('.') ]
    if fpath == '.':
        fpath = ''
    else:
        url = '%s/%s' % (script_name, os.path.dirname(fpath))
        m += tr(td(a_href(url, '[..]')))
    for name in sorted(names, cmp_name):
        url = '%s/%s' % (script_name, os.path.join(fpath, name))
        m += tr(td(a_href(url, name)))
    m += '</table>\n'
    return page(title(fpath), m)

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
    '.json': code(pygments.lexers.JavascriptLexer()),
    '.js': code(pygments.lexers.JavascriptLexer()),
    '.sh': code(pygments.lexers.BashLexer()),
    '.pl': code(pygments.lexers.PerlLexer()),
    '.py': code(pygments.lexers.PythonLexer()),
}
FORMATTER = pygments.formatters.HtmlFormatter(linenos=False, style='vs')

def not_found():
    return page(title('File not found'), h2('File not found'))

def not_impl():
    return page(title('Not Implemented'), h2('Not Implemented'))

def page(head, body):
    head, body = head.encode('utf-8'), body.encode('utf-8')
    return 'text/html', TMPL.substitute({'head':head, 'body':body})

# --- tags ---

def title(s):
    return '<title>%s</title>\n' % s

def h1(s):
    return '<h1>%s</h1>\n' % s

def h2(s):
    return '<h2>%s</h2>\n' % s

def tr(s):
    return '<tr>%s</tr>\n' % s

def td(s):
    return '<td>%s</td>' % s

def a_href(s, t):
    return '<a href="%s">%s</a>' % (urllib.quote_plus(s, '/'), t)

