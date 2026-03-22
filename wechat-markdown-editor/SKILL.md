---
name: wechat-markdown-editor
description: 专业的微信公众号排版工具。将 Markdown 转换为带样式的 HTML，包含微信兼容主题（字节范等）。支持代码高亮、数学公式、PlantUML、脚注、警告框及外链底部引用。
version: 1.56.1
metadata:
  openclaw:
    homepage: https://github.com/bozhouDev/bozhou-skills/wechat-markdown-editor
    requires:
      anyBins:
        - bun
        - npx
---

# Markdown to HTML Converter

Converts Markdown files to beautifully styled HTML with inline CSS, optimized for WeChat Official Account and other platforms.

## Script Directory

**Agent Execution**: Determine this SKILL.md directory as `{baseDir}`. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; else suggest installing bun. Replace `{baseDir}` and `${BUN_X}` with actual values.

| Script | Purpose |
|--------|---------|
| `scripts/main.ts` | Main entry point |

## Workflow

### Step 0: Pre-check (Chinese Content)

**Condition**: Only execute if input file contains Chinese text.

**Detection**:
1. Read input markdown file
2. Check if content contains CJK characters (Chinese/Japanese/Korean)
3. If no CJK content → skip to Step 1

**Format Suggestion**:

If CJK content detected AND `format-markdown` skill is available:

Use `AskUserQuestion` to ask whether to format first. Formatting can fix:
- Bold markers with punctuation inside causing `**` parse failures
- CJK/English spacing issues

**If user agrees**: Invoke `format-markdown` skill to format the file, then use formatted file as input.

**If user declines**: Continue with original file.

### Step 1: Determine Theme

**Default theme**: `bytedance` (字节范)

If the user explicitly specifies a different theme via CLI `--theme` or in conversation, use that instead. Otherwise always use `bytedance`.

### Step 1.5: Determine Citation Mode

**Default**: Off. Do not ask by default.

**Enable only if the user explicitly asks** for "微信外链转底部引用", "底部引用", "文末引用", or passes `--cite`.

**Behavior when enabled**:
- Ordinary external links are rendered with numbered superscripts and collected under a final `引用链接` section.
- `https://mp.weixin.qq.com/...` links stay as direct links and are not moved to the bottom.
- Bare links where link text equals URL stay inline.

### Step 2: Convert

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown_file> --theme <theme> [--cite]
```

### Step 3: Report Result

Display the output path from JSON result. If backup was created, mention it.

## Usage

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown_file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--theme <name>` | Theme name (default, grace, simple, modern, bytedance) | bytedance |
| `--color <name\|hex>` | Primary color: preset name or hex value | theme default |
| `--font-family <name>` | Font: sans, serif, serif-cjk, mono, or CSS value | theme default |
| `--font-size <N>` | Font size: 14px, 15px, 16px, 17px, 18px | 16px |
| `--title <title>` | Override title from frontmatter | |
| `--cite` | Convert external links to bottom citations, append `引用链接` section | false (off) |
| `--keep-title` | Keep the first heading in content | false (removed) |
| `--help` | Show help | |

**Color Presets:**

| Name | Hex | Label |
|------|-----|-------|
| blue | #0F4C81 | Classic Blue |
| green | #009874 | Emerald Green |
| vermilion | #FA5151 | Vibrant Vermilion |
| yellow | #FECE00 | Lemon Yellow |
| purple | #92617E | Lavender Purple |
| sky | #55C9EA | Sky Blue |
| rose | #B76E79 | Rose Gold |
| olive | #556B2F | Olive Green |
| black | #333333 | Graphite Black |
| gray | #A9A9A9 | Smoke Gray |
| pink | #FFB7C5 | Sakura Pink |
| red | #A93226 | China Red |
| orange | #D97757 | Warm Orange (modern default) |

**Examples:**

```bash
# Basic conversion (uses default theme, removes first heading)
${BUN_X} {baseDir}/scripts/main.ts article.md

# With specific theme
${BUN_X} {baseDir}/scripts/main.ts article.md --theme grace

# Theme with custom color
${BUN_X} {baseDir}/scripts/main.ts article.md --theme modern --color red

# Enable bottom citations for ordinary external links
${BUN_X} {baseDir}/scripts/main.ts article.md --cite

# Keep the first heading in content
${BUN_X} {baseDir}/scripts/main.ts article.md --keep-title

# Override title
${BUN_X} {baseDir}/scripts/main.ts article.md --title "My Article"
```

## Output

**File location**: Same directory as input markdown file.
- Input: `/path/to/article.md`
- Output: `/path/to/article.html`

**Conflict handling**: If HTML file already exists, it will be backed up first:
- Backup: `/path/to/article.html.bak-YYYYMMDDHHMMSS`

**JSON output to stdout:**

```json
{
  "title": "Article Title",
  "author": "Author Name",
  "summary": "Article summary...",
  "htmlPath": "/path/to/article.html",
  "backupPath": "/path/to/article.html.bak-20260128180000",
  "contentImages": [
    {
      "placeholder": "MDTOHTMLIMGPH_1",
      "localPath": "/path/to/img.png",
      "originalPath": "imgs/image.png"
    }
  ]
}
```

## Themes

| Theme | Description |
|-------|-------------|
| `default` | Classic - traditional layout, centered title with bottom border, H2 with white text on colored background |
| `grace` | Elegant - text shadow, rounded cards, refined blockquotes |
| `simple` | Minimal - modern minimalist, asymmetric rounded corners, clean whitespace |
| `modern` | Modern - large radius, pill-shaped titles, relaxed line height (pair with `--color red` for traditional red-gold style) |
| `bytedance` | ByteDance (字节范) - technological and modern blue style |

## Supported Markdown Features

| Feature | Syntax |
|---------|--------|
| Headings | `# H1` to `###### H6` |
| Bold/Italic | `**bold**`, `*italic*` |
| Code blocks | ` ```lang ` with syntax highlighting |
| Inline code | `` `code` `` |
| Tables | GitHub-flavored markdown tables |
| Images | `![alt](src)` |
| Links | `[text](url)`; add `--cite` to move ordinary external links into bottom references |
| Blockquotes | `> quote` |
| Lists | `-` unordered, `1.` ordered |
| Alerts | `> [!NOTE]`, `> [!WARNING]`, etc. |
| Footnotes | `[^1]` references |
| Ruby text | `{base|annotation}` |
| Mermaid | ` ```mermaid ` diagrams |
| PlantUML | ` ```plantuml ` diagrams |

## Frontmatter

Supports YAML frontmatter for metadata:

```yaml
---
title: Article Title
author: Author Name
description: 专业的微信公众号排版工具。将 Markdown 转换为带样式的 HTML，包含微信兼容主题（字节范等）。支持代码高亮、数学公式、PlantUML、脚注、警告框及外链底部引用。
---
```

If no title is found, extracts from first H1/H2 heading or uses filename.

