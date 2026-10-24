const CACHE_NAME = 'arkhe-auth-v1';
const ASSETS = ['/app/', '/app/index.html', '/app/manifest.json', '/app/icon.svg'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('/v1/')) return;
  e.respondWith(caches.match(e.request).then((response) => response || fetch(e.request)));
});
