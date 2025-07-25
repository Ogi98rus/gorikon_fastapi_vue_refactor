<template>
  <div id="app">
    <!-- Navigation Header -->
    <header class="app-header" v-if="showNavigation">
      <nav class="navbar">
        <div class="nav-container">
          <!-- Logo -->
          <div class="nav-brand">
            <router-link to="/" class="brand-link">
              <img src="./assets/logo.png" alt="Logo" class="brand-logo" />
              <span class="brand-text">EduGenerator</span>
            </router-link>
          </div>

          <!-- Mobile menu toggle -->
          <button
            class="mobile-menu-toggle"
            @click="toggleMobileMenu"
            :class="{ 'active': isMobileMenuOpen }"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <!-- Main Navigation -->
          <div class="nav-menu" :class="{ 'active': isMobileMenuOpen }">
            <div class="nav-links">
              <router-link to="/" class="nav-link" @click="closeMobileMenu">
                🏠 Главная
              </router-link>
              <router-link to="/math" class="nav-link" @click="closeMobileMenu">
                🧮 Математика
              </router-link>
              <router-link to="/ktp" class="nav-link" @click="closeMobileMenu">
                📅 КТП
              </router-link>
              <router-link
                v-if="isAuthenticated"
                to="/analytics"
                class="nav-link"
                @click="closeMobileMenu"
              >
                📊 Аналитика
              </router-link>
            </div>

            <!-- Language Selector -->
            <div class="language-selector">
              <select v-model="selectedLanguage" @change="changeLanguage">
                <option value="ru">🇷🇺 Русский</option>
                <option value="en">🇺🇸 English</option>
                <option value="kk">🇰🇿 Қазақша</option>
                <option value="be">🇧🇾 Беларуская</option>
                <option value="uk">🇺🇦 Українська</option>
              </select>
            </div>

            <!-- User Menu -->
            <div class="user-menu">
              <div v-if="isAuthenticated" class="user-dropdown">
                <button class="user-toggle" @click="toggleUserDropdown">
                  <div class="user-avatar">{{ userInitials }}</div>
                  <span class="user-name">{{ userName }}</span>
                  <span class="dropdown-arrow">▼</span>
                </button>
                
                <div class="dropdown-menu" :class="{ 'show': isUserDropdownOpen }">
                  <router-link to="/profile" class="dropdown-item" @click="closeUserDropdown">
                    👤 Профиль
                  </router-link>
                  <router-link to="/history" class="dropdown-item" @click="closeUserDropdown">
                    📊 История генераций
                  </router-link>
                  <router-link
                    v-if="isAdmin"
                    to="/analytics"
                    class="dropdown-item"
                    @click="closeUserDropdown"
                  >
          📊 Аналитика
        </router-link>
        <router-link
          v-if="isAdmin"
          to="/admin"
          class="dropdown-item"
          @click="closeUserDropdown"
        >
          👑 Панель администратора
                  </router-link>
                  <div class="dropdown-divider"></div>
                  <button @click="handleLogout" class="dropdown-item logout-btn">
                    🚪 Выйти
                  </button>
                </div>
              </div>
              
              <div v-else class="auth-buttons">
                <router-link to="/login" class="btn btn-outline" @click="closeMobileMenu">
                  🔐 Войти
                </router-link>
                <router-link to="/register" class="btn btn-primary" @click="closeMobileMenu">
                  📝 Регистрация
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="app-main" :class="{ 'with-header': showNavigation }">
      <router-view @notification="showNotification" />
    </main>

    <!-- Notification System -->
    <div class="notification-container">
      <transition-group name="notification" tag="div">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification"
          :class="`notification-${notification.type}`"
        >
          <div class="notification-content">
            <span class="notification-icon">{{ getNotificationIcon(notification.type) }}</span>
            <span class="notification-message">{{ notification.message }}</span>
          </div>
          <button
            @click="removeNotification(notification.id)"
            class="notification-close"
          >
            ✕
          </button>
        </div>
      </transition-group>
    </div>

    <!-- PWA Install Banner -->
    <div v-if="showPWAPrompt" class="pwa-banner">
      <div class="pwa-content">
        <div class="pwa-icon">📱</div>
        <div class="pwa-text">
          <h4>Установить приложение</h4>
          <p>Добавьте EduGenerator на главный экран для быстрого доступа</p>
        </div>
        <div class="pwa-actions">
          <button @click="installPWA" class="btn btn-primary">
            📥 Установить
          </button>
          <button @click="dismissPWAPrompt" class="btn btn-outline">
            ✕ Отклонить
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isGlobalLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Загрузка...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'App',
  
  data() {
    return {
      isMobileMenuOpen: false,
      isUserDropdownOpen: false,
      notifications: [],
      notificationIdCounter: 0,
      selectedLanguage: 'ru',
      
      // PWA
      showPWAPrompt: false,
      deferredPrompt: null
    }
  },

  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'user', 'isAdmin']),
    ...mapGetters(['isLoading']),

    showNavigation() {
      // Скрываем навигацию на страницах аутентификации
      const authPages = ['Login', 'Register']
      return !authPages.includes(this.$route.name)
    },

    isGlobalLoading() {
      return this.isLoading
    },

    userName() {
      return this.user?.full_name || 'Пользователь'
    },

    userInitials() {
      if (!this.user?.full_name) return '👤'
      return this.user.full_name
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase()
    }
  },

  async mounted() {
    // Инициализация аутентификации
    await this.initializeAuth()
    
    // Инициализация языка
    this.initializeLanguage()
    
    // Инициализация PWA
    this.initializePWA()
    
    // Обработка кликов вне выпадающих меню
    document.addEventListener('click', this.handleOutsideClick)
    
    // Обработка изменения размера экрана
    window.addEventListener('resize', this.handleResize)
  },

  beforeUnmount() {
    document.removeEventListener('click', this.handleOutsideClick)
    window.removeEventListener('resize', this.handleResize)
  },

  methods: {
    ...mapActions('auth', ['initAuth', 'logout']),
    ...mapActions(['setLoading']),

    async initializeAuth() {
      try {
        await this.initAuth()
      } catch (error) {
        console.log('Auth initialization failed:', error)
      }
    },

    initializeLanguage() {
      // Получаем сохраненный язык или используем язык браузера
      const savedLanguage = localStorage.getItem('selected_language')
      const browserLanguage = navigator.language.split('-')[0]
      
      this.selectedLanguage = savedLanguage || 
        (['ru', 'en', 'kk', 'be', 'uk'].includes(browserLanguage) ? browserLanguage : 'ru')
      
      this.changeLanguage()
    },

    initializePWA() {
      // Обработка события beforeinstallprompt
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault()
        this.deferredPrompt = e
        
        // Показываем баннер установки через некоторое время
        setTimeout(() => {
          if (!localStorage.getItem('pwa_dismissed')) {
            this.showPWAPrompt = true
          }
        }, 5000)
      })

      // Обработка установки PWA
      window.addEventListener('appinstalled', () => {
        this.showPWAPrompt = false
        this.showNotification({ message: 'Приложение успешно установлено!', type: 'success' })
      })
    },

    async changeLanguage() {
      try {
        // Сохраняем выбранный язык
        localStorage.setItem('selected_language', this.selectedLanguage)
        
        // Отправляем в backend для установки языка сессии
        if (this.isAuthenticated) {
          await this.$http.post('/api/i18n/set-language', {
            language: this.selectedLanguage
          })
        }
        
        // Обновляем переводы (когда будет реализована i18n система)
        this.$emit('language-changed', this.selectedLanguage)
        
      } catch (error) {
        console.error('Language change failed:', error)
      }
    },

    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },

    closeMobileMenu() {
      this.isMobileMenuOpen = false
    },

    toggleUserDropdown() {
      this.isUserDropdownOpen = !this.isUserDropdownOpen
    },

    closeUserDropdown() {
      this.isUserDropdownOpen = false
      this.closeMobileMenu()
    },

    handleOutsideClick(event) {
      // Закрываем выпадающие меню при клике вне их
      if (!event.target.closest('.user-dropdown')) {
        this.isUserDropdownOpen = false
      }
      if (!event.target.closest('.nav-menu') && !event.target.closest('.mobile-menu-toggle')) {
        this.isMobileMenuOpen = false
      }
    },

    handleResize() {
      // Закрываем мобильное меню при изменении размера экрана
      if (window.innerWidth > 768) {
        this.isMobileMenuOpen = false
      }
    },

    async handleLogout() {
      try {
        await this.logout()
        this.$router.push('/')
        this.closeUserDropdown()
        this.showNotification({ message: 'Вы успешно вышли из системы', type: 'info' })
      } catch (error) {
        console.error('Logout error:', error)
        this.showNotification({ message: 'Ошибка при выходе из системы', type: 'error' })
      }
    },

    async installPWA() {
      if (this.deferredPrompt) {
        this.deferredPrompt.prompt()
        const { outcome } = await this.deferredPrompt.userChoice
        
        if (outcome === 'accepted') {
          this.showPWAPrompt = false
        }
        
        this.deferredPrompt = null
      }
    },

    dismissPWAPrompt() {
      this.showPWAPrompt = false
      localStorage.setItem('pwa_dismissed', 'true')
    },

    showNotification(notification) {
      const id = ++this.notificationIdCounter
      const notificationObj = {
        id,
        message: notification.message,
        type: notification.type || 'info'
      }
      
      this.notifications.push(notificationObj)
      
      // Автоматически удаляем уведомление через 5 секунд
      setTimeout(() => {
        this.removeNotification(id)
      }, 5000)
    },

    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    getNotificationIcon(type) {
      const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
      }
      return icons[type] || icons.info
    }
  }
}
</script>

