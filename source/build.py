import re, glob, html, json, sys

FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
def fa(n): return str(n).translate(FA)

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = s.replace('......', '<span class="blank"></span>')
    s = s.replace(' ← ', ' <span class="arr">←</span> ')
    return s

def split_term(s):
    # "term: rest" -> (term, rest); first ": " occurrence
    i = s.find(': ')
    return (s[:i], s[i+2:]) if i > 0 else (None, s)

toc_pages = json.loads(open('toc.json').read()) if len(sys.argv) > 1 and sys.argv[1] == 'toc' else {}

lessons = []
for f in sorted(glob.glob('lessons/L*.txt')):
    lessons.append(open(f).read().rstrip('\n').split('\n'))

out = []
qnum = 0
lesson_titles = []
for li, lines in enumerate(lessons, 1):
    title = lines[0][2:]
    num, name = title.split(': ', 1)
    lesson_titles.append((num, name))
    body = []
    mode = 'notes'
    note_n = 0
    table = None
    LO = [None]
    def flush_list():
        if LO[0]:
            body.append('</%s>' % LO[0])
            LO[0] = None
    in_q = False
    for raw in lines[1:]:
        if not raw.strip():
            continue
        if raw.startswith('## '):
            flush_list()
            if in_q:
                body.append('</div>')
                in_q = False
            h = raw[3:]
            if h.startswith('پرسش و پاسخ'):
                mode = 'q'
                body.append('<h2 class="qa-title"><span>پرسش و پاسخ %s</span></h2><div class="qa">' % html.escape(num))
            else:
                body.append('<h3 class="sec">%s</h3>' % inline(h))
            continue
        tag, _, text = raw.partition(': ')
        if tag in ('table', 'table*'):
            flush_list()
            table = {'head': [c.strip() for c in text.split('|')], 'rows': [], 'plain': tag == 'table*'}
            continue
        if tag == 'tr':
            table['rows'].append([c.strip() for c in text.split('|')])
            continue
        if raw.strip() == '/table':
            cls = 'tbl cols%d%s' % (len(table['head']), ' plain' if table['plain'] else '')
            t = ['<table class="%s"><thead><tr>' % cls]
            t += ['<th>%s</th>' % inline(c) for c in table['head']]
            t.append('</tr></thead><tbody>')
            # merge repeated first-column cells (rowspan)
            rows = table['rows']
            i = 0
            while i < len(rows):
                j = i
                while j + 1 < len(rows) and rows[j + 1][0] == rows[i][0] and len(table['head']) == 3:
                    j += 1
                for k in range(i, j + 1):
                    t.append('<tr>')
                    for ci, c in enumerate(rows[k]):
                        if ci == 0 and len(table['head']) == 3 and j > i:
                            if k == i:
                                t.append('<td class="first" rowspan="%d">%s</td>' % (j - i + 1, inline(c)))
                            continue
                        t.append('<td%s>%s</td>' % (' class="first"' if ci == 0 else '', inline(c)))
                    t.append('</tr>')
                i = j + 1
            t.append('</tbody></table>')
            body.append(''.join(t))
            table = None
            continue
        if tag == 'box':
            flush_list()
            bt, _, bx = text.partition(' || ')
            body.append('<div class="box"><div class="box-t">%s</div><p>%s</p></div>' % (inline(bt), inline(bx)))
            continue
        if mode == 'q':
            if tag == 'q':
                if in_q:
                    body.append('</div>')
                qnum += 1
                body.append('<div class="q"><div class="qq"><span class="qn">%s</span><span class="qt">%s</span></div>' % (fa(qnum), inline(text)))
                in_q = True
            elif tag == 'a':
                body.append('<div class="qa-a"><span class="al">پاسخ:</span> %s</div>' % inline(text))
            elif tag == 't':
                k, v = split_term(text)
                body.append('<div class="qa-a sub"><span class="tk">%s:</span> %s</div>' % (inline(k), inline(v)))
            else:
                raise SystemExit('bad q line: ' + raw)
            continue
        # notes mode
        if tag == 'n':
            flush_list()
            note_n += 1
            body.append('<div class="note"><span class="nn">%s</span><div class="nt">%s</div></div>' % (fa(note_n), inline(text)))
        elif tag in ('ol', 'ul'):
            if LO[0] != tag:
                flush_list()
                body.append('<%s class="lst">' % tag)
                LO[0] = tag
            body.append('<li>%s</li>' % inline(text))
        else:
            raise SystemExit('bad line: ' + raw)
    flush_list()
    if in_q:
        body.append('</div>')
    if mode == 'q':
        body.append('</div>')
    out.append('''<section class="lesson">
<header class="lh"><span class="mark">@@L%02d@@</span><div class="lnum"><small>درس</small><span>%s</span></div><h1>%s</h1></header>
%s
</section>''' % (li, html.escape(num.replace('درس ', '')), html.escape(name), '\n'.join(body)))

toc_rows = []
for i, (num, name) in enumerate(lesson_titles, 1):
    pg = toc_pages.get('L%02d' % i, '')
    toc_rows.append('<li><span class="tn">%s</span><span class="tt">%s</span><span class="dots"></span><span class="tp">%s</span></li>'
                    % (html.escape(num), html.escape(name), fa(pg) if pg else ''))

doc = open('template.html').read()
doc = doc.replace('{{TOC}}', '\n'.join(toc_rows)).replace('{{BODY}}', '\n'.join(out))
open('booklet.html', 'w').write(doc)
print('questions:', qnum)
