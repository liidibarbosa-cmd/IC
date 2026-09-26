// Imprime caderno.html em PDF A3 (sem ajuste de escala) e gera PNGs de revisão.
import { chromium } from 'playwright';
import path from 'path';
const aqui = path.dirname(new URL(import.meta.url).pathname);
const saida = process.argv[2] || path.join(aqui, '..');
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1123, height: 1587 }, deviceScaleFactor: Number(process.env.ESCALA_PREVIA || 2) });
const html = process.env.HTML || 'caderno.html';
const pdf = process.env.PDF || 'CADERNO DE DETALHAMENTO DE REVESTIMENTO DE PISO 01-02 - R00.pdf';
const prev = process.env.PREVIA || 'folha';
await page.goto('file://' + path.join(aqui, html));
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: path.join(saida, pdf),
  width: '297mm', height: '420mm', printBackground: true, preferCSSPageSize: true });
const n = await page.locator('section.sheet').count();
for (let i = 0; i < n; i++) {
  await page.locator('section.sheet').nth(i).screenshot({ path: path.join(aqui, 'previa', `${prev}_${String(i + 1).padStart(2, '0')}.png`), scale: 'device' });
}
await browser.close();
console.log('ok', n);
