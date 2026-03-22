---
name: social-cover-image
description: Generates social cover images for articles, banners, and social posts with 5 dimensions (type, palette, rendering, text, mood) combining 10 color palettes and 7 rendering styles. Supports cinematic (2.35:1), widescreen (16:9), and square (1:1) aspects. Use when user asks to "generate cover image", "create social cover", "make banner", or "make cover".
version: 1.56.1
---

# Social Cover Image Generator

Generate elegant social cover images with 5-dimensional customization.

## Usage

```bash
# Auto-select dimensions based on content
/social-cover-image path/to/article.md

# Quick mode: skip confirmation
/social-cover-image article.md --quick

# Specify dimensions
/social-cover-image article.md --type conceptual --palette warm --rendering flat-vector

# Style presets (shorthand for palette + rendering)
/social-cover-image article.md --style blueprint

# With reference images
/social-cover-image article.md --ref style-ref.png

# Direct content input
/social-cover-image --palette mono --aspect 1:1 --quick
[paste content]
```

## Options

| Option | Description |
|--------|-------------|
| `--type <name>` | hero, conceptual, typography, metaphor, scene, minimal |
| `--palette <name>` | warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone |
| `--rendering <name>` | flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print |
| `--style <name>` | Preset shorthand (see [Style Presets](references/style-presets.md)) |
| `--text <level>` | none, title-only, title-subtitle, text-rich |
| `--mood <level>` | subtle, balanced, bold |
| `--font <name>` | clean, handwritten, serif, display |
| `--aspect <ratio>` | 16:9 (default), 2.35:1, 4:3, 3:2, 1:1, 3:4 |
| `--lang <code>` | Title language (en, zh, ja, etc.) |
| `--no-title` | Alias for `--text none` |
| `--quick` | Skip confirmation, use auto-selection |
| `--ref <files...>` | Reference images for style/composition guidance |

## Platform Aspect Guide

Use platform-specific aspect ratios when the publication target is known:

| Platform | Recommended Ratio | Notes |
|----------|-------------------|-------|
| WeChat article header | `2.35:1` | Best fit for WeChat public account article covers and blog headers |
| X header / social banner | `5:2` | Platform target ratio; current built-in generator does not output `5:2` directly, so generate a wide image first and crop afterward |
| General-purpose cover | `16:9` | Good default for mixed channels, slides, and thumbnails |
| Square social card | `1:1` | Best for square-first social placements |

Examples:

```bash
# WeChat public account article cover
/social-cover-image article.md --aspect 2.35:1

# X banner workflow: generate wide, then crop to 5:2 in post-processing
/social-cover-image article.md --aspect 16:9
```

## Five Dimensions

| Dimension | Values | Default |
|-----------|--------|---------|
| **Type** | hero, conceptual, typography, metaphor, scene, minimal | auto |
| **Palette** | warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone | auto |
| **Rendering** | flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print | auto |
| **Text** | none, title-only, title-subtitle, text-rich | title-only |
| **Mood** | subtle, balanced, bold | balanced |
| **Font** | clean, handwritten, serif, display | clean |

Auto-selection rules: [references/auto-selection.md](references/auto-selection.md)

## Galleries

**Types**: hero, conceptual, typography, metaphor, scene, minimal
→ Details: [references/types.md](references/types.md)

**Palettes**: warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone
→ Details: [references/palettes/](references/palettes/)

**Renderings**: flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print
→ Details: [references/renderings/](references/renderings/)

**Text Levels**: none (pure visual) | title-only (default) | title-subtitle | text-rich (with tags)
→ Details: [references/dimensions/text.md](references/dimensions/text.md)

**Mood Levels**: subtle (low contrast) | balanced (default) | bold (high contrast)
→ Details: [references/dimensions/mood.md](references/dimensions/mood.md)

**Fonts**: clean (sans-serif) | handwritten | serif | display (bold decorative)
→ Details: [references/dimensions/font.md](references/dimensions/font.md)

## File Structure

Output directory per `default_output_dir` preference:
- `same-dir`: `{article-dir}/`
- `imgs-subdir`: `{article-dir}/imgs/`
- `independent` (default): `cover-image/{topic-slug}/`

```
<output-dir>/
├── source-{slug}.{ext}    # Source files
├── refs/                  # Reference images (if provided)
│   ├── ref-01-{slug}.{ext}
│   └── ref-01-{slug}.md   # Description file
├── prompts/cover.md       # Generation prompt
└── cover.png              # Output image
```

**Slug**: 2-4 words, kebab-case. Conflict: append `-YYYYMMDD-HHMMSS`

## Workflow

### Progress Checklist

```
Cover Image Progress:
- [ ] Step 0: Check preferences (EXTEND.md) ⛔ BLOCKING
- [ ] Step 1: Analyze content + save refs + determine output dir
- [ ] Step 2: Confirm options (6 dimensions) ⚠️ unless --quick
- [ ] Step 3: Create prompt
- [ ] Step 4: Generate image
- [ ] Step 5: Completion report
```

### Flow

```
Input → [Step 0: Preferences] ─┬─ Found → Continue
                               └─ Not found → First-Time Setup ⛔ BLOCKING → Save EXTEND.md → Continue
        ↓
Analyze + Save Refs → [Output Dir] → [Confirm: 6 Dimensions] → Prompt → Generate → Complete
                                              ↓
                                     (skip if --quick or all specified)
```

### Step 0: Load Preferences ⛔ BLOCKING

