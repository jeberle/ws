'''Provides Pygments and reStructuredText as a minimal WSGI application.'''

import os.path
import string

import pygments
import pygments.lexers as lexers
import pygments.formatters as formatters
import docutils.core

DIR = os.path.dirname(os.path.abspath(__file__))
PAGE = string.Template(open(os.path.join(DIR, 'page.html')).read())
LEX_MAP = {
    'sh': lexers.BashLexer(),
    'pl': lexers.PerlLexer(),
    'py': lexers.PythonLexer(),
}

def application(env, start_response):
    method, uri = env['REQUEST_METHOD'], env['REQUEST_URI']
    fname, title = uri[1:], uri[1:]
    resp, ctype, content = '200 OK', 'text/html; charset=utf-8', None
    if fname.startswith('static/'):
        fname = fname.replace('static', DIR)
    if method != 'GET':
        resp = '501 Not Implemented'
        title, body = 'Not Implemented', '<h2>Not Implemented</h2>\n'
    elif not os.path.isfile(fname):
        resp = '404 Not Found'
        title, body = 'File not found', '<h2>File not found</h2>\n'
    elif fname.endswith('.css'):
        ctype, content = 'text/css', open(fname).read()
    elif fname.endswith('.txt'):
        ctype, content = 'text/plain; charset=utf-8', open(fname).read()
    elif fname.endswith('.rst') or fname.endswith('.rest'):
        body = rst2html(open(fname).read())
    else:
        body = pygmentize(fname)
    if content is None:
        content = PAGE.substitute({'title':title, 'body':body})
    start_response(resp, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def rst2html(buf):
    return docutils.core.publish_string(source=buf, writer_name='html')

def pygmentize(fname):
    buf = open(fname).read()
    ext = fname.rsplit('.', -1)[1] if '.' in fname else ''
    lexer = LEX_MAP[ext] if ext in LEX_MAP else lexers.guess_lexer(buf)
    formatter = formatters.HtmlFormatter(linenos=False, style='vs')
    return pygments.highlight(buf, lexer, formatter).encode('utf-8')

