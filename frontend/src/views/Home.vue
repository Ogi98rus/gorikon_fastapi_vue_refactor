<template>
  <div class="page-container">
    <div id="bg"></div>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo logo-large">
        <h1>{{ $t('home.title') }}</h1>
      </header>
      
      <main>
        <nav class="button-group">
          <router-link to="/math" class="btn">
            {{ $t('home.mathGenerator') }}
          </router-link>
          <router-link to="/ktp" class="btn">
            {{ $t('home.ktpGenerator') }}
          </router-link>
        </nav>
      </main>
      
      <footer>
        <div class="hint">
          <p>{{ $t('home.advice') }}</p>
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
      </footer>
    </div>
  </div>
</template>

<script>
import i18nMixin from '../utils/i18n-mixin'

export default {
  name: 'HomePage',
  mixins: [i18nMixin],
  data() {
    return {
      isDark: false
    }
  },
  computed: {
    logoSrc() {
      return this.isDark ? require('../assets/logo_dark.png') : require('../assets/logo.png')
    }
  },
  mounted() {
    // Загружаем тему из App.vue
    this.loadTheme()
    // Слушаем изменения темы через MutationObserver
    this.observeThemeChanges()
  },
  
  beforeUnmount() {
    // Очищаем observer
    if (this.themeObserver) {
      this.themeObserver.disconnect()
    }
  },
  methods: {
    loadTheme() {
      this.isDark = document.documentElement.hasAttribute('data-theme')
      console.log(`🏠 Home: Тема загружена, isDark = ${this.isDark}`)
    },
    
    observeThemeChanges() {
      // Создаем MutationObserver для отслеживания изменений атрибута data-theme
      this.themeObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            this.loadTheme()
          }
        })
      })
      
      // Начинаем наблюдение за изменениями атрибутов
      this.themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
      })
    }
  }
}
</script>

<style scoped>
/* Дополнительные стили для главной страницы */
.page-container {
  overflow: hidden;
}

.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.button-group .btn {
  font-size: 18px;
  padding: 16px 32px;
  min-width: 280px;
}

footer {
  margin-top: 30px;
}

/* Стили для блока поддержки сервера */
.server-support {
  margin-top: 40px;
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  max-width: 600px;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Адаптивность для мобильных устройств */
@media (max-width: 600px) {
  .iframe-container iframe {
    width: 100% !important;
    max-width: 400px;
  }
  
  .server-support {
    margin: 20px 10px 0 10px;
    padding: 15px;
  }
}
</style> 