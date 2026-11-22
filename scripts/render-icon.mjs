// Render the plugin's listing icon from its source drawing.
//
//   node scripts/render-icon.mjs            (after: bash skills/sei-diagrams/scripts/setup.sh)
//
// Reads .claude-plugin/icon-source.svg and writes .claude-plugin/icon.png at 1024 x 1024, with
// the Chromium the Mermaid renderer already installs. The plugin directory accepts a square PNG
// of 512 to 2048 px under 2 MB, and takes it once, when the plugin is first submitted.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(resolve(root, 'skills/sei-diagrams/package.json'));
const puppeteer = (await import(require.resolve('puppeteer'))).default;
const size = 1024;
const svg = readFileSync(resolve(root, '.claude-plugin/icon-source.svg'), 'utf8');

const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: size, height: size, deviceScaleFactor: 1 });
await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
await page.screenshot({ path: resolve(root, '.claude-plugin/icon.png'), clip: { x: 0, y: 0, width: size, height: size } });
await browser.close();
console.log('wrote .claude-plugin/icon.png');
