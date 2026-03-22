---
name: post-to-wechat
description: Posts content to WeChat Official Account (微信公众号) via API or Chrome CDP. Supports article posting (文章) with HTML, markdown, or plain text input, and image-text posting (贴图) with multiple images. Markdown article workflows default to converting ordinary external links into bottom citations for WeChat-friendly output. Use when user mentions "发布公众号", "post to wechat", "微信公众号", or "贴图/图文/文章".
version: 2.0.0
metadata:
  openclaw:
    requires:
      anyBins:
        - bun
        - npx
---

# Post to WeChat Official Account

## Language

**Match user's language**: Respond in the same language the user uses. If user writes in Chinese, respond in Chinese. If user writes in English, respond in English.

## Script Directory

**Agent Execution**: Determine this SKILL.md directory as `{baseDir}`, then use `{baseDir}/scripts/<name>.ts`. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; else suggest installing bun.

| Script | Purpose |
|--------|---------|
| `scripts/wechat-browser.ts` | Image-text posts (图文) |
| `scripts/wechat-article.ts` | Article posting via browser (文章) |
| `scripts/wechat-api.ts` | Article posting via API (文章) |
| `scripts/md-to-wechat.ts` | Markdown → WeChat-ready HTML with image placeholders |
| `scripts/check-permissions.ts` | Verify environment & permissions |

## Configuration

Config file: `~/.config/post-to-wechat/config.json`

### First-Time Setup (Step 0)

**BLOCKING**: Before ANY publishing step, check config file existence:

```bash
test -f "$HOME/.config/post-to-wechat/config.json" && echo "exists"
```

**If config exists** → load it and continue to Step 1.

**If config NOT exists** → run the setup flow below. Do NOT ask about content, themes, or publishing until setup is complete.

#### Setup Flow

Use AskUserQuestion with ALL questions in ONE call:

**Q1: Default Theme**
```yaml
header: "Theme"
question: "文章默认主题？"
options:
  - label: "default (Recommended)"
    description: "经典布局 - 居中标题带边框，白底彩色H2（默认蓝色）"
  - label: "grace"
    description: "优雅 - 文字阴影，圆角卡片，精致引用块（默认紫色）"
  - label: "simple"
    description: "简约现代 - 非对称圆角，干净留白（默认绿色）"
  - label: "modern"
    description: "大圆角，药丸形标题，宽松排版（默认橙色）"
```

**Q2: Default Color**
```yaml
header: "Color"
question: "默认颜色？（不设置则使用主题默认色）"
options:
  - label: "主题默认色 (Recommended)"
    description: "使用主题内置默认颜色"
  - label: "blue"
    description: "#0F4C81 经典蓝"
  - label: "red"
    description: "#A93226 中国红"
  - label: "green"
    description: "#009874 翡翠绿"
```
Note: User can choose "Other" to type any preset name (vermilion, yellow, purple, sky, rose, olive, black, gray, pink, orange) or hex value.

**Q3: Default Publishing Method**
```yaml
header: "Method"
question: "默认发布方式？"
options:
  - label: "api (Recommended)"
    description: "速度快，需要 API 凭证（AppID + AppSecret）"
  - label: "browser"
    description: "速度慢，需要 Chrome 和登录会话"
```

**Q4: Default Author**
```yaml
header: "Author"
question: "文章默认作者名？"
options:
  - label: "不设置"
    description: "留空，每篇文章单独指定"
```
Note: User will likely choose "Other" to type their author name.

#### Save Config

After collecting answers, create config file:

```bash
mkdir -p "$HOME/.config/post-to-wechat"
```

Write `~/.config/post-to-wechat/config.json`:

```json
{
  "app_id": "",
  "app_secret": "",
  "default_theme": "<user_choice>",
  "default_color": "<user_choice or empty>",
  "default_publish_method": "<user_choice>",
  "default_author": "<user_choice or empty>",
  "need_open_comment": 1,
  "only_fans_can_comment": 0
}
```

Tell the user:
1. Config saved to `~/.config/post-to-wechat/config.json`
2. **API credentials still need to be filled in** — guide them:
   - Visit https://mp.weixin.qq.com → 开发 → 基本配置
   - Copy AppID and AppSecret
   - Edit the config file to fill in `app_id` and `app_secret`
3. Or they can use browser method which doesn't need API credentials

Then continue to Step 1.

### Config Fields

