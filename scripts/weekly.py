import json,pathlib,datetime as dt,hashlib
from ai import summarize
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
d=json.loads((DATA/"ranking.json").read_text(encoding="utf-8"))
today=dt.datetime.now(dt.timezone.utc).date()
dest=DATA/"weekly"/f"{today}.md"
items=d["items"]
cache_path=DATA/"ai-cache.json"
try: cache=json.loads(cache_path.read_text(encoding="utf-8"))
except (FileNotFoundError,json.JSONDecodeError): cache={}
new_calls=0
def cached_summary(item):
    global new_calls
    fingerprint=hashlib.sha256((item.get("description","")+"|"+str(item.get("topics",[]))).encode("utf-8")).hexdigest()[:16]
    key=item["full_name"]+"@"+fingerprint
    if key in cache:return cache[key]
    result=summarize(item)
    # Do not cache raw English fallback: allow retry when API recovers.
    if result and result!=item.get("description","") and result!="暂无项目简介":
        cache[key]=result
    new_calls+=1
    return result
# Prefer measured weekly gain; while snapshots mature use total stars.
items=sorted(items,key=lambda r:(r.get("week_growth") is not None,r.get("week_growth") or 0,r["stars"]),reverse=True)[:15]
lines=[f"# 开源雷达中文周刊 · {today}","","本期精选 GitHub 开源项目，基于采集候选池排序；非 GitHub 官方 Trending。",""]
for i,r in enumerate(items,1):
    gain="历史数据积累中" if r.get("week_growth") is None else "+"+str(r["week_growth"])
    lines.extend([f"## {i}. [{r['full_name']}]({r['url']})","",f"⭐ {r['stars']:,} · 7日新增 {gain} · {r['language']}","",cached_summary(r),""])
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text("\n".join(lines)+"\n",encoding="utf-8")
cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("AI new attempts:",new_calls,"cache entries:",len(cache))
print("Weekly generated:",dest)
