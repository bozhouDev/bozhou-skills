# 写作风格迭代工作流

## 目标
持续优化泊舟的写作风格 Skill，让 AI 生成的内容越来越接近真实风格。

## 标准流程

### 1. 生成初稿
- 加载 `bozhou-writing-style` Skill
- AI 按 Skill 生成内容
- 保存为 `draft-original.md`

### 2. 手动修改
- 泊舟手动修改到满意
- 保存为 `draft-edited.md`
- **重要**：不要在聊天里说"改这里"，直接动手改文件

### 3. 对比差异
使用以下方式之一：

**方式 A：Git diff**
```bash
git diff --no-index draft-original.md draft-edited.md
```

**方式 B：让 AI 对比**
```
对比以下两段文字：

【原文】
[粘贴 AI 生成的原文]

【修改版】
[粘贴手动修改后的版本]

请分析：
1. 我做了哪些修改
2. 修改背后的规律是什么
3. 哪些规律可以提取成通用规则
```

### 4. 提取规则
AI 分析差异后，提取 3-5 条新规则，例如：
- "删除了所有'首先、其次、最后'，改为自然过渡"
- "把'作为一名...的老兵'改成'做了X年的人'"
- "长句拆成短句，每句不超过 25 字"

### 5. 更新 Skill
- 将新规则加入 `skills/bozhou-writing-style/SKILL.md`
- 更新版本号
- 记录迭代日志

### 6. 验证效果
- 用同一个主题重新生成
- 对比新版本是否改进
- 如果还有问题，继续迭代

## 迭代节奏

- **前 3 轮**：每次写作都迭代，快速建立核心规则
- **3-10 轮**：每 2-3 次写作迭代一次，补充细节
- **10 轮后**：发现明显问题时才更新，保持稳定

## 注意事项

1. **一次只提取 3-5 条规则**，别贪多
2. **规则要具体**，不要写"语气要自然"这种虚的
3. **正反示例都要有**，AI 看例子比看规则学得快
4. **禁止清单别太长**，超过 20 条要归纳总结
5. **定期精简**，删掉重复或矛盾的规则

## 文件结构

```
skills/bozhou-writing-style/
├── SKILL.md              # 主 Skill 文件
├── iterations/           # 迭代记录
│   ├── 2026-02-28-v1.md
│   └── ...
└── examples/             # 示例文章
    ├── good/             # 符合风格的
    └── bad/              # 不符合的
```

## 快速命令

```bash
# 创建新的迭代记录
date=$(date +%Y-%m-%d)
mkdir -p skills/bozhou-writing-style/iterations
touch skills/bozhou-writing-style/iterations/$date-iteration.md

# 对比差异
git diff --no-index draft-original.md draft-edited.md > diff.txt
```

---

**记住**：这是个持续优化的过程，不是一次性任务。每次修改都是训练数据。