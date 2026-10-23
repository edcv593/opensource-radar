"""Build a static Chinese project detail page for every ranked repository."""
import html
import json
import pathlib
import shutil
from urllib.parse import quote

root=pathlib.Path(__file__).resolve().parents[1]
out=root/"dist"
data=json.loads((root/"data/ranking.json").read_text(encoding="utf-8"))
dest=out/"projects"
dest.mkdir(parents=True,exist_ok=True)
def esc(value):
    return html.escape(str(value or ""),quote=True)
for item in data.get("items",[]):
    name=item["full_name"]
    owner,repo=name.split("/",1)
    folder=dest/quote(owner,safe="")/quote(repo,safe="")
    folder.mkdir(parents=True,exist_ok=True)
    desc=item.get("description_zh") or item.get("description") or "暂无项目介绍"
    topics=" ".join("<span class='tag'>"+esc(t)+"</span>" for t in item.get("topics",[])[:12])
    def gain(key):
        val=item.get(key)
        return "历史数据积累中" if val is None else "+"+str(val)
    body=f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(name)} · 中文项目介绍 · 开源雷达</title><meta name="description" content="{esc(desc[:150])}"><style>body{{margin:0;background:#0b1220;color:#e8eefb;font:16px/1.7 system-ui,sans-serif}}main{{max-width:850px;margin:45px auto;padding:0 20px}}a{{color:#79bbff}}.card{{background:#121e31;border:1px solid #293951;border-radius:14px;padding:24px;margin:18px 0}}.meta{{display:flex;gap:18px;flex-wrap:wrap;color:#a6b4c9}}.tag{{display:inline-block;padding:3px 9px;margin:4px;border-radius:15px;background:#20344d}}.action{{display:inline-block;background:#67b7ff;color:#081523;text-decoration:none;font-weight:700;border-radius:9px;padding:10px 18px}}</style></head><body><main><a href="../../../">← 返回开源雷达排行榜</a><h1>{esc(name)}</h1><p>{esc(item.get("category","其他"))} · {esc(item.get("language","Other"))}</p><section class="card"><h2>项目简介</h2><p>{esc(desc)}</p>{"<p>中文介绍尚未生成，当前展示原始项目说明。</p>" if not item.get("description_zh") else ""}</section><section class="card"><h2>项目数据</h2><div class="meta"><span>⭐ {item.get("stars",0):,} Stars</span><span>7 日增长：{gain("week_growth")}</span><span>30 日增长：{gain("month_growth")}</span></div><p>最后更新：{esc(item.get("updated_at","未知"))}</p><p>以上数据来自定期采集的 GitHub 快照，非官方 Trending 排名。</p></section><section class="card"><h2>GitHub 标签</h2>{topics or "暂无标签"}</section><p><a class="action" href="{esc(item.get("url",""))}" target="_blank" rel="noopener noreferrer">访问 GitHub 项目 ↗</a></p></main></body></html>"""
    (folder/"index.html").write_text(body,encoding="utf-8")
print("Built",len(data.get("items",[])),"Chinese project detail pages")