| Field | Default | Description |
|-------|---------|-------------|
| `app_id` | `""` | WeChat App ID (required for API method) |
| `app_secret` | `""` | WeChat App Secret (required for API method) |
| `default_theme` | `"default"` | Theme: `default`, `grace`, `simple`, `modern` |
| `default_color` | `""` | Color preset or hex (empty = theme default) |
| `default_publish_method` | `"api"` | Method: `api` or `browser` |
| `default_author` | `""` | Default author name |
| `need_open_comment` | `1` | Enable comments: `1` yes, `0` no |
| `only_fans_can_comment` | `0` | Fans-only comments: `1` yes, `0` no |
| `chrome_profile_path` | `""` | Chrome profile path (auto-generated if empty) |

**Value priority**:
1. CLI arguments
2. Frontmatter
3. Config file
4. Skill defaults

## Pre-flight Check (Optional)

Before first use, suggest running the environment check. User can skip if they prefer.

```bash
${BUN_X} {baseDir}/scripts/check-permissions.ts
```

Checks: Chrome, Bun, Accessibility, clipboard, paste keystroke, API credentials.

**If any check fails**, provide fix guidance per item:

| Check | Fix |
|-------|-----|
| Chrome | Install Chrome or set `WECHAT_BROWSER_CHROME_PATH` env var |
| Bun runtime | `brew install oven-sh/bun/bun` (macOS) or `npm install -g bun` |
| Accessibility (macOS) | System Settings → Privacy & Security → Accessibility → enable terminal app |
| Clipboard copy | Ensure Swift/AppKit available (macOS Xcode CLI tools: `xcode-select --install`) |
| Paste keystroke (macOS) | Same as Accessibility fix above |
| Paste keystroke (Linux) | Install `xdotool` (X11) or `ydotool` (Wayland) |
| API credentials | Edit `~/.config/post-to-wechat/config.json`, fill in `app_id` and `app_secret` |

## Image-Text Posting (图文)

For short posts with multiple images (up to 9):

```bash
${BUN_X} {baseDir}/scripts/wechat-browser.ts --markdown article.md --images ./images/
${BUN_X} {baseDir}/scripts/wechat-browser.ts --title "标题" --content "内容" --image img.png --submit
```

See [references/image-text-posting.md](references/image-text-posting.md) for details.

## Article Posting Workflow (文章)

Copy this checklist and check off items as you complete them:

```
Publishing Progress:
- [ ] Step 0: Check config (first-time setup if needed)
- [ ] Step 1: Determine input type
- [ ] Step 2: Select method and configure credentials
- [ ] Step 3: Resolve theme/color and validate metadata
- [ ] Step 4: Publish to WeChat
- [ ] Step 5: Report completion
```

### Step 1: Determine Input Type

| Input Type | Detection | Action |
|------------|-----------|--------|
| HTML file | Path ends with `.html`, file exists | Skip to Step 3 |
| Markdown file | Path ends with `.md`, file exists | Continue to Step 2 |
| Plain text | Not a file path, or file doesn't exist | Save to markdown, continue to Step 2 |

**Plain Text Handling**:

1. Generate slug from content (first 2-4 meaningful words, kebab-case)
2. Create directory and save file:

```bash
mkdir -p "$(pwd)/post-to-wechat/$(date +%Y-%m-%d)"
# Save content to: post-to-wechat/yyyy-MM-dd/[slug].md
```

3. Continue processing as markdown file

### Step 2: Select Publishing Method and Configure

**Determine publishing method** (first match wins):
1. CLI `--method` argument
2. Config file `default_publish_method`
3. Default: `api`

| Method | Speed | Requirements |
|--------|-------|--------------|
| `api` (Default) | Fast | API credentials in config |
| `browser` | Slow | Chrome, login session |

**If API Selected - Check Credentials**:

Read config file and check if `app_id` and `app_secret` are filled in.

**If Credentials Missing - Guide Setup**:

```
WeChat API credentials not configured.

To obtain credentials:
1. Visit https://mp.weixin.qq.com
2. Go to: 开发 → 基本配置
3. Copy AppID and AppSecret
4. Edit ~/.config/post-to-wechat/config.json, fill in app_id and app_secret
```

### Step 3: Resolve Theme/Color and Validate Metadata

1. **Resolve theme** (first match wins, do NOT ask user if resolved):
   - CLI `--theme` argument
   - Config file `default_theme`
   - Fallback: `default`

2. **Resolve color** (first match wins):
   - CLI `--color` argument
   - Config file `default_color`
   - Omit if not set (theme default applies)

3. **Validate metadata** from frontmatter (markdown) or HTML meta tags (HTML input):

| Field | If Missing |
|-------|------------|
| Title | Prompt: "Enter title, or press Enter to auto-generate from content" |
| Summary | Prompt: "Enter summary, or press Enter to auto-generate (recommended for SEO)" |
| Author | Use fallback chain: CLI `--author` → frontmatter `author` → config `default_author` |

