# Crawls the live GitHub Pages site and reports every internal link that does not return 200.
import re, sys, urllib.request, urllib.parse
from collections import defaultdict
BASE = sys.argv[1]; host = urllib.parse.urlparse(BASE).netloc
seen, bad, refs, queue = set(), {}, defaultdict(set), [BASE]
def status(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'linkcheck'}), timeout=20)
        return r.status, r.read().decode('utf-8', 'ignore') if 'html' in r.headers.get('content-type', '') else ''
    except urllib.error.HTTPError as e: return e.code, ''
    except Exception as e: return str(e), ''
while queue:
    u = queue.pop()
    if u in seen: continue
    seen.add(u); code, body = status(u)
    if code != 200: bad[u] = code; continue
    for href in re.findall(r'(?:href|src)="([^"#]+)', body):
        if href.startswith(('mailto:', 'tel:', 'sms:', 'data:', 'javascript:')): continue
        t = urllib.parse.urljoin(u, href).split('#')[0].split('?')[0]
        if urllib.parse.urlparse(t).netloc != host: continue
        refs[t].add(u.replace(BASE, '/'))
        if t not in seen: queue.append(t)
print('checked', len(seen), 'bad', len(bad))
for u, c in sorted(bad.items()):
    print(c, u, '<- from', len(refs[u]), 'pages e.g.', sorted(refs[u])[:3])
