import { createHmac, createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";

function sha256Hex(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

async function hmacSha256(key: Buffer | string, data: string): Promise<Buffer> {
  return createHmac("sha256", key).update(data).digest();
}

function getContentType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const map: Record<string, string> = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
  };
  return map[ext] ?? "application/octet-stream";
}

export type R2UploadResult = {
  url: string;
  key: string;
  bucket: string;
};

export async function uploadToR2(filePath: string, keyOverride?: string | null): Promise<R2UploadResult> {
  const accessKeyId = process.env.R2_ACCESS_KEY_ID;
  const secretAccessKey = process.env.R2_SECRET_ACCESS_KEY;
  const accountId = process.env.R2_ACCOUNT_ID;
  const bucket = process.env.R2_BUCKET;
  const publicUrl = process.env.R2_PUBLIC_URL;

  if (!accessKeyId || !secretAccessKey || !accountId || !bucket) {
    throw new Error(
      "R2 credentials not configured. Set R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, " +
      "R2_ACCOUNT_ID, R2_BUCKET in ~/.skills/.env or environment variables."
    );
  }

  const objectKey = keyOverride || path.basename(filePath);
  const fileData = await readFile(filePath);
  const contentType = getContentType(filePath);

  const host = `${accountId}.r2.cloudflarestorage.com`;
  const endpoint = `https://${host}`;
  const region = "auto";
  const service = "s3";

  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "").slice(0, 15) + "Z";
  const dateStamp = amzDate.slice(0, 8);

  const payloadHash = sha256Hex(fileData);

  // Canonical request
  const canonicalUri = `/${bucket}/${objectKey}`;
  const canonicalHeaders =
    `content-type:${contentType}\n` +
    `host:${host}\n` +
    `x-amz-content-sha256:${payloadHash}\n` +
    `x-amz-date:${amzDate}\n`;
  const signedHeaders = "content-type;host;x-amz-content-sha256;x-amz-date";

  const canonicalRequest = [
    "PUT",
    canonicalUri,
    "",
    canonicalHeaders,
    signedHeaders,
    payloadHash,
  ].join("\n");

  // String to sign
  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign = [
    "AWS4-HMAC-SHA256",
    amzDate,
    credentialScope,
    sha256Hex(canonicalRequest),
  ].join("\n");

  // Signing key
  const kDate = await hmacSha256(Buffer.from(`AWS4${secretAccessKey}`), dateStamp);
  const kRegion = await hmacSha256(kDate, region);
  const kService = await hmacSha256(kRegion, service);
  const kSigning = await hmacSha256(kService, "aws4_request");
  const signature = (await hmacSha256(kSigning, stringToSign)).toString("hex");

  const authorization =
    `AWS4-HMAC-SHA256 Credential=${accessKeyId}/${credentialScope}, ` +
    `SignedHeaders=${signedHeaders}, Signature=${signature}`;

  const response = await fetch(`${endpoint}/${bucket}/${objectKey}`, {
    method: "PUT",
    headers: {
      "Content-Type": contentType,
      "x-amz-date": amzDate,
      "x-amz-content-sha256": payloadHash,
      Authorization: authorization,
    },
    body: fileData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`R2 upload failed: ${response.status} ${response.statusText}\n${text}`);
  }

  const base = publicUrl ? publicUrl.replace(/\/$/, "") : `${endpoint}/${bucket}`;
  return { url: `${base}/${objectKey}`, key: objectKey, bucket };
}