**Auto-Generation Logic**:
- **Title**: First H1/H2 heading, or first sentence
- **Summary**: First paragraph, truncated to 120 characters

4. **Cover Image Check** (required for API `article_type=news`):
   1. Use CLI `--cover` if provided.
   2. Else use frontmatter (`coverImage`, `featureImage`, `cover`, `image`).
   3. Else check article directory default path: `imgs/cover.png`.
   4. Else fallback to first inline content image.
   5. If still missing, stop and request a cover image before publishing.

### Step 4: Publish to WeChat

**CRITICAL**: Publishing scripts handle markdown conversion internally. Do NOT pre-convert markdown to HTML — pass the original markdown file directly.

**Markdown citation default**:
- For markdown input, ordinary external links are converted to bottom citations by default.
- Use `--no-cite` only if the user explicitly wants to keep ordinary external links inline.
- Existing HTML input is left as-is; no extra citation conversion is applied.

**API method** (accepts `.md` or `.html`):

```bash
${BUN_X} {baseDir}/scripts/wechat-api.ts <file> --theme <theme> [--color <color>] [--title <title>] [--summary <summary>] [--author <author>] [--cover <cover_path>] [--no-cite]
```

**CRITICAL**: Always include `--theme` parameter. Never omit it, even if using `default`. Only include `--color` if explicitly set by user or config.

**Browser method** (accepts `--markdown` or `--html`):

```bash
${BUN_X} {baseDir}/scripts/wechat-article.ts --markdown <markdown_file> --theme <theme> [--color <color>] [--no-cite]
${BUN_X} {baseDir}/scripts/wechat-article.ts --html <html_file>
```

### Step 5: Completion Report

**For API method**, include draft management link:

```
WeChat Publishing Complete!

Input: [type] - [path]
Method: API
Theme: [theme name] [color if set]

Article:
• Title: [title]
• Summary: [summary]
• Images: [N] inline images
• Comments: [open/closed], [fans-only/all users]

Result:
✓ Draft saved to WeChat Official Account
• media_id: [media_id]

Next Steps:
→ Manage drafts: https://mp.weixin.qq.com (登录后进入「内容管理」→「草稿箱」)

Files created:
[• post-to-wechat/yyyy-MM-dd/slug.md (if plain text)]
[• slug.html (converted)]
```

**For Browser method**:

```
WeChat Publishing Complete!

Input: [type] - [path]
Method: Browser
Theme: [theme name] [color if set]

Article:
• Title: [title]
• Summary: [summary]
• Images: [N] inline images

Result:
✓ Draft saved to WeChat Official Account

Files created:
[• post-to-wechat/yyyy-MM-dd/slug.md (if plain text)]
[• slug.html (converted)]
```

## Detailed References

| Topic | Reference |
|-------|-----------|
| Image-text parameters, auto-compression | [references/image-text-posting.md](references/image-text-posting.md) |
| Article themes, image handling | [references/article-posting.md](references/article-posting.md) |

## Feature Comparison

| Feature | Image-Text | Article (API) | Article (Browser) |
|---------|------------|---------------|-------------------|
| Plain text input | ✗ | ✓ | ✓ |
| HTML input | ✗ | ✓ | ✓ |
| Markdown input | Title/content | ✓ | ✓ |
| Multiple images | ✓ (up to 9) | ✓ (inline) | ✓ (inline) |
| Themes | ✗ | ✓ | ✓ |
| Auto-generate metadata | ✗ | ✓ | ✓ |
| Default cover fallback (`imgs/cover.png`) | ✗ | ✓ | ✗ |
| Comment control | ✗ | ✓ | ✗ |
| Requires Chrome | ✓ | ✗ | ✓ |
| Requires API credentials | ✗ | ✓ | ✗ |
| Speed | Medium | Fast | Slow |

## Prerequisites

**For API method**:
- Config file with `app_id` and `app_secret` filled in

**For Browser method**:
- Google Chrome
- First run: log in to WeChat Official Account (session preserved)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing API credentials | Edit `~/.config/post-to-wechat/config.json`, fill in `app_id` and `app_secret` |
| Access token error | Check if API credentials are valid and not expired |
| Not logged in (browser) | First run opens browser - scan QR to log in |
| Chrome not found | Set `WECHAT_BROWSER_CHROME_PATH` env var or install Chrome |
| Title/summary missing | Use auto-generation or provide manually |
| No cover image | Add frontmatter cover or place `imgs/cover.png` in article directory |
| Wrong comment defaults | Edit config file, adjust `need_open_comment` and `only_fans_can_comment` |
| Paste fails | Check system clipboard permissions |
| Reset config | Delete `~/.config/post-to-wechat/config.json` to trigger setup again |
