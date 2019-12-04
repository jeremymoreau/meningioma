// Version: 0.5.3
self.addEventListener("install", function(e) {
  // waitUntil tells the browser that the install event is not finished until we have
  // cached all of our files
  e.waitUntil(
    caches.open("meningioma.app").then(cache => {
      return cache.addAll([
        "/",
        "/index.html",
        "/manifest.json",
        "/style.css",
        "/scripts.js",
        "/onsenui.min.css",
        "/onsen-css-components.min.css",
        "/onsenui.min.js",
        "/jquery.min.js",
        "/android-chrome-192x192.png",
        "/android-chrome-512x512.png",
        "/apple-touch-icon.png",
        "/favicon.ico",
        "/favicon-16x16.png",
        "/favicon-32x32.png",
        "/mstile-150x150.png",
        "/safari-pinned-tab.svg",
        "/icons/menu.svg",
        "/icons/book.svg",
        "/icons/mail.svg",
        "/icons/person.svg",
        "/icons/licence.svg",
        "/icons/smartphone.svg"
      ]);
    })
  );
});

// 2. Intercept requests and return the cached version instead
self.addEventListener("fetch", function(e) {
  e.respondWith(
    // check if this file exists in the cache
    caches
      .match(e.request)
      // Return the cached file, or else try to get it from the server
      .then(response => response || fetch(e.request))
  );
});
