'''Define Jinja2 environment & render method'''

import os.path
from jinja2 import Environment, FileSystemLoader

from code import Pygments
from md import Markdown
from rst import Restructured
from txtl import Textile

DIR = os.path.dirname(os.path.abspath(__file__))
THEME = '.'

ENV = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True,
    loader=FileSystemLoader(['.', 'templates', os.path.join(DIR, THEME)]),
    extensions=['jinja2.ext.autoescape', Pygments, Markdown, Restructured, Textile])

def render(fpath, root, title, **kwargs):
    d = {'root': root, 'ws': '%s/ws' % root, 'title': title, 'year': 2014}
    d.update(kwargs)
    tmpl = ENV.get_template(fpath)
    return tmpl.render(d).encode('utf-8')

