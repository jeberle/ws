'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import re
import cgi
import urllib

from jinja2 import Environment, FileSystemLoader
from docutils.core import publish_parts
from markdown import markdown
from textile import textile
import pygments
import pygments.lexers
import pygments.formatters
import yaml

DIR = os.path.dirname(os.path.abspath(__file__))
THEME = '.'
OVERRIDES = {'syntax_highlight': 'short', 'math_output': 'MathML', 'smart_quotes': True}

def application(env, start_response):
    resp_code, doc = handle(env)
    ctype, content = doc
    start_response(resp_code, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def handle(env):
    root, method, uri = env['SCRIPT_NAME'], env['REQUEST_METHOD'], env['REQUEST_URI']
    if method != 'GET':
        return '501 Not Implemented', page(root, 'Not Implemented', '')
    fpath = resolve(uri)
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
    ext = '.' + fpath.rsplit('.', 1)[1] if '.' in fpath else ''
    if ext in EXT_MAP:
        return EXT_MAP[ext](root, fpath)
    else:
        return txt(root, fpath)

def txt(root, fpath):
    buf = unicode(open(fpath).read(), encoding='utf-8')
    return page(root, fpath, u'<pre>%s</pre>' % cgi.escape(buf))

def html(root, fpath):
    buf = unicode(open(fpath).read(), encoding='utf-8')
    yml = fpath.replace('.html', '.yml')
    d = {'root': root, 'year': 2014}
    if os.path.isfile(yml):
        buf = unicode(open(yml).read(), encoding='utf-8')
        d.update(yaml.load(buf))
    tmpl = ENV.get_template(fpath)
    return 'text/html', tmpl.render(d).encode('utf-8')

def rst(root, fpath):
    parts = publish_parts(source=open(fpath).read(), writer_name='html', settings_overrides=OVERRIDES)
    return page2(root, parts['title'], parts['html_body'])

def md(root, fpath):
    return page(root, fpath, markdown(open(fpath).read()))

def txtl(root, fpath):
    buf = textile(open(fpath).read(), html_type='html', auto_link=True, encoding='utf-8')
    return page(root, fpath, buf)

def highlight(lexer):
    def f(root, fpath):
        body = pygments.highlight(open(fpath).read(), lexer, FORMATTER)
        return page(root, fpath, body)
    return f

def cat(ctype):
    def f(root, fpath):
        return (ctype, open(fpath).read())
    return f

# --- directories ---

def listdir(root, fpath):
    return render('dirlist.html', root=root, title=fpath, rows=rows(root, fpath))

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
    return render('marks.html', root=root, title=title, sections=sections)

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
    '.html': html,
    '.css': cat('text/css'),
    '.xml': cat('text/xml'),
    '.gif': cat('image/gif'),
    '.png': cat('image/png'),
    '.jpg': cat('image/jpeg'),
    '.svg': cat('image/svg+xml'),
    '.js': cat('application/x-javascript'),
    '.json': highlight(pygments.lexers.JavascriptLexer()),
    '.sh': highlight(pygments.lexers.BashLexer()),
    '.pl': highlight(pygments.lexers.PerlLexer()),
    '.py': highlight(pygments.lexers.PythonLexer()),
    '.vim': highlight(pygments.lexers.VimLexer()),
    '.yml': highlight(pygments.lexers.YamlLexer()),
}
FORMATTER = pygments.formatters.HtmlFormatter(linenos=False, style='vs')

def page(root, title, body):
    return render('page.html', root=root, title=title, h1=title, body=body)

def page2(root, title, body):
    return render('page.html', root=root, title=title, body=body)

def render(tmplname, **kwargs):
    tmpl = ENV.get_template(tmplname)
    return 'text/html', tmpl.render(kwargs).encode('utf-8')

# --- Jinja2 extensions ---

from jinja2 import nodes
from jinja2.ext import Extension


class Restructured(Extension):
    '''add {% rst %}...{% endrst %} custom tag'''
    tags = set(['rst'])

    def __init__(self, environment):
        super(Restructured, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endrst'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_render'), [], [], body).set_lineno(lineno)

    def _render(self, caller):
        parts = publish_parts(caller(), writer_name='html', settings_overrides=OVERRIDES)
        return parts['html_body']


class Textile(Extension):
    '''add {% txtl %}...{% endtxtl %} custom tag'''
    tags = set(['txtl'])

    def __init__(self, environment):
        super(Textile, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endtxtl'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_render'), [], [], body).set_lineno(lineno)

    def _render(self, caller):
        return textile(caller().encode('utf-8'), html_type='html', auto_link=True, encoding='utf-8')


class Markdown(Extension):
    '''add {% md %}...{% endmd %} custom tag'''
    tags = set(['md'])

    def __init__(self, environment):
        super(Markdown, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endmd'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_render'), [], [], body).set_lineno(lineno)

    def _render(self, caller):
        return markdown(caller())

ENV = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True,
    loader=FileSystemLoader(['.', os.path.join(DIR, THEME)]),
    extensions=['jinja2.ext.autoescape', Restructured, Textile, Markdown])