<style>
@import './assets/style.css';

/* App Layout */
#app {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* Header Navigation */
.app-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.navbar {
  padding: 0 20px;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 0;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--text-primary);
  font-weight: bold;
  font-size: 18px;
}

.brand-logo {
  height: 32px;
  margin-right: 10px;
}

.brand-text {
  color: var(--accent-primary);
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 30px;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link:hover {
  color: var(--accent-primary);
  background: var(--hover-bg);
}

.nav-link.router-link-active {
  color: var(--accent-primary);
  background: var(--accent-light);
}

/* Language Selector */
.language-selector select {
  background: var(--input-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 8px;
  color: var(--text-primary);
  font-size: 14px;
}

/* User Menu */
.user-dropdown {
  position: relative;
}

.user-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.3s ease;
}

.user-toggle:hover {
  background: var(--hover-bg);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.user-name {
  color: var(--text-primary);
  font-weight: 500;
}

.dropdown-arrow {
  color: var(--text-secondary);
  font-size: 10px;
  transition: transform 0.3s ease;
}

.user-dropdown.active .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 1001;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s ease;
}

.dropdown-item:hover {
  background: var(--hover-bg);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 8px 0;
}

.logout-btn {
  color: var(--error-color) !important;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

/* Mobile Menu */
.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  gap: 4px;
}

.mobile-menu-toggle span {
  width: 25px;
  height: 3px;
  background: var(--text-primary);
  transition: all 0.3s ease;
  border-radius: 2px;
}

.mobile-menu-toggle.active span:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.mobile-menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.mobile-menu-toggle.active span:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* Main Content */
.app-main {
  min-height: calc(100vh - 80px);
}

.app-main.with-header {
  min-height: calc(100vh - 80px);
}

/* Notifications */
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  max-width: 400px;
}

