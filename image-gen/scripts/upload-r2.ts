/**
 * Standalone R2 upload script
 *
 * Usage:
 *   npx -y bun upload-r2.ts --file image.png
 *   npx -y bun upload-r2.ts --file image.png --key custom-name.png
 *   npx -y bun upload-r2.ts --file image.png --json
 *
 * Env vars (or ~/.skills/.env):
 *   R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ACCOUNT_ID, R2_BUCKET, R2_PUBLIC_URL
 */

import path from "node:path";
import process from "node:process";
import { homedir } from "node:os";
import { readFile } from "node:fs/promises";
import { uploadToR2 } from "./r2";

async function loadEnvFile(p: string): Promise<void> {
  try {
    const content = await readFile(p, "utf8");
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const idx = trimmed.indexOf("=");
      if (idx === -1) continue;
      const key = trimmed.slice(0, idx).trim();
      let val = trimmed.slice(idx + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      if (!process.env[key]) process.env[key] = val;
    }
  } catch {
    // ignore missing files
  }
}

async function loadEnv(): Promise<void> {
  const home = homedir();
  const cwd = process.cwd();
  // Load in order: home generic, home baoyu-compat, cwd generic, cwd baoyu-compat
  await loadEnvFile(path.join(home, ".skills", ".env"));
  await loadEnvFile(path.join(home, ".baoyu-skills", ".env"));
  await loadEnvFile(path.join(cwd, ".skills", ".env"));
  await loadEnvFile(path.join(cwd, ".baoyu-skills", ".env"));
}

function printUsage(): void {
  console.log(`Upload a file to Cloudflare R2

Usage:
  npx -y bun upload-r2.ts --file <path> [options]

Options:
  --file <path>    File to upload (required)
  --key <name>     Object key in R2 (default: filename)
  --json           Output JSON with url, key, bucket
  -h, --help       Show help

Environment variables (set in ~/.skills/.env):
  R2_ACCESS_KEY_ID      R2 access key
  R2_SECRET_ACCESS_KEY  R2 secret key
  R2_ACCOUNT_ID         Cloudflare account ID
  R2_BUCKET             Bucket name
  R2_PUBLIC_URL         Public base URL (e.g. https://cdn.example.com)`);
}

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  let filePath: string | null = null;
  let key: string | null = null;
  let json = false;

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    if (a === "-h" || a === "--help") { printUsage(); return; }
    if (a === "--json") { json = true; continue; }
    if (a === "--file") { filePath = argv[++i] ?? null; continue; }
    if (a === "--key") { key = argv[++i] ?? null; continue; }
    if (!a.startsWith("-") && !filePath) { filePath = a; continue; }
  }

  if (!filePath) {
    console.error("Error: --file is required");
    printUsage();
    process.exit(1);
  }

  await loadEnv();

  const result = await uploadToR2(filePath, key);

  if (json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(result.url);
  }
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exit(1);
});
