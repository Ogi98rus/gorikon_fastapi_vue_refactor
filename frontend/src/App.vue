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
              <span class="brand-text">GORIKON</span>
            </router-link>
          </div>

          <!-- Theme Toggle Button -->
          <button
            class="theme-toggle-btn"
            @click="toggleTheme"
            :title="$t('common.toggleTheme')"
          >
            <span v-if="isDark">☀️</span>
            <span v-else>🌙</span>
          </button>

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
                🏠 {{ $t('nav.home') }}
              </router-link>
              <router-link to="/math" class="nav-link" @click="closeMobileMenu">
                🧮 {{ $t('nav.math') }}
              </router-link>
              <router-link to="/ktp" class="nav-link" @click="closeMobileMenu">
                📅 {{ $t('nav.ktp') }}
              </router-link>
            </div>

            <!-- Language Selector -->
            <div class="language-selector">
              <select v-model="selectedLanguage" @change="changeLanguage">
                <option value="ru">🇷🇺 {{ $t('common.russian') }}</option>
                <option value="en">🇺🇸 {{ $t('common.english') }}</option>
              </select>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="app-main" :class="{ 'with-header': showNavigation }">
      <router-view />
    </main>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'

export default {
  name: 'App',
  
  data() {
    return {
      isMobileMenuOpen: false,
      selectedLanguage: 'ru',
      isDark: false
    }
  },

  computed: {
    showNavigation() {
      return true
    },
    
    ...mapState('i18n', ['currentLanguage'])
  },

  watch: {
    currentLanguage(newLang) {
      this.selectedLanguage = newLang
    }
  },

  mounted() {
    // Инициализация языка
    this.initializeLanguage()
    
    // Загружаем тему
    this.loadTheme()
    
    // Обработка изменения размера экрана
    window.addEventListener('resize', this.handleResize)
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },

  methods: {
    ...mapActions('i18n', ['setLanguage']),
    

    
    async initializeLanguage() {
      try {
        // Получаем сохраненный язык или используем язык браузера
        const savedLanguage = localStorage.getItem('selected_language')
        const browserLanguage = navigator.language.split('-')[0]
        
        const language = savedLanguage || 
          (['ru', 'en', 'kk', 'be', 'uk'].includes(browserLanguage) ? browserLanguage : 'ru')
        
        // Устанавливаем язык через store
        await this.setLanguage(language)
        this.selectedLanguage = language
      } catch (error) {
        console.error('Failed to initialize language:', error)
        // Fallback на русский язык
        this.selectedLanguage = 'ru'
      }
    },

    async changeLanguage() {
      try {
        // Устанавливаем язык через store
        await this.setLanguage(this.selectedLanguage)
      } catch (error) {
        console.error('Failed to change language:', error)
      }
    },

    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },

    closeMobileMenu() {
      this.isMobileMenuOpen = false
    },
    
    toggleTheme() {
      this.isDark = !this.isDark
      this.applyTheme()
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light')
    },
    
    loadTheme() {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        this.isDark = savedTheme === 'dark'
      } else {
        this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      this.applyTheme()
    },
    
    applyTheme() {
      if (this.isDark) {
        document.documentElement.setAttribute('data-theme', 'dark')
        console.log('🌙 Тема изменена на темную')
      } else {
        document.documentElement.removeAttribute('data-theme')
        console.log('☀️ Тема изменена на светлую')
      }
    },

    handleResize() {
      // Закрываем мобильное меню при изменении размера экрана
      if (window.innerWidth > 768) {
        this.isMobileMenuOpen = false
      }
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

/* Theme Toggle Button */
.theme-toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  font-size: 18px;
  transition: all 0.3s ease;
  margin-right: 15px;
}

.theme-toggle-btn:hover {
  background: var(--hover-bg);
  transform: scale(1.1);
}

.theme-toggle-btn:active {
  transform: scale(0.95);
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
  .nav-container {
    padding: 10px 0;
  }
  
  .theme-toggle-btn {
    margin-right: 10px;
    font-size: 16px;
    padding: 6px;
  }
  
  .mobile-menu-toggle {
    display: flex;
    margin-left: 10px;
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
    z-index: 999;
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

/* Extra small screens */
@media (max-width: 480px) {
  .nav-container {
    padding: 8px 0;
  }
  
  .theme-toggle-btn {
    margin-right: 8px;
    font-size: 14px;
    padding: 4px;
  }
  
  .mobile-menu-toggle {
    margin-left: 8px;
  }
  
  .brand-text {
    font-size: 16px;
  }
  
  .brand-logo {
    height: 28px;
    margin-right: 8px;
  }
}
</style>
