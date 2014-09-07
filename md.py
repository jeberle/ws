
from markdown import markdown
from jinja2 import nodes
from jinja2.ext import Extension

def md(fpath):
    return '', markdown(open(fpath).read(), extensions=['smartypants(entities=unicode)'])

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
        return markdown(caller(), extensions=['smartypants(entities=unicode)'])

