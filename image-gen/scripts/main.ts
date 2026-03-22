import path from "node:path";
import process from "node:process";
import { homedir } from "node:os";
import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { uploadToR2 } from "./r2";
import type { CliArgs as Args, Provider } from "./types";

function printUsage(): void {
  console.log(`Usage:
  npx -y bun scripts/main.ts --prompt "A cat" --image cat.png
  npx -y bun scripts/main.ts --promptfiles prompt.md --image out.png --ar 16:9
  npx -y bun scripts/main.ts --prompt "A cat" --image cat.png --r2

Options:
  -p, --prompt <text>       Prompt text
  --promptfiles <files...>  Read prompt from files (concatenated)
  --image <path>            Output image path (required)
  --provider google|openai|dashscope
  -m, --model <id>          Model ID
  --ar <ratio>              Aspect ratio: 16:9, 1:1, 4:3, etc.
  --size <WxH>              e.g. 1024x1024
  --quality normal|2k       Default: 2k
  --imageSize 1K|2K|4K      Google only
  --ref <files...>          Reference images
  --n <count>               Number of images
  --r2                      Upload to Cloudflare R2, print public URL
  --r2-key <name>           R2 object key (default: filename)
  --json                    JSON output
  -h, --help

Env vars (set in ~/.skills/.env):
  GOOGLE_API_KEY / GEMINI_API_KEY
  OPENAI_API_KEY
  DASHSCOPE_API_KEY
  R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ACCOUNT_ID, R2_BUCKET, R2_PUBLIC_URL`);
}

function parseArgs(argv: string[]): Args {
  const out: Args = {
    prompt: null, promptFiles: [], imagePath: null,
    provider: null, model: null, aspectRatio: null, size: null,
    quality: null, imageSize: null, referenceImages: [],
    n: 1, json: false, help: false, r2Upload: false, r2Key: null,
  };

  const takeMany = (i: number) => {
    const items: string[] = [];
    let j = i + 1;
    while (j < argv.length && !argv[j]!.startsWith("-")) items.push(argv[j++]!);
    return { items, next: j - 1 };
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    if (a === "-h" || a === "--help") { out.help = true; continue; }
    if (a === "--json") { out.json = true; continue; }
    if (a === "--r2") { out.r2Upload = true; continue; }
    if (a === "-p" || a === "--prompt") { out.prompt = argv[++i] ?? null; continue; }
    if (a === "--image") { out.imagePath = argv[++i] ?? null; continue; }
    if (a === "--model" || a === "-m") { out.model = argv[++i] ?? null; continue; }
    if (a === "--ar") { out.aspectRatio = argv[++i] ?? null; continue; }
    if (a === "--size") { out.size = argv[++i] ?? null; continue; }
    if (a === "--r2-key") { out.r2Key = argv[++i] ?? null; continue; }
    if (a === "--n") { out.n = parseInt(argv[++i] ?? "1", 10); continue; }
    if (a === "--provider") {
      const v = argv[++i] as Provider;
      if (!["google", "openai", "dashscope"].includes(v)) throw new Error(`Invalid provider: ${v}`);
      out.provider = v; continue;
    }
    if (a === "--quality") {
      const v = argv[++i];
      if (v !== "normal" && v !== "2k") throw new Error(`Invalid quality: ${v}`);
      out.quality = v; continue;
    }
    if (a === "--imageSize") {
      const v = argv[++i]?.toUpperCase() as "1K" | "2K" | "4K";
      if (!["1K", "2K", "4K"].includes(v)) throw new Error(`Invalid imageSize: ${v}`);
      out.imageSize = v; continue;
    }
    if (a === "--promptfiles") {
      const { items, next } = takeMany(i);
      out.promptFiles.push(...items); i = next; continue;
    }
    if (a === "--ref" || a === "--reference") {
      const { items, next } = takeMany(i);
      out.referenceImages.push(...items); i = next; continue;
    }
    if (!a.startsWith("-") && !out.prompt) { out.prompt = a; continue; }
  }

  return out;
}

