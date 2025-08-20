<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <!-- 404 Animation -->
      <div class="error-animation">
        <div class="error-number">
          <span class="digit">4</span>
          <span class="digit-0">0</span>
          <span class="digit">4</span>
        </div>
        <div class="error-emoji">😕</div>
      </div>

      <!-- Error Message -->
      <div class="error-message">
        <h1>Страница не найдена</h1>
        <p>
          К сожалению, запрашиваемая страница не существует или была перемещена.
          Возможно, вы перешли по устаревшей ссылке или допустили ошибку в адресе.
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="error-actions">
        <router-link to="/" class="btn btn-primary">
          🏠 Вернуться на главную
        </router-link>
        
        <button @click="goBack" class="btn btn-secondary">
          ⬅️ Назад
        </button>
        
        <router-link to="/math" class="btn btn-outline">
          🧮 Генератор задач
        </router-link>
      </div>

      <!-- Helpful Links -->
      <div class="helpful-links">
        <h3>🔗 Полезные ссылки:</h3>
        <ul>
          <li>
            <router-link to="/">📄 Главная страница</router-link>
          </li>
          <li>
            <router-link to="/math">🧮 Математический генератор</router-link>
          </li>
          <li>
            <router-link to="/ktp">📅 Генератор КТП</router-link>
          </li>
        </ul>
      </div>

      <!-- Search Box -->
      <div class="search-section">
        <h3>🔍 Попробуйте поиск:</h3>
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Что вы ищете?"
            @keyup.enter="performSearch"
          />
          <button @click="performSearch" class="search-btn">
            🔍 Найти
          </button>
        </div>
      </div>

      <!-- Блок поддержки сервера -->
      <div class="server-support">
        <h3>{{ $t('common.serverSupport') }} 🍪✨</h3>
        <div class="iframe-container">
          <iframe
            src="https://yoomoney.ru/quickpay/fundraise/button?billNumber=159RQI2K3KC.240916&"
            width="500" 
            height="50"
            frameborder="0"
            scrolling="no">
          </iframe>
        </div>
      </div>

      <!-- Contact Info -->
      <div class="contact-info">
        <p>
          📧 Если проблема повторяется, 
          <a href="mailto:support@edugenerator.ru">свяжитесь с поддержкой</a>
        </p>
      </div>
    </div>

    <!-- Background Animation -->
    <div class="background-animation">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-shape shape-4"></div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import i18nMixin from '../utils/i18n-mixin'

export default {
  name: 'NotFound',
  mixins: [i18nMixin],
  
  data() {
    return {
      searchQuery: ''
    }
  },

  computed: {
    ...mapGetters('auth', ['isAuthenticated'])
  },

  mounted() {
    // Логирование 404 ошибок для аналитики
    this.logPageNotFound()
  },

  methods: {
    goBack() {
      // Проверяем есть ли история
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        // Если истории нет, идем на главную
        this.$router.push('/')
      }
    },

    performSearch() {
      if (!this.searchQuery.trim()) return
      
      // Простой поиск по ключевым словам
      const query = this.searchQuery.toLowerCase().trim()
      
      if (query.includes('математ') || query.includes('задач') || query.includes('примеры')) {
        this.$router.push('/math')
      } else if (query.includes('ктп') || query.includes('план') || query.includes('календарь')) {
        this.$router.push('/ktp')
      } else if (query.includes('профиль') || query.includes('аккаунт')) {
        if (this.isAuthenticated) {
          this.$router.push('/profile')
        } else {
          this.$router.push('/login')
        }
      } else if (query.includes('стат') || query.includes('аналитик')) {
        if (this.isAuthenticated) {
          this.$router.push('/analytics')
        } else {
          this.$router.push('/login')
        }
      } else {
        // По умолчанию идем на главную
        this.$router.push('/')
      }
      
      // Показываем уведомление
      this.$emit('notification', {
        message: `Выполняется поиск: "${this.searchQuery}"`,
        type: 'info'
      })
    },

    async logPageNotFound() {
      // Отправляем информацию о 404 ошибке в аналитику
      try {
        if (this.isAuthenticated) {
          await this.$store.dispatch('analytics/trackPageView', {
            page: '404',
            path: this.$route.fullPath,
            error_type: 'page_not_found',
            referrer: document.referrer,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        console.warn('Failed to log 404 error:', error)
      }
    }
  }
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.not-found-content {
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 90%;
  text-align: center;
  position: relative;
  z-index: 10;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.error-animation {
  margin-bottom: 30px;
}

.error-number {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.digit,
.digit-0 {
  font-size: 80px;
  font-weight: bold;
  color: var(--accent-primary);
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.digit-0 {
  animation: bounce 2s infinite;
  color: var(--error-color);
}

.error-emoji {
  font-size: 60px;
  animation: shake 3s ease-in-out infinite;
}

.error-message h1 {
  color: var(--text-primary);
  margin: 0 0 20px 0;
  font-size: 28px;
}

.error-message p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 30px;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  margin-bottom: 40px;
}

.helpful-links {
  margin-bottom: 30px;
  text-align: left;
}

.helpful-links h3 {
  color: var(--text-primary);
  margin-bottom: 15px;
  text-align: center;
}

.helpful-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.helpful-links li {
  margin-bottom: 8px;
}

.helpful-links a {
  color: var(--accent-primary);
  text-decoration: none;
  transition: color 0.3s ease;
}

.helpful-links a:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.search-section {
  margin-bottom: 30px;
}

.search-section h3 {
  color: var(--text-primary);
  margin-bottom: 15px;
}

.search-box {
  display: flex;
  gap: 10px;
  max-width: 400px;
  margin: 0 auto;
}

.search-box input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(92, 107, 192, 0.1);
}

.search-btn {
  padding: 12px 20px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.search-btn:hover {
  background: var(--accent-hover);
}

.contact-info {
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 14px;
}

.contact-info a {
  color: var(--accent-primary);
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
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
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(92, 107, 192, 0.3);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: var(--accent-primary);
  border: 2px solid var(--accent-primary);
}

.btn-outline:hover {
  background: var(--accent-primary);
  color: white;
  transform: translateY(-2px);
}

/* Стили для блока поддержки сервера */
.server-support {
  margin: 30px 0;
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.server-support h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.iframe-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.iframe-container iframe {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Адаптивность для мобильных устройств */
@media (max-width: 600px) {
  .iframe-container iframe {
    width: 100% !important;
    max-width: 400px;
  }
  
  .server-support {
    margin: 20px 10px;
    padding: 15px;
  }
}

/* Background Animation */
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  overflow: hidden;
}

.floating-shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 60px;
  height: 60px;
  top: 70%;
  right: 10%;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 40px;
  height: 40px;
  top: 30%;
  right: 30%;
  animation-delay: 1s;
}

/* Animations */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .not-found-content {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .error-number {
    gap: 5px;
  }
  
  .digit,
  .digit-0 {
    font-size: 60px;
  }
  
  .error-emoji {
    font-size: 40px;
  }
  
  .error-message h1 {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .search-box {
    flex-direction: column;
    max-width: 100%;
  }
  
  .btn {
    font-size: 14px;
    padding: 10px 20px;
  }
}

@media (max-width: 480px) {
  .digit,
  .digit-0 {
    font-size: 48px;
  }
  
  .error-emoji {
    font-size: 32px;
  }
  
  .error-message h1 {
    font-size: 20px;
  }
  
  .not-found-content {
    padding: 20px 15px;
  }
}
</style> 