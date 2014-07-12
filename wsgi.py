import os.path
import string

import pygments
import pygments.lexers as lexers
import pygments.formatters as formatters
import docutils.core

LEX_MAP = {
    'sh': lexers.BashLexer(),
    'pl': lexers.PerlLexer(),
    'py': lexers.PythonLexer(),
    'xml': lexers.XmlLexer(),
}
PAGE = string.Template(open('page.html').read())

def application(env, start_response):
    uri, content, resp, ctype = env['REQUEST_URI'], '', '200 OK', 'text/html'
    fname, title = uri[1:], uri[1:]
    if not os.path.isfile(fname):
        resp = '404 Not Found'
        title, body = 'File not found', '<h2>File not found</h2>\n'
    elif fname.endswith('.css'):
        ctype, content = 'text/css', open(fname).read()
    elif fname.endswith('.txt'):
        ctype, content = 'text/plain', open(fname).read()
    elif fname.endswith('.rst') or fname.endswith('.rest'):
        body = rst2html(fname)
    else:
        body = pygmentize(fname)
    if not content:
        content = PAGE.substitute({'title':title, 'body':body})
    start_response(resp, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def rst2html(fname):
    return docutils.core.publish_string(source=open(fname).read(), writer_name='html')

def pygmentize(fname):
    buf = open(fname).read()
    ext = fname.rsplit('.', -1)[1] if '.' in fname else ''
    lexer = LEX_MAP[ext] if ext in LEX_MAP else lexers.guess_lexer(buf)
    formatter = formatters.HtmlFormatter(linenos=False, style='vs')
    return pygments.highlight(buf, lexer, formatter).encode('utf-8')

