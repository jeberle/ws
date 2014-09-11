'''Define Jinja2 environment & render method'''

import os.path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from code import Pygments
from md import Markdown
from rst import Restructured
from txtl import Textile

DIR = os.path.dirname(os.path.abspath(__file__))

# system templates

SYS_ENV = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True,
    loader=FileSystemLoader([DIR]),
    extensions=['jinja2.ext.autoescape'])

def render_sys(fpath, root, **kwargs):
    d = {'root': root, 'ws': '%s/ws' % root, 'now': datetime.now()}
    d.update(kwargs)
    tmpl = SYS_ENV.get_template(fpath)
    return tmpl.render(d).encode('utf-8')

# external templates

EXT_ENV = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True,
    loader=FileSystemLoader(['.', 'templates']),
    extensions=['jinja2.ext.autoescape', Pygments, Markdown, Restructured, Textile])

def render_ext(fpath, root, **kwargs):
    d = {'root': root, 'now': datetime.now()}
    d.update(kwargs)
    tmpl = EXT_ENV.get_template(fpath)
    return tmpl.render(d).encode('utf-8')

