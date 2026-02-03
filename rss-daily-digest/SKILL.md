---
name: rss-daily-digest
description: |
  RSS 日报生成器 - 从技术博客 RSS 源获取 24 小时内的文章,总结翻译成中文日报。
  触发场景: 用户请求生成博客日报、RSS 摘要、技术资讯汇总时使用。
---

# RSS 日报生成器

从 90+ 个技术博客 RSS 源获取最近 24 小时内的文章,总结并翻译成中文日报。

## 工作流程

1. 运行脚本获取 RSS 内容:
```bash
python3 /Users/xc/my/notes/.claude/skills/rss-daily-digest/scripts/fetch_rss.py
```

2. 分析返回的 JSON,筛选有价值的文章

3. **抓取每篇文章原文** (使用 WebFetch),深度阅读后:
   - 翻译标题为中文
   - 总结核心内容,每篇不超过 500 字
   - 保留原文链接

4. 生成日报文件:
   - 路径: `/Users/xc/my/notes/灵感库/博客日报/YYYY-MM-DD-标题.md`
   - 标题根据当日热点内容提炼

## 翻译规则

技术名词保留英文,不直译:
- Claude → Claude (不译为"克劳德")
- Docker, Kubernetes, React, Node.js 等保持原样
- API, SDK, CLI 等缩写保持原样
- 公司/产品名: OpenAI, Anthropic, GitHub 等保持原样

## 日报格式

```markdown
# [当日热点主题]

> 生成日期: YYYY-MM-DD

## 今日精选

### [中文标题]
**来源**: [博客名] | [原文链接](url)

[1-2 句中文摘要]

---

[更多文章...]

## 统计
- 共收录 X 篇文章
- 涵盖 Y 个信息源
```

## 注意事项

- 若无 24 小时内新文章,告知用户"今日暂无更新"
- 优先选择有深度的技术文章
- 标题翻译保持简洁,避免直译
