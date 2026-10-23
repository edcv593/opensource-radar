# OpenSource Radar / 开源雷达

**🌐 [立即访问开源雷达网站](https://edcv593.github.io/opensource-radar/)** · [自动更新工作流](https://github.com/edcv593/opensource-radar/actions/workflows/radar.yml)


自动采集 GitHub 仓库、保存每日 Star 快照、展示周增长榜、每周生成中文开源周刊，发布到 GitHub Pages。

## 使用
1. 创建公开仓库 `edcv593/opensource-radar`，上传本项目所有文件（包括 `.github`）。
2. Settings → Actions → General → Workflow permissions：选择 **Read and write permissions**。
3. Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
4. Actions → Radar Update and Publish → Run workflow，首次运行后访问 `https://edcv593.github.io/opensource-radar/`。
5. AI 可选：Settings → Secrets and variables → Actions：Secret `AI_API_KEY`；Variables `AI_BASE_URL`（例如 `https://api.example.com/v1`）、`AI_MODEL`。不填则直接使用原始项目描述，不会阻止发布。

## 统计口径
每天 09:17（北京时间）计划运行，GitHub Actions 定时任务可能延迟。7/30 日增长是当前快照与不晚于 7/30 天前的最新快照的差值；快照不足时显示“积累中”。不是 GitHub 官方 Trending 榜单。搜索候选池受 API 查询、配额和采集上限限制，排名仅针对已采集项目。

## 手动本地运行
```bash
pip install -r requirements.txt
python scripts/update.py
python scripts/weekly.py
python scripts/build.py
python -m http.server 8000 -d dist
```
浏览 `http://localhost:8000`。周刊每周一生成；手动运行 workflow 会立即生成周刊；定时任务每周一生成周刊。

## 下一阶段
V2: GitHub Trending 候选源、全量历史库、主题订阅、结构化中文分析、AI 多提供商故障切换和缓存、RSS、编辑审核、自动周刊精选评分。现已支持通过 GitHub Secret `AI_PROVIDERS_JSON` 配置多个兼容 API 服务商，按顺序尝试并在失败时回退；全部失败则保留原始描述。
