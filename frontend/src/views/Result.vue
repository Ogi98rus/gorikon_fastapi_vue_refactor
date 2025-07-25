<template>
  <div class="page-container">
    <div id="bg"></div>
    <button class="theme-toggle" @click="toggleTheme">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
    
    <div class="container result-container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo">
        <h1>✅ Файл успешно сгенерирован!</h1>
      </header>
      
      <main>
        <div class="success-message">
          <p><strong>{{ description }}</strong></p>
          <p>Файл автоматически скачан. Проверьте папку загрузок на вашем компьютере.</p>
        </div>
        
        <div v-if="downloaded" class="success-note">
          <p>✅ <strong>Файл "{{ fileName }}" успешно скачан!</strong></p>
          <p>📁 Найдите его в папке "Загрузки" на вашем компьютере</p>
        </div>
        
        <div class="action-buttons">
          <div class="button-group">
            <button @click="goBack" class="btn">
              🔄 Создать ещё
            </button>
            <router-link to="/" class="btn">
              🏠 На главную
            </router-link>
          </div>
        </div>
        
      </main>
      
      <footer>
        <div class="hint">
          <h3>💡 Полезные советы</h3>
          <div v-if="type === 'math'">
            <p>• PDF файл содержит математические примеры с ответами</p>
            <p>• Можете распечатать файл для использования в классе</p>
            <p>• Ответы помогут быстро проверить работы учеников</p>
          </div>
          <div v-else-if="type === 'ktp'">
            <p>• Excel файл содержит календарно-тематическое планирование</p>
            <p>• Даты отформатированы для удобного чтения (ДД.ММ)</p>
            <p>• Можете добавить дополнительные столбцы с темами уроков</p>
            <p>• Не забудьте добавить переносы рабочих дней вручную!</p>
          </div>
        </div>
        
        <div class="hint">
          <h3>🔗 Поделиться генератором</h3>
          <p>Расскажите коллегам об этом удобном инструменте для создания учебных материалов!</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultPage',
  data() {
    return {
      isDark: false,
      downloaded: false,
      fileUrl: '',
      fileName: '',
      description: '',
      type: ''
    }
  },
  computed: {
    logoSrc() {
      return this.isDark ? require('../assets/logo_dark.png') : require('../assets/logo.png')
    }
  },
  mounted() {
    this.loadTheme()
    this.loadResultData()
  },
  methods: {
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
      } else {
        document.documentElement.removeAttribute('data-theme')
      }
    },
    loadResultData() {
      // Получаем данные из localStorage
      const resultData = localStorage.getItem('lastResult')
      
      if (resultData) {
        const data = JSON.parse(resultData)
        this.type = data.type || ''
        this.fileName = data.fileName || 'file'
        this.description = data.description || 'Файл сгенерирован'
        this.downloaded = data.downloaded || false
        
        // Очищаем данные после загрузки
        localStorage.removeItem('lastResult')
      } else {
        // Если нет данных, возвращаемся на главную
        this.$router.push('/')
      }
    },
    getDownloadText() {
      if (this.type === 'math') {
        return '📄 Скачать PDF с примерами'
      } else if (this.type === 'ktp') {
        return '📊 Скачать Excel с расписанием'
      }
      return '📥 Скачать файл'
    },
    handleDownload() {
      // Отмечаем, что файл был скачан
      setTimeout(() => {
        this.downloaded = true
      }, 1000)
    },
    goBack() {
      // Возвращаемся к соответствующему генератору
      if (this.type === 'math') {
        this.$router.push('/math-generator')
      } else if (this.type === 'ktp') {
        this.$router.push('/ktp-generator')
      } else {
        this.$router.push('/')
      }
    }
  }
}
</script>

<style scoped>
.result-container {
  max-width: 600px;
  text-align: center;
}

.success-message {
  background: rgba(76, 175, 80, 0.1);
  border-left: 4px solid var(--success-color);
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  color: var(--text-primary);
}

.success-message p {
  margin: 8px 0;
  font-size: 16px;
}

.download-links {
  margin: 30px 0;
}

.download-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 20px 40px;
  background: linear-gradient(135deg, var(--success-color), #66bb6a);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 18px;
  transition: all 0.3s ease;
  min-width: 300px;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.download-link:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
  background: linear-gradient(135deg, #66bb6a, var(--success-color));
}

.download-link:active {
  transform: translateY(-1px);
}

.action-buttons {
  margin: 30px 0;
}

.action-buttons .button-group {
  gap: 15px;
}

.action-buttons .btn {
  padding: 12px 20px;
  font-size: 16px;
  min-width: 160px;
}

.success-note {
  background: rgba(76, 175, 80, 0.1);
  border: 2px solid var(--success-color);
  padding: 15px;
  margin: 20px 0;
  border-radius: 8px;
  color: var(--success-color);
  font-weight: 500;
  animation: fadeIn 0.5s ease;
}

.success-note p {
  margin: 5px 0;
}

footer {
  margin-top: 40px;
}

footer .hint {
  text-align: left;
}

footer .hint h3 {
  text-align: center;
  margin-bottom: 15px;
  color: var(--text-primary);
}

footer .hint p {
  margin: 8px 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .download-link {
    min-width: 100%;
    padding: 16px 20px;
    font-size: 16px;
  }
  
  .action-buttons .button-group {
    flex-direction: column;
  }
  
  .action-buttons .btn {
    min-width: 100%;
  }
}
</style> 