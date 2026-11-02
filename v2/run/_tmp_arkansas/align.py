import json, sys, pickle
sys.path.insert(0, 'v2/tools')
from validate_inst import fold
R = 'v2/run/'
A = json.load(open(R + 'coderA/arkansas.json'))
B = json.load(open(R + 'coderB/arkansas.json'))
C = json.load(open('v2/collect/arkansas.json'))
tf = {d['id']: d['text_file'] for d in C['documents']}


def span(hay, u):
    a = fold(u['anchor'])
    i = hay.find(a)
    if i < 0:
        s = hay.find(fold(u['frag_start']))
        return (s, s + len(a)) if s >= 0 else (-1, -1)
    return (i, i + len(a))


out = []
for da in A['documents']:
    db = next(d for d in B['documents'] if d['id'] == da['id'])
    hay = fold(open(tf[da['id']]).read())
    ua = da['units']
    ub = db['units']
    sa = [span(hay, u) for u in ua]
    sb = [span(hay, u) for u in ub]
    cands = []
    for i, (a0, a1) in enumerate(sa):
        for j, (b0, b1) in enumerate(sb):
            ov = min(a1, b1) - max(a0, b0)
            if ov > 0 or -ov <= 15:
                sc = ov / max(1, min(a1 - a0, b1 - b0)) if ov > 0 else 0.01
                if ua[i]['policy_type'] == ub[j]['policy_type']:
                    sc += 0.5
                cands.append((sc, i, j))
    cands.sort(reverse=True)
    ma = {}
    mb = {}
    for sc, i, j in cands:
        if i in ma or j in mb:
            continue
        if sc < 0.2:
            continue
        ma[i] = j
        mb[j] = i
    out.append((da['id'], ma, mb))
    print('==', da['id'], len(ua), len(ub), 'matched', len(ma))
    for i, j in sorted(ma.items()):
        a = ua[i]
        b = ub[j]
        d = [k for k in ('actor', 'phase', 'modality', 'policy_type', 'unit_stance') if a[k] != b[k]]
        if d:
            print('M A%d/B%d %r' % (i, j, a['anchor'][:50]), {k: (a[k], b[k]) for k in d})
    for i in range(len(ua)):
        if i not in ma:
            print('ONLY_A', i, ua[i]['policy_type'], ua[i]['anchor'])
    for j in range(len(ub)):
        if j not in mb:
            print('ONLY_B', j, ub[j]['policy_type'], ub[j]['anchor'])
pickle.dump(out, open('v2/run/_tmp_arkansas/m.pkl', 'wb'))
