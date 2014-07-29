
def doctype():
    return '<!DOCTYPE html>\n'

def _full(name, eol0='', eol1=''):
    tag0 = '<%s%%s>%s' % (name, eol0)
    tag1 = '</%s>%s' % (name, eol1)
    def f(a, attrs=None):
        return [tag0 % _pack(attrs), a, tag1]
    return f

def _half(name, eol=''):
    tag0 = '<%s%%s/>%s' % (name, eol)
    def f(attrs):
        return tag0 % _pack(attrs)
    return f

def _pack(attrs):
    if not attrs:
        return ''
    return ' '+' '.join(['%s="%s"' % (k, v) for k, v in attrs])

html = _full('html', '\n', '\n')
head = _full('head', '\n', '\n')
title = _full('title', '', '\n')
link = _half('link', '\n')
meta = _half('meta', '\n')
body = _full('body', '\n', '\n')
div = _full('div', '', '\n')
h1 = _full('h1', '', '\n')
h2 = _full('h2','',  '\n')
h3 = _full('h3','',  '\n')
table = _full('table', '\n', '\n')
tr = _full('tr', '', '\n')
td = _full('td', '', '\n')
ul = _full('ul', '\n', '\n')
ol = _full('ol', '\n', '\n')
li = _full('li', '', '\n')
pre = _full('pre', '', '\n')
a = _full('a', '', '')

def flatten(a):
    for v in a:
        if type(v) in (type(''), type(u'')):
            yield v
        else:
            for w in flatten(v):
                yield w

