import tag as t

def page(root, head, body):
    doc = [
        t.doctype(), 
        t.html([
          t.head([
            t.link([('href', '%s/static/style.css' % root), ('media', 'screen'),
                  ('rel', 'stylesheet'), ('type', 'text/css')]),
            t.meta([('http-equiv', 'Content-Type'), ('content', 'text/html; charset=utf-8')]),
            head,
          ]),
          t.body(body)
        ])
    ]
    return 'text/html', ''.join(t.flatten(doc)).encode('utf-8')

def test_page():
    ctype, doc = page('$root', '$head', '$body')
    s = ''.join(t.flatten(doc))
    print s
    assert s == '''\
<!DOCTYPE html>
<html>
<head>
<link href="$root/static/style.css" media="screen" rel="stylesheet" type="text/css"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
$head</head>
<body>
$body</body>
</html>
'''

