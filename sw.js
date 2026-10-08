// وایت‌برد — کار بدون اینترنت وقتی از آیکونِ صفحه‌ی اصلی باز می‌شود
// صفحه: اول از اینترنت (تا نسخه‌ی تازه برسد)، اگر نبود از حافظه؛ آیکون‌ها و فهرست: از حافظه
const CACHE = 'whiteboard-v1';
const FILES = ['./whiteboard.html', './manifest.webmanifest', './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-512-maskable.png', './icons/favicon-32.png'];

self.addEventListener('install', e=>{
  e.waitUntil(caches.open(CACHE).then(c=> c.addAll(FILES)).then(()=> self.skipWaiting()));
});
self.addEventListener('activate', e=>{
  e.waitUntil(caches.keys().then(keys=> Promise.all(keys.filter(k=> k.startsWith('whiteboard-') && k !== CACHE).map(k=> caches.delete(k)))).then(()=> self.clients.claim()));
});
self.addEventListener('fetch', e=>{
  const req = e.request, url = new URL(req.url);
  if(req.method !== 'GET' || url.origin !== self.location.origin) return;
  const page = req.mode === 'navigate' || url.pathname.endsWith('.html');
  if(page){
    e.respondWith(fetch(req).then(res=>{
      if(res && res.ok){ const copy = res.clone(); caches.open(CACHE).then(c=> c.put('./whiteboard.html', copy)); }
      return res;
    }).catch(()=> caches.match('./whiteboard.html')));
    return;
  }
  e.respondWith(caches.match(req).then(hit=> hit || fetch(req)));
});
