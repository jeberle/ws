import pygments.lexers

from code import highlight
from md import md
from rst import rst
from txtl import txtl
from tmpl import render_sys

def test_code():
    fpath = 'files/code.py'
    lexer = pygments.lexers.get_lexer_for_filename(fpath)
    body = highlight(lexer, fpath)
    open('files/last.html', 'w').write(body.encode('utf-8'))
    assert body == unicode(open('files/code.html').read(), encoding='utf-8')

def test_md():
    title, body = md('files/md.md')
    open('files/last.html', 'w').write(body.encode('utf-8'))
    assert title == ''
    assert body == unicode(open('files/md.html').read(), encoding='utf-8').rstrip()

def test_rst():
    title, body = rst('files/rst.rst')
    open('files/last.html', 'w').write(body.encode('utf-8'))
    assert title == ''
    assert body == unicode(open('files/rst.html').read(), encoding='utf-8')

def test_txtl():
    title, body = txtl('files/txtl.txtl')
    open('files/last.html', 'w').write(body.encode('utf-8'))
    assert title == ''
    assert body == unicode(open('files/txtl.html').read(), encoding='utf-8').rstrip()

def test_tmpl():
    body = render_sys('files/tmpl.html', 'root', title='Title', year=2014)
    open('files/last.html', 'w').write(body)
    assert body.rstrip() == open('files/rendered.html').read().rstrip()

