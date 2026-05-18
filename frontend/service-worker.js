const CACHE_NAME = 'seufuturo-v3';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/privacy.html',
  '/terms.html',
  '/icons/apple-touch-icon.png',
  '/icons/badge-96.png',
  '/icons/favicon-16.png',
  '/icons/favicon-32.png',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-1024.png',
  '/icons/maskable-192.png',
  '/icons/maskable-512.png',
  '/icons/splash-1280x720.png',
  '/icons/screenshot-narrow.png'
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
          self.registration.showNotification('SeuFuturo atualizado!', {
            badge: '/icons/badge-96.png',
            icon: '/icons/icon-192.png',
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
    badge: '/icons/badge-96.png',
    icon: '/icons/icon-192.png',
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