Check EXTEND.md existence (priority: project → user):
```bash
# macOS, Linux, WSL, Git Bash
test -f .my-tools/social-cover-image/EXTEND.md && echo "project"
test -f "${XDG_CONFIG_HOME:-$HOME/.config}/social-cover-image/EXTEND.md" && echo "xdg"
test -f "$HOME/.my-tools/social-cover-image/EXTEND.md" && echo "user"
```

```powershell
# PowerShell (Windows)
if (Test-Path .my-tools/social-cover-image/EXTEND.md) { "project" }
$xdg = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { "$HOME/.config" }
if (Test-Path "$xdg/social-cover-image/EXTEND.md") { "xdg" }
if (Test-Path "$HOME/.my-tools/social-cover-image/EXTEND.md") { "user" }
```

| Result | Action |
|--------|--------|
| Found | Load, display summary → Continue |
| Not found | ⛔ Run first-time setup ([references/config/first-time-setup.md](references/config/first-time-setup.md)) → Save → Continue |

**CRITICAL**: If not found, complete setup BEFORE any other steps or questions.

### Step 1: Analyze Content

1. **Save reference images** (if provided) → [references/workflow/reference-images.md](references/workflow/reference-images.md)
2. **Save source content** (if pasted, save to `source.md`)
3. **Analyze content**: topic, tone, keywords, visual metaphors
4. **Deep analyze references** ⚠️: Extract specific, concrete elements (see reference-images.md)
   - If references contain **people** → set `usage: direct` so model sees reference image, describe character features for stylized preservation (see reference-images.md § Character Analysis)
5. **Detect language**: Compare source, user input, EXTEND.md preference
6. **Determine output directory**: Per File Structure rules

### Step 2: Confirm Options ⚠️

Full confirmation flow: [references/workflow/confirm-options.md](references/workflow/confirm-options.md)

| Condition | Skipped | Still Asked |
|-----------|---------|-------------|
| `--quick` or `quick_mode: true` | 6 dimensions | Aspect ratio (unless `--aspect`) |
| All 6 + `--aspect` specified | All | None |

### Step 3: Create Prompt

Save to `prompts/cover.md`. Template: [references/workflow/prompt-template.md](references/workflow/prompt-template.md)

**CRITICAL - References in Frontmatter**:
- Files saved to `refs/` → Add to frontmatter `references` list
- Style extracted verbally (no file) → Omit `references`, describe in body
- Before writing → Verify: `test -f refs/ref-NN-{slug}.{ext}`

**Reference elements in body** MUST be detailed, prefixed with "MUST"/"REQUIRED", with integration approach.

### Step 4: Generate Image

1. **Backup existing** `cover.png` if regenerating
2. **ALWAYS use nano-banana-pro** (OpenClaw built-in skill) for image generation:
   ```bash
   GEMINI_API_KEY="<from openclaw config>" uv run /opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
     --prompt "<prompt text>" \
     --filename "<output_path>/cover.png" \
     --resolution 2K \
     --aspect-ratio <ratio>
   ```
   - Do NOT use alternative image providers unless user explicitly requests
   - GEMINI_API_KEY is configured in `~/.openclaw/openclaw.json` under `skills.entries.nano-banana-pro.apiKey`
3. **Process references** from prompt frontmatter:
   - `direct` usage → pass via `-i` flag to nano-banana-pro
   - `style`/`palette` → extract traits, append to prompt
4. On failure: auto-retry once

### Step 5: Completion Report

```
Cover Generated!

Topic: [topic]
Type: [type] | Palette: [palette] | Rendering: [rendering]
Text: [text] | Mood: [mood] | Font: [font] | Aspect: [ratio]
Title: [title or "visual only"]
Language: [lang] | Watermark: [enabled/disabled]
References: [N images or "extracted style" or "none"]
Location: [directory path]

Files:
✓ source-{slug}.{ext}
✓ prompts/cover.md
✓ cover.png
```

## Image Modification

| Action | Steps |
|--------|-------|
| **Regenerate** | Backup → Update prompt file FIRST → Regenerate |
| **Change dimension** | Backup → Confirm new value → Update prompt → Regenerate |

## Composition Principles

- **Whitespace**: 40-60% breathing room
- **Visual anchor**: Main element centered or offset left
- **Characters**: Simplified silhouettes; NO realistic humans
- **Title**: Use exact title from user/source; never invent

## Extension Support

Custom configurations via EXTEND.md. See **Step 0** for paths.

Supports: Watermark | Preferred dimensions | Default aspect/output | Quick mode | Custom palettes | Language

Schema: [references/config/preferences-schema.md](references/config/preferences-schema.md)

## References

**Dimensions**: [text.md](references/dimensions/text.md) | [mood.md](references/dimensions/mood.md) | [font.md](references/dimensions/font.md)
**Palettes**: [references/palettes/](references/palettes/)
**Renderings**: [references/renderings/](references/renderings/)
**Types**: [references/types.md](references/types.md)
**Auto-Selection**: [references/auto-selection.md](references/auto-selection.md)
**Style Presets**: [references/style-presets.md](references/style-presets.md)
**Compatibility**: [references/compatibility.md](references/compatibility.md)
**Visual Elements**: [references/visual-elements.md](references/visual-elements.md)
**Workflow**: [confirm-options.md](references/workflow/confirm-options.md) | [prompt-template.md](references/workflow/prompt-template.md) | [reference-images.md](references/workflow/reference-images.md)
**Config**: [preferences-schema.md](references/config/preferences-schema.md) | [first-time-setup.md](references/config/first-time-setup.md) | [watermark-guide.md](references/config/watermark-guide.md)
