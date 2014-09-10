'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import cgi
import sys
import urllib
from glob import glob

# since we cd normally, put file dir at head of path
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from dirlist import dirlist
from showfile import showfile
from tmpl import render_sys

EXT_MAP = {
    '.css': 'text/css; charset=utf-8',
    '.xml': 'text/xml; charset=utf-8',
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml; charset=utf-8',
    '.js': 'application/x-javascript; charset=utf-8',
}

def application(env, start_response):
    resp_code, ctype, content = handle(env)
    start_response(resp_code, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def handle(env):
    try:
        root, method, uri = env['SCRIPT_NAME'], env['REQUEST_METHOD'], env['REQUEST_URI']
        if method != 'GET':
            return '501 Not Implemented', 'text/html; charset=utf-8', error(root, 'Not Implemented')
        fpath = resolve(root, uri)
        if os.path.isdir(fpath):
            # check for index.* w/in dir
            ls = glob(os.path.join(fpath, 'index.*'))
            if len(ls) == 1:
                fpath = ls[0]
            else:
                return '200 OK', 'text/html; charset=utf-8', dirlist(root, fpath)
        elif not os.path.exists(fpath):
            # try to resolve file like Apache MultiViews: /foo -> /foo.html
            ls = glob(fpath + '.*')
            if len(ls) == 1:
                fpath = ls[0]
        ext = '.' + fpath.rsplit('.', 1)[1] if '.' in fpath else ''
        if ext in EXT_MAP and os.path.isfile(fpath):
            return '200 OK', EXT_MAP[ext], open(fpath).read()
        if os.path.isfile(fpath):
            return '200 OK', 'text/html; charset=utf-8', showfile(root, fpath)
        else:
            return '404 Not Found', 'text/html; charset=utf-8', error(root, 'File not found')
    except Exception as ex:
        return '500 Error', 'text/html; charset=utf-8', error(root, '%s: %s' % (type(ex), ex))

def resolve(root, uri):
    '''resolve URI -> fpath, w/ special case for "<root>/ws" stem'''
    fpath = urllib.unquote_plus(uri)
    if fpath.startswith('%s/ws/' % root):
        fpath = os.path.normpath(fpath.replace('%s/ws' % root, DIR))
        if fpath == DIR:
            fpath = '.'
    elif fpath == '/':
        fpath = '.'
    else:
        fpath = fpath[1:]
    return fpath

def error(root, err):
    body = u'<pre>%s</pre>' % cgi.escape(err)
    return render_sys('page.html', root, title='Error', body=body)

