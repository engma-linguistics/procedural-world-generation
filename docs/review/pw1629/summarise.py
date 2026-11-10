import json, sys
rows=[json.loads(l) for l in open(sys.argv[1]) if l.startswith('{')]
for sea in ('tide','wave','river'):
  print(sea)
  for P in sorted({r['P'] for r in rows}):
    rr=[r for r in rows if r['P']==P and r['sea']==sea]
    if rr: print(int(P), rr[0]['q'], 'nb',rr[0]['nb'],'mouths',[r['mouths'] for r in rr],'rough',[round(r['rough'],2) for r in rr],'near',[round(r['sea_near'],2) for r in rr], [r['type'][:4] for r in rr])
