// Imprime orcamento.html em PDF A4 paisagem com rodapé e numeração.
import { chromium } from 'playwright';
import path from 'path';
const aqui = path.dirname(new URL(import.meta.url).pathname);
const pdf = process.env.PDF || 'LISTA TECNICA PARA ORCAMENTO - BANDINI - R00.pdf';
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.goto('file://' + path.join(aqui, 'orcamento.html'));
await page.evaluate(() => document.fonts.ready);
const st = 'font-family:Helvetica,Arial,sans-serif;font-size:6.5pt;color:#4f5439;width:100%;margin:0 12mm;display:flex;justify-content:space-between;border-top:0.25mm solid #d8cfbc;padding-top:1.5mm';
await page.pdf({ path: path.join(aqui, '..', pdf), printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate: `<div style="${st}"><span><b>DUAS</b> design &amp; arq · Lidiane Barbosa e Isadora Ferrari</span><span>Residência IC — Lista técnica para orçamento (Bandini) · 26/09/2026 · Rev. 00 · Folha <span class="pageNumber"></span>/<span class="totalPages"></span></span></div>` });
await browser.close();
console.log('ok');
