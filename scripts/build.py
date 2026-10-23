import pathlib,json,html,re,shutil
root=pathlib.Path(__file__).resolve().parents[1];site=root/'site';out=root/'dist';shutil.rmtree(out,ignore_errors=True);shutil.copytree(site,out);(out/'data').mkdir();shutil.copy(root/'data/ranking.json',out/'data/ranking.json');(out/'weekly').mkdir()
files=sorted((root/'data/weekly').glob('*.md'),reverse=True);(out/'data/weekly-index.json').write_text(json.dumps([f.stem for f in files],ensure_ascii=False),encoding='utf-8')
for p in files:
 lines=[]
 for line in p.read_text(encoding='utf-8').splitlines():
  if line.startswith('# '):lines.append('<h1>'+html.escape(line[2:])+'</h1>')
  elif line.startswith('## '):
   m=re.match(r'## (\d+)\. \[(.*?)\]\((https://github.com/[^)]+)\)',line)
   lines.append(f'<h2>{m.group(1)}. <a href="{html.escape(m.group(3),quote=True)}">{html.escape(m.group(2))}</a></h2>' if m else '<h2>'+html.escape(line[3:])+'</h2>')
  elif line.strip():lines.append('<p>'+html.escape(line.lstrip('> '))+'</p>')
 (out/'weekly'/f'{p.stem}.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>开源雷达周刊</title><style>body{max-width:800px;margin:40px auto;padding:0 20px;font:17px/1.7 system-ui;background:#0b1220;color:#e8eefb}a{color:#79bbff}</style><a href="../">← 返回榜单</a>'+''.join(lines)+'</html>',encoding='utf-8')
