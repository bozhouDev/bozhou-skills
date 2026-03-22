export type Provider = "google" | "openai" | "dashscope";

export type CliArgs = {
  prompt: string | null;
  promptFiles: string[];
  imagePath: string | null;
  provider: Provider | null;
  model: string | null;
  aspectRatio: string | null;
  size: string | null;
  quality: "normal" | "2k" | null;
  imageSize: "1K" | "2K" | "4K" | null;
  referenceImages: string[];
  n: number;
  json: boolean;
  help: boolean;
  r2Upload: boolean;
  r2Key: string | null;
};
