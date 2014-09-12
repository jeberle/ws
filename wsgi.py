'''Render Pygments, reStructuredText, and Markdown via a minimal WSGI application.'''

import os.path
import cgi
import sys
import traceback
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
    '.vim': 'text/plain; charset=utf-8',
    '.gif': 'image/gif',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml; charset=utf-8',
    '.js': 'application/x-javascript; charset=utf-8',
}

HTML = 'text/html; charset=utf-8'
XML = 'text/xml; charset=utf-8'

def application(env, start_response):
    resp_code, ctype, loc, content = handle(env)
    if loc:
        start_response(resp_code, [
            ('Content-Type', ctype),
            ('Content-Length', str(len(content))),
            ('Location', loc)
        ])
    else:
        start_response(resp_code, [
            ('Content-Type', ctype),
            ('Content-Length', str(len(content)))
        ])
    return [content]

def handle(env):
    try:
        root, method, uri = env['SCRIPT_NAME'], env['REQUEST_METHOD'], env['REQUEST_URI']
        if method != 'GET':
            return '501 Not Implemented', HTML, None, error(root, 'Not Implemented')
        fpath = resolve(root, uri)
        ext = '.' + fpath.rsplit('.', 1)[1] if '.' in fpath else ''
        if ext in EXT_MAP and os.path.isfile(fpath):
            return '200 OK', EXT_MAP[ext], None, open(fpath).read()
        if os.path.isdir(fpath):
            if not uri.endswith('/'):
                return '301 Moved Permanently', HTML, uri+'/', error(root, 'Moved Permanently')
            # check for index.* w/in dir
            ls = sorted(glob(os.path.join(fpath, 'index.*')))
            if ls:
                fpath = ls[0]
            else:
                return '200 OK', HTML, None, dirlist(root, fpath)
        elif not os.path.exists(fpath):
            # try to resolve file like Apache MultiViews: /foo -> /foo.html
            ls = sorted(glob(fpath + '.*'))
            if ls:
                fpath = ls[0]
        if os.path.isfile(fpath):
            ctype = XML if fpath.endswith('.xml') else HTML
            return '200 OK', ctype, None, showfile(root, fpath)
        else:
            return '404 Not Found', HTML, None, error(root, 'File not found')
    except Exception as ex:
        return '500 Error', HTML, None, error(root, traceback.format_exc())

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

