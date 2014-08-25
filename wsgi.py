'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import re
import cgi
import urllib

from docutils.core import publish_parts
from markdown import markdown
from textile import textile
import pygments
import pygments.lexers
import pygments.formatters
from jinja2 import Environment, FileSystemLoader
import yaml

DIR = os.path.dirname(os.path.abspath(__file__))
THEME = '.'
ENV = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True,
    loader=FileSystemLoader(os.path.join(DIR, THEME)),
    extensions=['jinja2.ext.autoescape'])

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
        return '501 Not Implemented', page(root, 'Not Implemented', '')
    root, fpath = env['SCRIPT_NAME'], resolve(env['REQUEST_URI'])
    if os.path.isdir(fpath):
        return '200 OK', listdir(root, fpath)
    if os.path.isfile(fpath):
        return '200 OK', showfile(root, fpath)
    else:
        return '404 Not Found', page(root, 'File not found', '')

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
    if os.path.basename(os.path.dirname(os.path.abspath(fpath))) == 'marks':
        return marks(root, fpath)
    ext = '.' + fpath.rsplit('.', -1)[1] if '.' in fpath else ''
    if ext in EXT_MAP:
        return EXT_MAP[ext](root, fpath)
    else:
        return txt(root, fpath)

def txt(root, fpath):
    buf = unicode(open(fpath).read(), encoding='utf-8')
    return page(root, fpath, '<pre>%s</pre>' % cgi.escape(buf))

def yml(root, fpath):
    buf = unicode(open(fpath).read(), encoding='utf-8')
    d = yaml.load(buf)
    tmpl = ENV.get_template(fpath.replace('.yml', '.html'))
    return 'text/html', tmpl.render(d).encode('utf-8')

def rst(root, fpath):
    parts = publish_parts(source=open(fpath).read(), writer_name='html',
        settings_overrides={'syntax_highlight': 'short', 'math_output': 'MathML'})
    return page(root, parts['head'], parts['html_body'])

def md(root, fpath):
    return page(root, fpath, markdown(open(fpath).read()))

def txtl(root, fpath):
    buf = textile(open(fpath).read(), html_type='html', auto_link=True, encoding='utf-8')
    return page(root, fpath, buf)

def cat(ctype):
    def f(root, fpath):
        return (ctype, open(fpath).read())
    return f

def highlight(lexer):
    def f(root, fpath):
        body = pygments.highlight(open(fpath).read(), lexer, FORMATTER)
        return page(root, fpath, body)
    return f

# --- directories ---

def listdir(root, fpath):
    return render(root, fpath, {'rows': rows(root, fpath)}, 'dirlist.html')

def rows(root, fpath):
    names = [ n for n in os.listdir(fpath) if not n.startswith('.') ]
    if fpath == '.':
        fpath = ''
    else:
        url = '%s/%s' % (root, os.path.dirname(fpath))
        yield {'url': urllib.quote_plus(url, '/'), 'name': '[..]'}
    for name in sorted(names, cmp_name):
        url = '%s/%s' % (root, os.path.join(fpath, name))
        yield {'url': urllib.quote_plus(url, '/'), 'name': name}

def cmp_name(a, b):
    return cmp(os.path.isdir(b), os.path.isdir(a)) or cmp(a.lower(), b.lower())

# --- bookmarks ---

def marks(root, fpath):
    title, sections = load_marks(fpath)
    return render(root, title, {'sections': sections}, 'marks.html')

def load_marks(fpath):
    f = open(fpath)
    title = unicode(f.readline().rstrip(), encoding='utf-8')
    sections = []
    sec = {'hdr': '', 'links': []}
    for line in f:
        line = unicode(line.rstrip(), encoding='utf-8')
        if re.search(r'(^-)|(^[#])', line):  # comment line
            continue
        elif line == '':  # empty line
            if (sec['hdr'] != ''):
                sections.append(sec)
            sec = {'hdr': '', 'links': []}
        elif (sec['hdr'] == ''):  # group line
            sec['hdr'] = line
        else:  # link line
          m = re.match(r'^(.*)\t(.*)$', line)
          name = m.group(1)
          url  = m.group(2)
          sec['links'].append({'name': name, 'url': url})
    return title, sections

# --- etc ---

EXT_MAP = {
    '.txt': txt,
    '.rst': rst,
    '.rest': rst,
    '.md': md,
    '.txtl': txtl,
    '.textile': txtl,
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
    '.yml': yml,
}
FORMATTER = pygments.formatters.HtmlFormatter(linenos=False, style='vs')

def page(root, title, body):
    return render(root, title, {'body': body.encode('utf-8')}, 'page.html')

def render(root, title, ctx, tmplname):
    ctx['root'] = root
    ctx['title'] = title
    tmpl = ENV.get_template(tmplname)
    return 'text/html', tmpl.render(ctx).encode('utf-8')

