
from textile import textile
from jinja2 import nodes
from jinja2.ext import Extension

def txtl(fpath):
    return '', textile(open(fpath).read(), html_type='html', auto_link=True, encoding='utf-8')

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

