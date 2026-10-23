"""Incremental Chinese summaries for the public ranking; bounded daily AI usage."""
import datetime as dt
import hashlib
import json
import os
import pathlib
from ai import summarize

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
RANKING=DATA/"ranking.json"
CACHE=DATA/"ai-cache.json"
STATE=DATA/"translation-state.json"
def read(path,default):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError,json.JSONDecodeError):return default
def save(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def key_for(item):
    raw=(item.get("description","")+"|"+str(item.get("topics",[]))).encode("utf-8")
    return item["full_name"]+"@"+hashlib.sha256(raw).hexdigest()[:16]
def chinese(text):
    return any("\u4e00"<=c<="\u9fff" for c in text)
def main():
    ranking=read(RANKING,{})
    items=ranking.get("items",[])
    cache=read(CACHE,{})
    state=read(STATE,{})
    today=dt.datetime.now(dt.timezone.utc).date().isoformat()
    limit=max(0,min(int(os.getenv("ZH_DAILY_LIMIT","25")),100))
    spent=state.get("attempts",0) if state.get("date")==today else 0
    remaining=max(0,limit-spent)
    translated=0
    # Prioritize prominent projects, then work through missing summaries on subsequent days.
    for item in items:
        key=key_for(item)
        cached=cache.get(key)
        if cached and chinese(cached):
            item["description_zh"]=cached
            continue
        item.pop("description_zh",None)
        if chinese(item.get("description","")):
            item["description_zh"]=item["description"]
            continue
        if remaining<=0:continue
        remaining-=1
        spent+=1
        state={"date":today,"attempts":spent}
        save(STATE,state)
        result=summarize(item)
        if result and chinese(result):
            cache[key]=result
            item["description_zh"]=result
            translated+=1
            save(CACHE,cache)
    ranking["zh_coverage"]=sum(bool(i.get("description_zh")) for i in items)
    ranking["zh_total"]=len(items)
    save(RANKING,ranking)
    save(CACHE,cache)
    print("Chinese coverage:",ranking["zh_coverage"],"/",len(items),"new:",translated,"daily attempts:",spent,"limit:",limit)
if __name__=="__main__":
    main()
