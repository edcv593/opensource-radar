import os,json,datetime as dt,time,requests,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; (DATA/'snapshots').mkdir(parents=True,exist_ok=True);(DATA/'weekly').mkdir(exist_ok=True)
TODAY=dt.datetime.now(dt.timezone.utc).date(); TOKEN=os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN','')
S=requests.Session();S.headers.update({'Accept':'application/vnd.github+json','User-Agent':'opensource-radar/1.0',**({'Authorization':f'Bearer {TOKEN}'} if TOKEN else {})})
def get(url,params=None):
 for i in range(4):
  try:
   r=S.get(url,params=params,timeout=25)
   if r.status_code in (403,429,500,502,503,504):time.sleep(min(2**i*3,30));continue
   r.raise_for_status();return r.json()
  except requests.RequestException:
   if i==3:raise
   time.sleep(2**i)
 raise RuntimeError('API unavailable')
def read(p,default):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except (FileNotFoundError,json.JSONDecodeError):return default
previous=read(DATA/'repos.json',[]); found={r['full_name']:r for r in previous}
queries=['stars:>100 pushed:>2026-01-01','topic:ai stars:>100','topic:docker stars:>100','topic:self-hosted stars:>100']
for q in queries:
 try:
  for item in get('https://api.github.com/search/repositories',{'q':q,'sort':'updated','order':'desc','per_page':50}).get('items',[]):
   if item.get('archived') or item.get('fork'):continue
   name=item['full_name'];found[name]={'full_name':name,'url':item['html_url'],'description':item.get('description') or '', 'stars':item['stargazers_count'],'language':item.get('language') or 'Other','topics':item.get('topics',[]),'updated_at':item.get('updated_at'),'created_at':item.get('created_at')}
 except Exception as e:print('source failed',q,e)
if not found:raise RuntimeError('No repository data; refusing empty publish')
rows=list(found.values());rows.sort(key=lambda r:r['stars'],reverse=True);rows=rows[:350]
snap=DATA/'snapshots'/f'{TODAY.isoformat()}.json'; snap.write_text(json.dumps({r['full_name']:r['stars'] for r in rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def baseline(days):
 files=sorted((DATA/'snapshots').glob('*.json'));target=TODAY-dt.timedelta(days=days)
 eligible=[p for p in files if p.stem<=target.isoformat()]
 return read(eligible[-1],{}) if eligible else {}
week=baseline(7);month=baseline(30)
for r in rows:
 for key,old in [('week_growth',week),('month_growth',month)]:r[key]=max(0,r['stars']-old[r['full_name']]) if r['full_name'] in old else None
ranks=sorted(rows,key=lambda r:(r['week_growth'] is not None,r['week_growth'] or 0,r['stars']),reverse=True)
(DATA/'repos.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DATA/'ranking.json').write_text(json.dumps({'updated_at':TODAY.isoformat(),'week_ready':bool(week),'items':ranks[:100]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('saved',len(rows),'repositories')
