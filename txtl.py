
from textile import textile
from jinja2 import nodes
from jinja2.ext import Extension

def txtl(fpath):
    return '', textile(unicode(open(fpath).read(), encoding='utf-8'), html_type='html', auto_link=True, encoding='utf-8')

class Textile(Extension):
    '''add {% txtl 'nl2sp' %}...{% endtxtl %} custom tag'''
    tags = set(['txtl'])

    def __init__(self, environment):
        super(Textile, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        if parser.stream.current.test('string'):
            nl2sp = parser.parse_expression()
        else:
            nl2sp = nodes.Const(None)
        body = parser.parse_statements(['name:endtxtl'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_render', [nl2sp]), [], [], body).set_lineno(lineno)

    def _render(self, nl2sp, caller):
        txt = _nl2sp(caller()) if nl2sp == 'nl2sp' else caller()
        return textile(txt.encode('utf-8'), html_type='html', auto_link=True, encoding='utf-8')

def _nl2sp(txt):
    txt = txt.replace('\n\n', '\0')
    txt = txt.replace('\n', ' ')
    txt = txt.replace('\0', '\n')
    return txt

