'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import sys
import urllib

# since we cd normally, put file dir at head of path
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from dirlist import dirlist
from showfile import showfile
from tmpl import render

THEME = '.'
EXT_MAP = {
    '.css': 'text/css',
    '.xml': 'text/xml',
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.js': 'application/x-javascript',
}

def application(env, start_response):
    resp_code, ctype, content = handle(env)
    start_response(resp_code, [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content)))
    ])
    return [content]

def handle(env):
    root, method, uri = env['SCRIPT_NAME'], env['REQUEST_METHOD'], env['REQUEST_URI']
    if method != 'GET':
        return '501 Not Implemented', 'text/html', error(root, 'Not Implemented')
    fpath = resolve(root, uri)
    ext = '.' + fpath.rsplit('.', 1)[1] if '.' in fpath else ''
    if ext in EXT_MAP and os.path.isfile(fpath):
        return '200 OK', EXT_MAP[ext], open(fpath).read()
    if os.path.isfile(fpath):
        return '200 OK', 'text/html', showfile(root, fpath)
    if os.path.isdir(fpath):
        return '200 OK', 'text/html', dirlist(root, fpath)
    else:
        return '404 Not Found', 'text/html', error(root, 'File not found')

def resolve(root, uri):
    '''resolve URI -> fpath, w/ special case for "<root>/ws" stem'''
    fpath = urllib.unquote_plus(uri)
    if fpath.startswith('%s/ws/' % root):
        fpath = os.path.normpath(fpath.replace('%s/ws' % root, os.path.join(DIR, THEME)))
        if fpath == DIR:
            fpath = '.'
    elif fpath == '/':
        fpath = '.'
    else:
        fpath = fpath[1:]
    return fpath

def error(root, err):
    return render('page.html', root, err, h1=err)

