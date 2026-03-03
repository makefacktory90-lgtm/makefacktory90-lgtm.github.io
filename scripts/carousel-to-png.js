#!/usr/bin/env node
/**
 * Carousel to PNG exporter
 * Usage: node scripts/carousel-to-png.js carousel/seedance-hollywood-lite.html
 * Output: carousel/export/seedance-hollywood-lite/slide-01.png, slide-02.png, ...
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Usage: node carousel-to-png.js <file.html>');
  process.exit(1);
}

const absPath = path.resolve(inputFile);
const baseName = path.basename(inputFile, '.html');
const exportDir = path.join(path.dirname(absPath), 'export', baseName);

fs.mkdirSync(exportDir, { recursive: true });

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Load with enough viewport for full-size slides
  await page.setViewport({ width: 1200, height: 1600 });
  await page.goto(`file://${absPath}`, { waitUntil: 'networkidle2', timeout: 30000 });

  // Wait for fonts to load
  await page.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, 2000));

  // Get all slides
  const slides = await page.$$('.slide');
  console.log(`Found ${slides.length} slides`);

  for (let i = 0; i < slides.length; i++) {
    const num = String(i + 1).padStart(2, '0');
    const outFile = path.join(exportDir, `slide-${num}.png`);

    // Screenshot each slide at its native 1080x1350
    await slides[i].screenshot({
      path: outFile,
      type: 'png',
      clip: await slides[i].boundingBox().then(box => ({
        x: box.x,
        y: box.y,
        width: 1080,
        height: 1350,
      })),
    });

    console.log(`  ✅ ${outFile}`);
  }

  await browser.close();
  console.log(`\nExported ${slides.length} slides to ${exportDir}/`);
})();
