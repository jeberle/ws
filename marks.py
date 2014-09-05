import re

def marks(root, fpath):
    title, sections = load_marks(fpath)
    return render('marks.html', root, title, sections=sections)

def load_marks(fpath):
    f = open(fpath)
    title = unicode(f.readline().rstrip(), encoding='utf-8')
    sections = []
    sec = {'hdr': '', 'links': []}
    for line in f:
        line = unicode(line.rstrip(), encoding='utf-8')
        if re.search(r'(^-)|(^[#])', line):  # comment line
            continue
        elif line == '':  # empty line
            if (sec['hdr'] != ''):
                sections.append(sec)
            sec = {'hdr': '', 'links': []}
        elif (sec['hdr'] == ''):  # group line
            sec['hdr'] = line
        else:  # link line
          m = re.match(r'^(.*)\t(.*)$', line)
          name = m.group(1)
          url  = m.group(2)
          sec['links'].append({'name': name, 'url': url})
    return title, sections

