'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import string
import cgi
import urllib

import docutils.core
import markdown
import pygments
import pygments.lexers as lexers
import pygments.formatters as formatters

DIR = os.path.dirname(os.path.abspath(__file__))
PAGE = string.Template(open(os.path.join(DIR, 'page.html')).read())
EXT_MAP = {
    '.sh': lexers.BashLexer(),
    '.pl': lexers.PerlLexer(),
    '.py': lexers.PythonLexer(),
}
FORMATTER = formatters.HtmlFormatter(linenos=False, style='vs')

def application(env, start_response):
    # fix up URI -> fname, w/ special case for "/static" stem
    fname = urllib.unquote_plus(env['REQUEST_URI'])
    if fname.startswith('/static/'):
        fname = os.path.normpath(fname.replace('/static', DIR))
        if fname == DIR:
            fname = '.'
    elif fname == '/':
        fname = '.'
    else:
        fname = fname[1:]
    resp, ctype, title, content = '200 OK', 'text/html;charset=utf-8', None, None
    if env['REQUEST_METHOD'] != 'GET':
        resp = '501 Not Implemented'
        title, body = 'Not Implemented', '<h2>Not Implemented</h2>\n'
    ext = '.' + fname.rsplit('.', -1)[1] if '.' in fname else ''
    # directory list
    if os.path.isdir(fname):
        body = listdir(fname)
    # 404 file not found
    elif not os.path.isfile(fname):
        resp = '404 Not Found'
        title, body = 'File not found', '<h2>File not found</h2>\n'
    # css
    elif ext == '.css':
        ctype, content = 'text/css', open(fname).read()
    # html
    elif ext == '.html':
        content = open(fname).read()
    # restructured text
    elif ext == '.rst' or ext == '.rest':
        body = rst2html(open(fname).read())
    # markdown
    elif ext == '.md':
        body = md2html(open(fname).read())
    # source code for syntax highlighting
    elif ext in EXT_MAP:
        body = pygmentize(open(fname).read(), EXT_MAP[ext])
    # plain text
    else:
        body = '<pre>%s</pre>\n' % cgi.escape(open(fname).read())
    if title is None:
        title = fname
    if content is None:
        content = PAGE.substitute({'title':title, 'body':body})
    start_response(resp, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def listdir(fpath):
    m  = '<h1>%s</h1>\n' % fpath
    m += '<table id="dirlist">\n'
    names = [ n for n in os.listdir(fpath) if not n.startswith('.') ]
    if fpath == '.':
        fpath = ''
    else:
        url = urllib.quote_plus(os.path.dirname(fpath), '/')
        m += '<tr><td><a href="/%s">%s</a></td></tr>\n' % (url, '[..]')
    for name in sorted(names, cmp_name):
        url = urllib.quote_plus(os.path.join(fpath, name), '/')
        m += '<tr><td><a href="%s">%s</a></td></tr>\n' % (url, name)
    m += '</table>\n'
    return m

def cmp_name(a, b):
    return cmp(os.path.isdir(b), os.path.isdir(a)) or cmp(a.lower(), b.lower())

def rst2html(buf):
    return docutils.core.publish_string(source=buf, writer_name='html')

def md2html(buf):
    return markdown.markdown(buf).encode('utf-8')

def pygmentize(buf, lexer):
    return pygments.highlight(buf, lexer, FORMATTER).encode('utf-8')

