<template>
  <div class="page-container">
    <div id="bg"></div>
    <button class="theme-toggle" @click="toggleTheme">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo logo-large">
        <h1>ВЫБЕРИТЕ ГЕНЕРАТОР</h1>
      </header>
      
      <main>
        <nav class="button-group">
          <router-link to="/math" class="btn">
            📊 Генератор Математических Примеров
          </router-link>
          <router-link to="/ktp" class="btn">
            📅 Генератор Дат для КТП
          </router-link>
        </nav>
      </main>
      
      <footer>
        <div class="hint">
          <p><strong>Совет:</strong> Выберите нужный генератор выше для создания учебных материалов.</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
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
    // Проверяем сохраненную тему при загрузке
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      this.isDark = savedTheme === 'dark'
      this.applyTheme()
    } else {
      // Автоматическое определение темы по системным настройкам
      this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      this.applyTheme()
    }
  },
  methods: {
    toggleTheme() {
      this.isDark = !this.isDark
      this.applyTheme()
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light')
    },
    applyTheme() {
      if (this.isDark) {
        document.documentElement.setAttribute('data-theme', 'dark')
      } else {
        document.documentElement.removeAttribute('data-theme')
      }
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
</style> 