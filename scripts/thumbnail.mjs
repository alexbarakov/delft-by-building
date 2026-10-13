/*
  A 1920×1080 cover image for the promo video, into out-video/amsterdam-thumbnail.jpg.
    cd ../stop-token && node ../amsterdam-by-building/scripts/thumbnail.mjs [http://localhost:8642]
*/
import { createRequire } from "node:module";
import { resolve } from "node:path";
const require = createRequire(resolve("package.json"));
const { chromium } = require("playwright");

const base = process.argv[2] || "http://localhost:8642";
const browser = await chromium.launch({ args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"] });
const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })).newPage();
await page.goto(`${base}/?lang=en`);
await page.evaluate(() => document.fonts.ready);
await page.waitForFunction(() => document.getElementById("loading").hidden, null, { timeout: 60000 });
await page.evaluate(() => {
  const d = window.__dbg;
  d.controls.target.set(150, 0, 350);
  d.camera.position.set(150 + 2300, 2600, 350 + 2900);
  d.controls.update();
  for (const s of ["#panel", ".modes", ".howto", ".lang", ".timeline", ".tally", ".dek"]) document.querySelector(s).style.display = "none";
  const cap = document.createElement("div");
  cap.innerHTML = `<div style="font-size:84px;font-weight:800;letter-spacing:-0.035em;line-height:.95">Every building<br>in Amsterdam,<br>by age and history</div>
    <div style="margin-top:22px;font-size:30px;font-weight:500;color:#3e4448">192,000 buildings · seven centuries · context layers</div>`;
  cap.style.cssText = "position:fixed;left:64px;bottom:72px;font-family:'Schibsted Grotesk',sans-serif;color:#000;" +
    "background:rgba(228,232,234,.88);padding:30px 38px 34px;border-radius:14px;max-width:880px";
  document.body.appendChild(cap);
});
await page.waitForTimeout(2500);
await page.screenshot({ path: resolve("out-video/amsterdam-thumbnail.jpg"), type: "jpeg", quality: 92 });
await browser.close();
console.log("out-video/amsterdam-thumbnail.jpg");
