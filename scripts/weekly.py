import os,json,pathlib,datetime as dt,requests,time
ROOT=pathlib.Path(__file__).resolve().parents[1];DATA=ROOT/'data';d=json.loads((DATA/'ranking.json').read_text(encoding='utf-8'));items=d['items'][:10];today=dt.datetime.now(dt.timezone.utc).date();dest=DATA/'weekly'/f'{today}.md'
def summary(item):
 base=item['description'] or '暂无项目简介'
 key=os.getenv('AI_API_KEY');url=os.getenv('AI_BASE_URL','').rstrip('/');model=os.getenv('AI_MODEL','')
 if not(key and url and model):return base
 try:
  r=requests.post(url+'/chat/completions',headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json={'model':model,'messages':[{'role':'system','content':'用简体中文简洁介绍开源项目，只根据输入资料，禁止虚构功能或安装步骤。最多80字。'},{'role':'user','content':json.dumps(item,ensure_ascii=False)}],'temperature':0.2,'max_tokens':160},timeout=35);r.raise_for_status();return r.json()['choices'][0]['message']['content'].strip() or base
 except Exception as e:print('AI fallback',e);return base
lines=[f'# 开源雷达周刊 · {today}', '', '> 自动生成；AI 介绍仅供参考，项目详情请以原仓库为准。','']
for i,r in enumerate(items,1):
 growth='数据积累中' if r['week_growth'] is None else f"+{r['week_growth']}"
 lines.extend([f"## {i}. [{r['full_name']}]({r['url']})",'',f"⭐ {r['stars']} · 近7天增长：{growth} · {r['language']}",'',summary(r),''])
dest.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(dest)
