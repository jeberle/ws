
from docutils.core import publish_parts
from jinja2 import nodes
from jinja2.ext import Extension

OVERRIDES = {'syntax_highlight': 'short', 'math_output': 'MathML', 'smart_quotes': True}

def rst(fpath):
    parts = publish_parts(source=open(fpath).read(), writer_name='html', settings_overrides=OVERRIDES)
    return parts['title'], parts['html_body']

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

