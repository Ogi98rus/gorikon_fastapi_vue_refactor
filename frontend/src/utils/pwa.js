// PWA утилиты для Генератора учебных материалов

class PWAManager {
  constructor() {
    this.deferredPrompt = null;
    this.isOnline = navigator.onLine;
    this.installButton = null;
    this.offlineIndicator = null;
    this.swRegistration = null;
    
    this.init();
  }

  // ============= ИНИЦИАЛИЗАЦИЯ =============
  
  init() {
    this.createPWAElements();
    this.setupEventListeners();
    this.checkOnlineStatus();
    
    // Проверяем, если приложение уже установлено
    if (this.isAppInstalled()) {
      console.log('📱 Приложение уже установлено');
    }
  }

  createPWAElements() {
    // Кнопка установки
    this.installButton = document.createElement('button');
    this.installButton.className = 'install-button';
    this.installButton.innerHTML = '📱 Установить';
    this.installButton.title = 'Установить приложение на устройство';
    document.body.appendChild(this.installButton);

    // Индикатор offline
    this.offlineIndicator = document.createElement('div');
    this.offlineIndicator.className = 'offline-indicator';
    this.offlineIndicator.innerHTML = '📡 Нет подключения к интернету';
    document.body.appendChild(this.offlineIndicator);
  }

  setupEventListeners() {
    // Событие "beforeinstallprompt"
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('📱 PWA: Доступна установка');
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Событие установки
    window.addEventListener('appinstalled', () => {
      console.log('✅ PWA: Приложение установлено');
      this.hideInstallButton();
      this.showNotification('Приложение успешно установлено!');
    });

    // Клик по кнопке установки
    this.installButton.addEventListener('click', () => {
      this.installApp();
    });

    // Статус подключения к интернету
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.hideOfflineIndicator();
      this.showNotification('Подключение восстановлено');
      console.log('🌐 Подключение к интернету восстановлено');
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.showOfflineIndicator();
      console.log('📡 Потеряно подключение к интернету');
    });

    // Обновления Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        console.log('🔄 Service Worker обновлен');
        this.showNotification('Приложение обновлено!');
      });
    }
  }

  // ============= УСТАНОВКА ПРИЛОЖЕНИЯ =============

  async installApp() {
    if (!this.deferredPrompt) {
      console.log('❌ PWA: Установка недоступна');
      return;
    }

    try {
      // Показываем диалог установки
      this.deferredPrompt.prompt();
      
      // Ждем выбора пользователя
      const { outcome } = await this.deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('✅ PWA: Пользователь согласился на установку');
      } else {
        console.log('❌ PWA: Пользователь отклонил установку');
      }
      
      this.deferredPrompt = null;
      this.hideInstallButton();
      
    } catch (error) {
      console.error('❌ PWA: Ошибка установки:', error);
    }
  }

  showInstallButton() {
    this.installButton.classList.add('show');
  }

  hideInstallButton() {
    this.installButton.classList.remove('show');
  }

  isAppInstalled() {
    // Проверяем различные способы определения установки
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true ||
      document.referrer.includes('android-app://')
    );
  }

  // ============= OFFLINE ФУНКЦИОНАЛЬНОСТЬ =============

  checkOnlineStatus() {
    if (!this.isOnline) {
      this.showOfflineIndicator();
    }
  }

  showOfflineIndicator() {
    this.offlineIndicator.classList.add('show');
  }

  hideOfflineIndicator() {
    this.offlineIndicator.classList.remove('show');
  }

  // ============= УВЕДОМЛЕНИЯ =============

  showNotification(message, type = 'info') {
    // Создаем временное уведомление
    const notification = document.createElement('div');
    notification.className = 'pwa-badge';
    notification.textContent = message;
    
    // Стили в зависимости от типа
    switch (type) {
      case 'success':
        notification.style.background = 'var(--success-color)';
        break;
      case 'error':
        notification.style.background = 'var(--error-color)';
        break;
      case 'warning':
        notification.style.background = 'var(--warning-color)';
        break;
      default:
        notification.style.background = 'var(--accent-primary)';
    }
    
    document.body.appendChild(notification);
    
    // Автоматически удаляем через 3 секунды
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 3000);
  }

  // ============= КЕШИРОВАНИЕ =============

  async cacheImportantResources() {
    if (!('caches' in window)) {
      console.log('❌ Cache API не поддерживается');
      return;
    }

    try {
      const cache = await caches.open('user-cache-v1');
      
      // Кешируем важные ресурсы
      const importantResources = [
        '/api/analytics/dashboard',
        '/static/css/main.css',
        '/static/js/main.js'
      ];
      
      await cache.addAll(importantResources);
      console.log('💾 Важные ресурсы закешированы');
      
    } catch (error) {
      console.error('❌ Ошибка кеширования:', error);
    }
  }

  async clearCache() {
    if (!('caches' in window)) return;

    try {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      );
      console.log('🗑️ Кеш очищен');
      this.showNotification('Кеш приложения очищен');
    } catch (error) {
      console.error('❌ Ошибка очистки кеша:', error);
    }
  }

  // ============= ОБНОВЛЕНИЯ =============

  async checkForUpdates() {
    if (!('serviceWorker' in navigator)) return;

    try {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration) {
        await registration.update();
        console.log('🔄 Проверка обновлений завершена');
      }
    } catch (error) {
      console.error('❌ Ошибка проверки обновлений:', error);
    }
  }

  // ============= СТАТИСТИКА =============

  getConnectionInfo() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    return {
      online: this.isOnline,
      connectionType: connection ? connection.effectiveType : 'unknown',
      downlink: connection ? connection.downlink : null,
      rtt: connection ? connection.rtt : null
    };
  }

  // ============= API ДЛЯ КОМПОНЕНТОВ =============

  async makeOfflineRequest(url, options = {}) {
    try {
      // Пытаемся сделать сетевой запрос
      if (this.isOnline) {
        const response = await fetch(url, options);
        return response;
      }
      
      // Если офлайн, пытаемся получить из кеша
      const cachedResponse = await caches.match(url);
      if (cachedResponse) {
        console.log('📄 Ответ получен из кеша:', url);
        return cachedResponse;
      }
      
      // Возвращаем mock-ответ для офлайн режима
      return new Response(
        JSON.stringify({
          error: 'Offline mode',
          message: 'Запрос недоступен в офлайн режиме'
        }),
        {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
    } catch (error) {
      console.error('❌ Ошибка запроса:', error);
      throw error;
    }
  }
}

// ============= ЭКСПОРТ И ИНИЦИАЛИЗАЦИЯ =============

// Создаем глобальный экземпляр PWA менеджера
let pwaManager = null;

export function initPWA() {
  if (!pwaManager) {
    pwaManager = new PWAManager();
    console.log('🚀 PWA Manager инициализирован');
  }
  return pwaManager;
}

export function getPWAManager() {
  return pwaManager;
}

// Автоматическая инициализация при загрузке
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    initPWA();
  });
}

export default PWAManager; 