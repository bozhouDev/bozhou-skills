import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const CONFIG_DIR = path.join(os.homedir(), ".config", "post-to-wechat");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

export interface WechatConfig {
  app_id?: string;
  app_secret?: string;
  default_theme?: string;
  default_color?: string;
  default_publish_method?: string;
  default_author?: string;
  need_open_comment?: number;
  only_fans_can_comment?: number;
  chrome_profile_path?: string;
}

export function getConfigPath(): string {
  return CONFIG_FILE;
}

export function configExists(): boolean {
  return fs.existsSync(CONFIG_FILE);
}

export function loadWechatExtendConfig(): WechatConfig {
  if (!fs.existsSync(CONFIG_FILE)) return {};
  try {
    const content = fs.readFileSync(CONFIG_FILE, "utf-8");
    return JSON.parse(content) as WechatConfig;
  } catch {
    return {};
  }
}

export function saveConfig(config: WechatConfig): void {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2) + "\n", "utf-8");
}

export interface ResolvedAccount {
  default_publish_method?: string;
  default_author?: string;
  need_open_comment: number;
  only_fans_can_comment: number;
  chrome_profile_path?: string;
}

export function resolveAccount(config: WechatConfig, _alias?: string): ResolvedAccount {
  return {
    default_publish_method: config.default_publish_method,
    default_author: config.default_author,
    need_open_comment: config.need_open_comment ?? 1,
    only_fans_can_comment: config.only_fans_can_comment ?? 0,
    chrome_profile_path: config.chrome_profile_path,
  };
}

export function loadCredentials(_account?: ResolvedAccount): { appId: string; appSecret: string } {
  const config = loadWechatExtendConfig();
  const appId = config.app_id || "";
  const appSecret = config.app_secret || "";

  if (!appId || !appSecret) {
    throw new Error(
      `Missing app_id or app_secret in config.\n` +
      `Please edit ${CONFIG_FILE} and fill in your WeChat API credentials.`
    );
  }

  return { appId, appSecret };
}
