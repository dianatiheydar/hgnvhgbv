# نیازمندی‌ها: python3 + pymupdf، node + playwright، فونت وزیرمتن نصب‌شده روی سیستم
cd "$(dirname "$0")"
set -e
echo '{}' > toc.json
python3 build.py >/dev/null && node pdf.js pass1.pdf
python3 -c "
import pymupdf,json
d=pymupdf.open('pass1.pdf')
toc={}
for i,p in enumerate(d):
    for k in range(1,15):
        if p.search_for('@@L%02d@@'%k): toc['L%02d'%k]=i+1
assert len(toc)==14, toc
json.dump(toc,open('toc.json','w')); print(d.page_count, toc)
"
python3 build.py toc && sed -i 's|<span class="mark">@@L[0-9]*@@</span>||' booklet.html && node pdf.js final.pdf
python3 -c "
import pymupdf
d=pymupdf.open('final.pdf')
d.set_metadata({'title':'جزوهٔ علوم تجربی ششم دبستان','author':'دیانتی','creator':'دیانتی','producer':'','creationDate':'','modDate':''})
d.save('../جزوه-علوم-تجربی-ششم-دیانتی.pdf',garbage=3,deflate=True); print('pages',d.page_count)
"
rm -f pass1.pdf final.pdf booklet.html toc.json
