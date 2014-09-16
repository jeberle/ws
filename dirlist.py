'''Generate directory listing as a set of links'''

import os.path
import urllib

from tmpl import render_sys

def dirlist(root, fpath):
    fpath = os.path.normpath(fpath)
    return render_sys('dirlist.html', root, title=fpath, rows=rows(root, fpath))

def rows(root, fpath):
    names = [ n for n in os.listdir(fpath) if not n.startswith('.') ]
    if fpath == '.':
        fpath = ''
    else:
        url = '%s/%s' % (root, os.path.dirname(fpath))
        yield {'url': urllib.quote_plus(url, '/'), 'name': '[..]'}
    for name in sorted(names, cmp_name):
        fpath2 = os.path.join(fpath, name)
        fpath2 = fpath2 + '/' if os.path.isdir(fpath2) else fpath2
        url = '%s/%s' % (root, fpath2)
        yield {'url': urllib.quote_plus(url, '/'), 'name': name}

def cmp_name(a, b):
    return cmp(os.path.isdir(b), os.path.isdir(a)) or cmp(a.lower(), b.lower())

