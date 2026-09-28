// Renders SVG files to PNG with headless Chromium. Usage: node render.js jobs.json
// Needs: npm i playwright-core, and a chromium binary (PLAYWRIGHT_BROWSERS_PATH or CHROMIUM_PATH).
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.readdirSync(base)) {
    for (const rel of ['chrome-linux/chrome', 'chrome-linux64/chrome', 'chrome-headless-shell-linux64/chrome-headless-shell']) {
      const p = path.join(base, d, rel);
      if (fs.existsSync(p)) return p;
    }
  }
  return undefined;
}

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch({ executablePath: findChromium(), args: ['--no-sandbox'] });
  const page = await browser.newPage();
  for (const j of jobs) {
    await page.setViewportSize({ width: j.w, height: j.h });
    const svg = fs.readFileSync(j.svg, 'utf8');
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.screenshot({ path: j.png, omitBackground: j.transparent, clip: { x: 0, y: 0, width: j.w, height: j.h } });
  }
  await browser.close();
})();
