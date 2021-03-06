
import pygments
import pygments.lexers
import pygments.formatters
from jinja2 import nodes
from jinja2.ext import Extension

FORMATTER = pygments.formatters.HtmlFormatter(linenos=False, style='vs')

def highlight(lexer, fpath):
    return pygments.highlight(unicode(open(fpath).read(), encoding='utf-8'), lexer, FORMATTER)

class Pygments(Extension):
    '''add {% code 'lexer-alias' %}...{% endcode %} custom tag'''
    tags = set(['code'])

    def __init__(self, environment):
        super(Pygments, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        alias = parser.parse_expression()
        body = parser.parse_statements(['name:endcode'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_render', [alias]), [], [], body).set_lineno(lineno)

    def _render(self, alias, caller):
        return pygments.highlight(caller(), pygments.lexers.get_lexer_by_name(alias), FORMATTER)

