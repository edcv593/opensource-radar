import json,pathlib,datetime as dt
from ai import summarize
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
d=json.loads((DATA/"ranking.json").read_text(encoding="utf-8"))
today=dt.datetime.now(dt.timezone.utc).date()
dest=DATA/"weekly"/f"{today}.md"
items=d["items"]
# Prefer measured weekly gain; while snapshots mature use total stars.
items=sorted(items,key=lambda r:(r.get("week_growth") is not None,r.get("week_growth") or 0,r["stars"]),reverse=True)[:15]
lines=[f"# 开源雷达中文周刊 · {today}","","本期精选 GitHub 开源项目，基于采集候选池排序；非 GitHub 官方 Trending。",""]
for i,r in enumerate(items,1):
    gain="历史数据积累中" if r.get("week_growth") is None else "+"+str(r["week_growth"])
    lines.extend([f"## {i}. [{r['full_name']}]({r['url']})","",f"⭐ {r['stars']:,} · 7日新增 {gain} · {r['language']}","",summarize(r),""])
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text("\n".join(lines)+"\n",encoding="utf-8")
print("Weekly generated:",dest)
