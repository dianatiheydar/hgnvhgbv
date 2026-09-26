const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/booklet.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const foot = `<div style="width:100%;font-family:'Vazirmatn FD';font-size:8.5pt;color:#6b7486;direction:rtl;padding:0 14mm;display:flex;justify-content:space-between;align-items:center">
    <span>جزوهٔ علوم تجربی ششم دبستان &nbsp;|&nbsp; دیانتی ۰۹۱۶۵۱۶۲۱۶۶</span>
    <span style="background:#1e4d8c;color:#fff;border-radius:3px;padding:0 7px;font-weight:700">صفحهٔ <span class="pageNumber"></span></span></div>`;
  await p.pdf({ path: process.argv[2] || 'out.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: false });
  await b.close();
})();
