---
name: ai-daily-newsletter
description: 聚合 20+ AI 信息源，生成每日 AI 日报
---

# AI 日报生成器

当用户说 "AI 日报"、"AI 新闻"、"今日 AI"、"AI daily" 时，执行以下工作流程。

## 工作流程

### 第 1 步：获取数据

运行抓取脚本收集所有源的数据：

```bash
python3 ai-daily-newsletter/scripts/fetch_ai_news.py
```

脚本输出 JSON 数组到 stdout，日志信息输出到 stderr。

**注意**：如果用户指定了不同的时间窗口，调整 `--hours` 参数（默认 24h）。

### 第 2 步：分类总结（使用 subagent 并行）

解析 JSON 输出后，按 category 分组，**尽可能使用 Agent 工具创建多个 subagent 并行处理**：

- **Subagent 1**：🔥 重大发布（announcements）— 筛选产品发布、模型发布、重大公告类条目，总结核心信息和影响,必须确定是24小时内的信息
- **Subagent 2**：🔬 研究论文（research）— 筛选 HF Papers + Arxiv + MIT Tech Review 等，总结每篇论文的创新点和影响
- **Subagent 3**：💰 行业商业 + 🛠️ 工具应用 + 🌍 政策伦理（industry + tools + policy）— 总结行业动态、开源工具、政策讨论。**对 GitHub Trending 条目**：数据中已含 `readme` 字段（README 前 500 字）；结合 `readme` 内容判断该项目是否真正与 AI 相关，不相关的直接跳过不放入日报；相关的用 `readme` 补充简介，若信息仍不足再用 `WebFetch` 读取完整 README

每个 subagent 负责：
1. 对其分组内的重要条目，根据已有信息判断是否需要阅读原文：
   - **RSS 源条目**：如果 `summary` 已有足够描述（>100 字），可直接使用，无需读全文；信息不足时再 `WebFetch` 原文
   - **HuggingFace Papers 条目**：`summary` 通常已包含论文摘要，优先使用；不足时再读原文
2. 输出该分组的中文总结文本（直接可用于日报对应 section）

如果某个分类为空，标记"今日暂无更新"。

### 第 3 步：生成日报

汇总各 subagent 的总结结果，按以下模板生成日报，保存到 `reports/YYYY-MM-DD/ai-daily.md`（用户可指定其他路径）：

```markdown
# 🤖 AI 日报 | YYYY-MM-DD

> 聚合 20+ AI 信息源，每日精选

---

## 📰 今日头条
[从全部源中挑选 3-5 个最重要的 AI 新闻，简要总结其背景和意义]

## 🔥 重大发布
[产品发布、模型发布、重大公告]
- **标题** — 核心内容简短描述(50 字以内)
  - 背景与意义
  - [原文链接]

## 🔬 研究论文
[HF Papers + Arxiv + MIT Tech Review 精选 2-5 篇]
- **论文标题** — 创新点一句话描述
  - 影响：对领域的意义
  - [论文链接] | [GitHub 链接]

## 💰 行业商业
[融资、收购、合作、市场趋势]
- **标题** — 核心信息
  - [原文链接]

## 🛠️ 工具应用
[AI 工具、框架、开源项目、实际应用]
- **repo/name** ⭐ Stars | 语言 — 简介
  - [GitHub 链接]

## 🌍 政策伦理
[AI 监管、安全讨论、社会影响]

## 📊 趋势洞察
[跨源综合分析：今日 AI 领域的模式、趋势和值得关注的方向]

---
统计: X 源 | Y 条 | 生成于 HH:MM
```

### 第 4 步：渲染 HTML 并截图

将生成的日报 Markdown 渲染为 Newsletter 风格 HTML 页面，并截取全页 PNG：

```bash
# 推荐：按分类截图，每个 section 一张图
python3 ai-daily-newsletter/scripts/render_html.py reports/YYYY-MM-DD/ai-daily.md --screenshot --split-by-section

# 备选：按固定高度切割（每张 4000px ≈ 2000px 页面内容）
python3 ai-daily-newsletter/scripts/render_html.py reports/YYYY-MM-DD/ai-daily.md --screenshot --split-height 4000
```

`--split-by-section` 模式：以 2x Retina 分辨率截全图，再按每个 `h2` 标题边界裁剪，生成 `ai-daily-01-今日头条.png`、`ai-daily-02-重大发布.png` 等分类图片。

## 规则

1. **全部输出简体中文**，技术名词保留英文（如 LLM、Transformer、RLHF）
2. **时间字段必填**，缺失标记"时间未知"
3. **禁止编造**：只使用 JSON 数据和 WebFetch 获取的原文信息
4. **空 section 写 "今日暂无更新"**，不凑数
5. **默认保存到 `reports/YYYY-MM-DD/ai-daily.md`**，用户可指定其他路径
6. 生成完成后告知用户保存路径和统计信息

## 分类体系

| category | 标签 | 含义 |
|----------|------|------|
| announcements | 🔥 重大发布 | 产品发布、模型发布、重大公告 |
| research | 🔬 研究论文 | 学术突破、研究论文、新技术 |
| industry | 💰 行业商业 | 融资、收购、合作、市场趋势 |
| tools | 🛠️ 工具应用 | AI 工具、框架、开源项目、实际应用 |
| policy | 🌍 政策伦理 | AI 监管、安全讨论、社会影响 |

## 信息源

脚本抓取以下 20+ 源：

**主流 AI 媒体（5 个）：**
- VentureBeat AI、TechCrunch AI、The Verge AI、MIT Technology Review AI、AI News

**AI 公司博客（6 个）：**
- OpenAI Blog、Anthropic Blog、Google AI Blog、DeepMind Blog、Microsoft AI Blog、Meta AI Blog

**AI Newsletters（5 个）：**
- Latent Space AINews、Interconnects、One Useful Thing、ChinAI、The Batch

**AI Bloggers（2 个）：**
- Simon Willison、Gary Marcus

**论文（2 个）：**
- Arxiv cs.AI、Arxiv cs.LG

**产品（1 个）：**
- Product Hunt

**API/爬取源（2 个）：**
- HuggingFace Papers（网页抓取）
- GitHub Trending（网页抓取 + AI 过滤）
