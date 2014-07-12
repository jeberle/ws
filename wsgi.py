import os.path
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.lexers import XmlLexer, PythonLexer, PerlLexer, BashLexer
from pygments.formatters import HtmlFormatter
from docutils.core import publish_file

LEX_MAP = {
    'sh': BashLexer(),
    'pl': PerlLexer(),
    'py': PythonLexer(),
    'xml': XmlLexer(),
}

def application(env, start_response):
    uri = env['REQUEST_URI']
    fname = './%s' % uri[1:]
    if not os.path.isfile(fname):
        start_response('404 Not Found', [('Content-Type','text/html')])
        return ['<pre>File not found</pre>\n']
    if fname.endswith('.rst') or fname.endswith('.rest'):
        ctype, out = rst2html(fname)
    elif fname.endswith('.txt'):
        ctype, out = dump(fname)
    else:
        ctype, out = pygmentize(fname)
    start_response('200 OK', [
        ('Content-Type', ctype),
        ('Content-Length', str(len(out)))
    ])
    return [out]

def rst2html(fname):
    return 'text/html', publish_file(source_path=fname, writer_name='html')

def dump(fname):
    return 'text/plain', open(fname).read()

def pygmentize(fname):
    ext = fname.rsplit('.', -1)[1] if '.' in fname else ''
    buf = open(fname).read()
    if ext in LEX_MAP:
        lexer = LEX_MAP[ext]
    else:
        lexer = guess_lexer(buf)
    formatter = HtmlFormatter(linenos=False, style='vs')
    out = highlight(buf, lexer, formatter).encode('utf-8')
    return 'text/html', out

