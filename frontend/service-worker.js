const CACHE_NAME = 'seufuturo-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/privacy.html',
  '/terms.html',
  '/icons/icon-192.svg',
  '/icons/icon-512.svg',
  '/icons/splash.svg',
  '/icons/screenshot-narrow.svg'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch(() => {
        console.log('Some assets failed to cache');
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET and cross-origin requests
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) {
    return;
  }

  // API responses can contain account-specific data, so keep them network-only.
  if (request.url.includes('/api/')) {
    event.respondWith(fetch(request));
    return;
  }

  // For other requests, cache first, then network
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }

      return fetch(request)
        .then((response) => {
          // Cache successful responses
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }

          const clonedResponse = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clonedResponse);
          });

          return response;
        })
        .catch(() => {
          // Return a custom offline page if needed
          if (request.destination === 'document') {
            return caches.match('/index.html');
          }
        });
    })
  );
});

// Handle messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Background sync for notifications (optional)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-horoscope') {
    event.waitUntil(
      fetch('/api/horoscopo')
        .then(() => {
          // Show notification
          self.registration.showNotification('SeuFuturo atualizado! 🌙', {
            badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><text x="48" y="70" font-size="60" text-anchor="middle" fill="%23ff1493" font-family="serif">🌙</text></svg>',
            icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%231a0e2e" width="192" height="192"/><text x="96" y="140" font-size="130" text-anchor="middle" fill="%23ff1493" font-family="serif" font-weight="bold">🌙</text></svg>',
            tag: 'horoscope-notification',
            requireInteraction: false
          });
        })
        .catch(() => {
          console.error('Background sync failed');
        })
    );
  }
});

// Push notification handler
self.addEventListener('push', (event) => {
  const options = {
    badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><text x="48" y="70" font-size="60" text-anchor="middle" fill="%23ff1493" font-family="serif">🌙</text></svg>',
    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%231a0e2e" width="192" height="192"/><text x="96" y="140" font-size="130" text-anchor="middle" fill="%23ff1493" font-family="serif" font-weight="bold">🌙</text></svg>',
    body: event.data ? event.data.text() : 'Nova previsão disponível!',
    tag: 'horoscope-push',
    requireInteraction: false
  };

  event.waitUntil(
    self.registration.showNotification('SeuFuturo', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Check if app is already open
      for (const client of clientList) {
        if (client.url === '/' && 'focus' in client) {
          return client.focus();
        }
      }
      // If not open, open it
      if (clients.openWindow) {
        return clients.openWindow('/');
      }
    })
  );
});