.notification {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 100%;
}

.notification-success {
  border-left: 4px solid #4caf50;
}

.notification-error {
  border-left: 4px solid #f44336;
}

.notification-warning {
  border-left: 4px solid #ff9800;
}

.notification-info {
  border-left: 4px solid #2196f3;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notification-icon {
  font-size: 18px;
}

.notification-message {
  color: var(--text-primary);
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.notification-close:hover {
  background: var(--hover-bg);
}

/* Notification Animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.5s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* PWA Banner */
.pwa-banner {
  position: fixed;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  z-index: 1500;
  max-width: 500px;
  margin: 0 auto;
}

.pwa-content {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
}

.pwa-icon {
  font-size: 32px;
}

.pwa-text {
  flex: 1;
}

.pwa-text h4 {
  margin: 0 0 5px 0;
  color: var(--text-primary);
}

.pwa-text p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.pwa-actions {
  display: flex;
  gap: 10px;
  flex-direction: column;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  backdrop-filter: blur(5px);
}

.loading-spinner {
  text-align: center;
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-top: 5px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.btn-outline {
  background: transparent;
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

.btn-outline:hover {
  background: var(--accent-primary);
  color: white;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: flex;
  }
  
  .nav-menu {
    position: fixed;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    flex-direction: column;
    gap: 0;
    padding: 20px;
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
  }
  
  .nav-menu.active {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }
  
  .nav-links {
    flex-direction: column;
    gap: 10px;
    width: 100%;
    margin-bottom: 20px;
  }
  
  .nav-link {
    width: 100%;
    text-align: center;
    padding: 12px;
  }
  
  .language-selector {
    margin-bottom: 20px;
  }
  
  .user-menu {
    width: 100%;
  }
  
  .auth-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .user-dropdown {
    width: 100%;
  }
  
  .user-toggle {
    width: 100%;
    justify-content: center;
  }
  
  .dropdown-menu {
    position: static;
    box-shadow: none;
    border: none;
    background: transparent;
    opacity: 1;
    visibility: visible;
    transform: none;
    margin-top: 10px;
  }
  
  .notification-container {
    left: 10px;
    right: 10px;
    max-width: none;
  }
  
  .pwa-banner {
    left: 10px;
    right: 10px;
  }
  
  .pwa-content {
    flex-direction: column;
    text-align: center;
  }
  
  .pwa-actions {
    flex-direction: row;
    justify-content: center;
  }
}
</style>
