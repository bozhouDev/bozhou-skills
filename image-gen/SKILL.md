---
name: image-gen
description: AI image generation with OpenAI, Google and DashScope APIs. Supports text-to-image, reference images, aspect ratios, and direct Cloudflare R2 upload. Sequential by default; parallel generation available on request. Use when user asks to generate, create, or draw images.
---

# Image Generation

Generate images via OpenAI, Google Gemini, or DashScope APIs. Optional R2 upload.

## Scripts

```
SKILL_DIR/
  scripts/main.ts        — generate image (+ optional R2 upload)
  scripts/upload-r2.ts   — upload any existing file to R2
  scripts/r2.ts          — R2 upload module (AWS SigV4, no external deps)
  scripts/providers/     — google.ts / openai.ts / dashscope.ts
  scripts/types.ts       — shared types
```

## Usage

```bash
SKILL_DIR="/path/to/image-gen"

# Basic generation
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "A cat" --image cat.png

# With aspect ratio
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "A landscape" --image out.png --ar 16:9

# From prompt file
npx -y bun ${SKILL_DIR}/scripts/main.ts --promptfiles prompt.md --image out.png

# Generate + upload to R2 (prints public URL)
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "A cat" --image cat.png --r2

# Generate + upload with custom R2 key
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "A cat" --image cat.png --r2 --r2-key articles/hero.png

# Upload existing file to R2
npx -y bun ${SKILL_DIR}/scripts/upload-r2.ts --file image.png
npx -y bun ${SKILL_DIR}/scripts/upload-r2.ts --file image.png --key custom/path.png

# With reference image
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "Make it blue" --image out.png --ref source.png

# Force provider
npx -y bun ${SKILL_DIR}/scripts/main.ts --prompt "A cat" --image out.png --provider openai
```

## Options

| Option | Description |
|--------|-------------|
| `-p, --prompt <text>` | Prompt text |
| `--promptfiles <files...>` | Read prompt from files |
| `--image <path>` | Output path (required) |
| `--provider google\|openai\|dashscope` | Force provider |
| `-m, --model <id>` | Model ID |
| `--ar <ratio>` | Aspect ratio: `16:9`, `1:1`, `4:3`, `9:16`, `2.35:1` |
| `--quality normal\|2k` | Default: `2k` |
| `--imageSize 1K\|2K\|4K` | Google only |
| `--ref <files...>` | Reference images |
| `--r2` | Upload to R2 after generation, print public URL |
| `--r2-key <name>` | R2 object key (default: filename) |
| `--json` | JSON output |

## Environment Variables

Set in `~/.skills/.env` or `~/.baoyu-skills/.env`:

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` / `GEMINI_API_KEY` | Google API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `DASHSCOPE_API_KEY` | DashScope API key |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 access key |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 secret key |
| `R2_ACCOUNT_ID` | Cloudflare account ID |
| `R2_BUCKET` | R2 bucket name |
| `R2_PUBLIC_URL` | Public base URL (e.g. `https://cdn.example.com`) |

## Provider Selection

Auto-detects from available API keys. Priority: Google → OpenAI → DashScope.
With `--ref`: Google first (Gemini multimodal), then OpenAI.

## R2 Upload

Uses AWS SigV4 signing with built-in Node.js crypto — no external dependencies.
With `--r2`, prints R2 public URL instead of local path.

## Generation Mode

Sequential by default. For parallel batch generation, use multiple background subagents.
