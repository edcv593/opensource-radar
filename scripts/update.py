import os,json,datetime as dt,time,requests,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
(DATA/'snapshots').mkdir(parents=True,exist_ok=True)
(DATA/'weekly').mkdir(exist_ok=True)
TODAY=dt.datetime.now(dt.timezone.utc).date()
TOKEN=os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN','')
S=requests.Session()
S.headers.update({'Accept':'application/vnd.github+json','User-Agent':'opensource-radar/2.2',**({'Authorization':f'Bearer {TOKEN}'} if TOKEN else {})})
def get(url,params=None):
 for i in range(4):
  try:
   r=S.get(url,params=params,timeout=25)
   if r.status_code in (403,429,500,502,503,504):
    if i==3:raise RuntimeError(f'GitHub API HTTP {r.status_code}')
    time.sleep(min(2**i*3,24));continue
   r.raise_for_status();return r.json()
  except requests.RequestException:
   if i==3:raise
   time.sleep(2**i)
 raise RuntimeError('GitHub API unavailable')
CATEGORIES={
 'AI / 大模型':['ai','artificial-intelligence','llm','large-language-model','machine-learning','deep-learning','generative-ai'],
 'AI Agent':['agent','ai-agent','ai-agents','agents','mcp','model-context-protocol'],
 'NAS / 自托管':['self-hosted','selfhosted','homelab','nas','home-server'],
 'Docker / 运维':['docker','kubernetes','devops','container','containers','monitoring'],
 '开发工具':['developer-tools','cli','editor','ide','programming','code-editor'],
 '自动化 / 效率':['automation','workflow','productivity','n8n','workflow-automation'],
 '数据 / 数据库':['database','postgresql','mysql','data-engineering','analytics'],
 '安全 / 隐私':['security','privacy','cybersecurity','infosec']
}
def category_of(row):
 topics=set(t.lower() for t in row.get('topics',[]))
 name=(row.get('full_name','')+' '+row.get('description','')).lower()
 for label,keywords in CATEGORIES.items():
  if any(t in topics for t in keywords):return label
 if 'docker' in name:return 'Docker / 运维'
 return '其他'
def score_of(row):
 growth=row.get('week_growth')
 # Score is a transparent heuristic, not AI judgment.
 if growth is None:return None
 return round(growth*1.0 + min(row['stars'],100000)**0.5*0.12,2)
def read(p,default):
 try:return json.loads(p.read_text(encoding='utf-8'))
 except (FileNotFoundError,json.JSONDecodeError):return default
previous=read(DATA/'repos.json',[])
found={r['full_name']:r for r in previous if r.get('full_name')}
# Diverse discovery pools, sorted by stars and recent updates; not official Trending.
queries=[
 ('stars:>100 pushed:>'+str(TODAY-dt.timedelta(days=45)),'updated'),
 ('created:>'+str(TODAY-dt.timedelta(days=30))+' stars:>30','stars'),
 ('topic:artificial-intelligence stars:>100','updated'),
 ('topic:llm stars:>100','updated'),
 ('topic:ai-agents stars:>30','updated'),
 ('topic:self-hosted stars:>100','updated'),
 ('topic:docker stars:>100','updated'),
 ('topic:developer-tools stars:>100','updated'),
 ('topic:automation stars:>100','updated'),
 ('topic:open-source stars:>100','updated'),
]
success=0
for q,sort in queries:
 try:
  items=get('https://api.github.com/search/repositories',{'q':q,'sort':sort,'order':'desc','per_page':100}).get('items',[])
  success+=1
  for item in items:
   if item.get('archived') or item.get('fork'):continue
   name=item['full_name']
   found[name]={'full_name':name,'url':item['html_url'],'description':item.get('description') or '', 'stars':item['stargazers_count'],'language':item.get('language') or 'Other','topics':item.get('topics',[]),'updated_at':item.get('updated_at'),'created_at':item.get('created_at')}
 except Exception as e:print('Source failed:',q,str(e)[:180])
if not found:raise RuntimeError('No repository data; refusing empty publish')
# Retain all known candidates (bounded) so projects can accumulate measured history.
rows=sorted(found.values(),key=lambda r:r['stars'],reverse=True)[:1200]
snap=DATA/'snapshots'/f'{TODAY.isoformat()}.json'
snap.write_text(json.dumps({r['full_name']:r['stars'] for r in rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def baseline(days):
 files=sorted((DATA/'snapshots').glob('*.json'))
 eligible=[p for p in files if p.stem<=(TODAY-dt.timedelta(days=days)).isoformat()]
 return read(eligible[-1],{}) if eligible else {}
day=baseline(1);week=baseline(7);month=baseline(30)
for r in rows:
 for key,old in [('day_growth',day),('week_growth',week),('month_growth',month)]:
  r[key]=max(0,r['stars']-old[r['full_name']]) if r['full_name'] in old else None
 r['category']=category_of(r)
 r['trend_score']=score_of(r)
ranks=sorted(rows,key=lambda r:(r['day_growth'] is not None,r['day_growth'] or 0,r['stars']),reverse=True)
(DATA/'repos.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DATA/'ranking.json').write_text(json.dumps({'updated_at':TODAY.isoformat(),'day_ready':bool(day),'week_ready':bool(week),'month_ready':bool(month),'total_candidates':len(rows),'successful_sources':success,'items':ranks[:500]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Saved',len(rows),'repositories; successful discovery sources:',success)
