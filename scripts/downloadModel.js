#!/usr/bin/env node
// Simple helper that downloads a model/archive from a given URL and saves it
// into the workspace under `models/` (creating the directory if necessary).
//
// Usage:
//   node scripts/downloadModel.js <url> [<output-name>]
//
// Example:
//   node scripts/downloadModel.js https://huggingface.co/gpt2/resolve/main/pytorch_model.bin gpt2.bin
//
// This can be used for any "free" downloadable model you find on the web, e.g.
// a small LLM checkpoint from Smailing (or any other vendor). The script is
// purposely minimal; it merely fetches the bytes and writes them to disk.

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

if (process.argv.length < 3) {
  console.error('Usage: node scripts/downloadModel.js <url> [<output-filename>]');
  process.exit(1);
}

const url = process.argv[2];
let filename = process.argv[3] || path.basename(url);
const outDir = path.resolve(__dirname, '../models');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}
const outPath = path.join(outDir, filename);

console.log(`Downloading model from ${url} to ${outPath}`);

const client = url.startsWith('https') ? https : http;
client.get(url, res => {
  if (res.statusCode !== 200) {
    console.error(`Failed to download: HTTP ${res.statusCode}`);
    process.exit(1);
  }

  const fileStream = fs.createWriteStream(outPath);
  res.pipe(fileStream);
  fileStream.on('finish', () => {
    fileStream.close();
    console.log('Download complete.');
  });
}).on('error', err => {
  console.error('Error downloading model:', err.message);
  process.exit(1);
});
