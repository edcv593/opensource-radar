"""Optional OpenAI-compatible providers; failure never blocks publishing."""
import json,os,time,requests
def summarize(item):
    fallback=item.get("description") or "暂无项目简介"
    providers=[]
    raw=os.getenv("AI_PROVIDERS_JSON","").strip()
    if raw:
        try:
            for p in json.loads(raw):
                key=os.getenv(p.get("key_env",""),"") if p.get("key_env") else p.get("api_key","")
                if key and p.get("base_url") and p.get("model"):providers.append((p["base_url"],p["model"],key))
        except (ValueError,TypeError) as e:print("Invalid AI_PROVIDERS_JSON",e)
    key=os.getenv("AI_API_KEY","")
    if key and os.getenv("AI_BASE_URL") and os.getenv("AI_MODEL"):
        providers.append((os.getenv("AI_BASE_URL"),os.getenv("AI_MODEL"),key))
    for url,model,key in providers:
        endpoint=url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):endpoint+="/chat/completions"
        for attempt in range(2):
            try:
                r=requests.post(endpoint,headers={"Authorization":"Bearer "+key},json={"model":model,"messages":[{"role":"system","content":"你是中文开源项目编辑。仅根据给定信息用简体中文概括项目用途、适合人群与亮点，最多90字，不得编造。只输出摘要。"},{"role":"user","content":json.dumps({"name":item.get("full_name"),"description":fallback,"language":item.get("language"),"topics":item.get("topics",[])},ensure_ascii=False)}],"temperature":0.2,"max_tokens":180},timeout=22)
                if r.status_code in (401,403):break
                r.raise_for_status()
                content=r.json()["choices"][0]["message"]["content"].strip()
                if content:return content
            except (requests.RequestException,ValueError,KeyError,IndexError,TypeError) as e:
                print("AI provider fallback:",str(e)[:160])
            if attempt==0:time.sleep(1)
    return fallback