async function loadEnv(): Promise<void> {
  const home = homedir();
  const cwd = process.cwd();
  const files = [
    path.join(home, ".skills", ".env"),
    path.join(home, ".baoyu-skills", ".env"),
    path.join(cwd, ".skills", ".env"),
    path.join(cwd, ".baoyu-skills", ".env"),
  ];
  for (const p of files) {
    try {
      const content = await readFile(p, "utf8");
      for (const line of content.split("\n")) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#")) continue;
        const idx = trimmed.indexOf("=");
        if (idx === -1) continue;
        const key = trimmed.slice(0, idx).trim();
        let val = trimmed.slice(idx + 1).trim().replace(/^["']|["']$/g, "");
        if (!process.env[key]) process.env[key] = val;
      }
    } catch { /* file missing, skip */ }
  }
}

function detectProvider(args: Args): Provider {
  if (args.provider) return args.provider;
  const hasGoogle = !!(process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY);
  const hasOpenai = !!process.env.OPENAI_API_KEY;
  const hasDashscope = !!process.env.DASHSCOPE_API_KEY;
  if (args.referenceImages.length > 0) {
    if (hasGoogle) return "google";
    if (hasOpenai) return "openai";
    throw new Error("Reference images need GOOGLE_API_KEY or OPENAI_API_KEY.");
  }
  if (hasGoogle) return "google";
  if (hasOpenai) return "openai";
  if (hasDashscope) return "dashscope";
  throw new Error("No API key found. Set GOOGLE_API_KEY, OPENAI_API_KEY, or DASHSCOPE_API_KEY in ~/.skills/.env");
}

type ProviderModule = {
  getDefaultModel: () => string;
  generateImage: (prompt: string, model: string, args: Args) => Promise<Uint8Array>;
};

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { printUsage(); return; }

  await loadEnv();

  if (!args.quality) args.quality = "2k";

  let prompt = args.prompt;
  if (!prompt && args.promptFiles.length > 0) {
    prompt = (await Promise.all(args.promptFiles.map(f => readFile(f, "utf8")))).join("\n\n");
  }
  if (!prompt && !process.stdin.isTTY) {
    try { const t = (await Bun.stdin.text()).trim(); if (t) prompt = t; } catch { /* ignore */ }
  }

  if (!prompt) { console.error("Error: prompt required"); process.exit(1); }
  if (!args.imagePath) { console.error("Error: --image required"); process.exit(1); }

  for (const ref of args.referenceImages) {
    try { await access(path.resolve(ref)); }
    catch { throw new Error(`Reference image not found: ${ref}`); }
  }

  const provider = detectProvider(args);
  const mod = await import(`./providers/${provider}`) as ProviderModule;
  const model = args.model ?? mod.getDefaultModel();
  const outputPath = path.extname(args.imagePath) ? path.resolve(args.imagePath) : path.resolve(args.imagePath) + ".png";

  let imageData: Uint8Array;
  try {
    imageData = await mod.generateImage(prompt, model, args);
  } catch (e) {
    // retry once
    console.error("Generation failed, retrying...");
    imageData = await mod.generateImage(prompt, model, args);
  }

  await mkdir(path.dirname(outputPath), { recursive: true });
  await writeFile(outputPath, imageData);

  let r2Url: string | null = null;
  if (args.r2Upload) {
    const result = await uploadToR2(outputPath, args.r2Key);
    r2Url = result.url;
  }

  if (args.json) {
    console.log(JSON.stringify({ savedImage: outputPath, r2Url, provider, model, prompt: prompt.slice(0, 200) }, null, 2));
  } else {
    console.log(r2Url ?? outputPath);
  }
}

main().catch(e => { console.error(e instanceof Error ? e.message : String(e)); process.exit(1); });
