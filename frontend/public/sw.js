// Service Worker для Генератора учебных материалов
// Версия кеша - обновите при изменении файлов
const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `generator-cache-${CACHE_VERSION}`;

// Файлы для кеширования
const STATIC_CACHE_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
];

// Файлы API для динамического кеширования
const DYNAMIC_CACHE_PATTERNS = [
  '/api/analytics/dashboard',
  '/api/auth/check',
];

// Файлы, которые никогда не кешируются
const NEVER_CACHE_PATTERNS = [
  '/api/math/generate',
  '/api/ktp/generate',
  '/api/auth/login',
  '/api/auth/register',
];

// ============= УСТАНОВКА SERVICE WORKER =============

self.addEventListener('install', (event) => {
  console.log('📦 Service Worker: Установка...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📁 Service Worker: Кеширование основных файлов');
        // Кешируем файлы по одному, чтобы избежать ошибок
        return Promise.allSettled(
          STATIC_CACHE_FILES.map(url => 
            cache.add(url).catch(err => {
              console.warn('⚠️ Не удалось закешировать:', url, err);
              return null;
            })
          )
        );
      })
      .then(() => {
        console.log('✅ Service Worker: Установлен');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker: Ошибка установки:', error);
      })
  );
});

// ============= АКТИВАЦИЯ SERVICE WORKER =============

self.addEventListener('activate', (event) => {
  console.log('🔄 Service Worker: Активация...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        // Удаляем старые кеши
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ Service Worker: Удаление старого кеша:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker: Активирован');
        return self.clients.claim();
      })
  );
});

// ============= ПЕРЕХВАТ ЗАПРОСОВ =============

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Пропускаем не-GET запросы
  if (request.method !== 'GET') {
    return;
  }
  
  // Пропускаем файлы, которые не должны кешироваться
  if (NEVER_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern))) {
    return;
  }
  
  // Обработка запросов
  event.respondWith(
    handleRequest(request)
  );
});

// ============= ОБРАБОТКА ЗАПРОСОВ =============

async function handleRequest(request) {
  const url = new URL(request.url);
  
  try {
    // 1. Проверяем статические файлы в кеше
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      console.log('📄 Из кеша:', url.pathname);
      return cachedResponse;
    }
    
    // 2. Загружаем из сети
    const networkResponse = await fetch(request);
    
    // 3. Кешируем подходящие файлы
    if (shouldCache(request, networkResponse)) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      console.log('💾 Закешировано:', url.pathname);
    }
    
    return networkResponse;
    
  } catch (error) {
    console.log('🌐 Офлайн режим для:', url.pathname);
    
    // Возвращаем офлайн страницу для навигации
    if (request.mode === 'navigate') {
      return getOfflinePage();
    }
    
    // Возвращаем заглушку для API
    if (url.pathname.startsWith('/api/')) {
      return new Response(
        JSON.stringify({
          error: 'Нет подключения к интернету',
          offline: true
        }),
        {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    throw error;
  }
}

// ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

function shouldCache(request, response) {
  const url = new URL(request.url);
  
  // Кешируем только успешные ответы
  if (!response || response.status !== 200 || response.type !== 'basic') {
    return false;
  }
  
  // Кешируем статические ресурсы
  if (url.pathname.includes('/static/') || 
      url.pathname.includes('/icons/') ||
      url.pathname.includes('/assets/')) {
    return true;
  }
  
  // Кешируем определенные API эндпоинты
  if (DYNAMIC_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern))) {
    return true;
  }
  
  return false;
}

async function getOfflinePage() {
  try {
    // Пытаемся вернуть закешированную главную страницу
    const mainPage = await caches.match('/');
    if (mainPage) {
      return mainPage;
    }
  } catch (error) {
    console.error('Ошибка получения офлайн страницы:', error);
  }
  
  // Возвращаем базовую офлайн страницу
  return new Response(`
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Офлайн - Генератор учебных материалов</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          text-align: center;
          padding: 50px;
          background: #f5f5f5;
        }
        .offline-container {
          background: white;
          padding: 40px;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          max-width: 500px;
          margin: 0 auto;
        }
        .icon {
          font-size: 64px;
          margin-bottom: 20px;
        }
        h1 { color: #333; }
        p { color: #666; }
        button {
          background: #2196F3;
          color: white;
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          margin-top: 20px;
        }
      </style>
    </head>
    <body>
      <div class="offline-container">
        <div class="icon">📡</div>
        <h1>Нет подключения к интернету</h1>
        <p>Приложение работает в офлайн режиме. Некоторые функции могут быть недоступны.</p>
        <button onclick="window.location.reload()">Попробовать снова</button>
      </div>
    </body>
    </html>
  `, {
    headers: { 'Content-Type': 'text/html' }
  });
}

// ============= BACKGROUND SYNC (для будущего использования) =============

self.addEventListener('sync', (event) => {
  console.log('🔄 Background Sync:', event.tag);
  
  if (event.tag === 'upload-pending') {
    event.waitUntil(uploadPendingData());
  }
});

async function uploadPendingData() {
  // Логика для отправки отложенных данных
  console.log('📤 Отправка отложенных данных...');
}

// ============= PUSH NOTIFICATIONS (для будущего использования) =============

self.addEventListener('push', (event) => {
  console.log('📬 Push уведомление получено');
  
  const options = {
    body: event.data ? event.data.text() : 'Новое уведомление',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };
  
  event.waitUntil(
    self.registration.showNotification('Генератор учебных материалов', options)
  );
});

// ============= ОБРАБОТКА КЛИКОВ ПО УВЕДОМЛЕНИЯМ =============

self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Клик по уведомлению');
  
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
}); 