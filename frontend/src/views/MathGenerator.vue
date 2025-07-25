<template>
  <div class="page-container">
    <div id="bg"></div>
    <button class="theme-toggle" @click="toggleTheme">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo">
        <h1>📊 Генерация математических примеров</h1>
      </header>
      
      <main>
        <form @submit.prevent="generateMath">
          <label for="num_operands">Количество операндов:</label>
          <input 
            type="number" 
            id="num_operands" 
            v-model.number="formData.numOperands" 
            min="2" 
            max="5" 
            required
          >
          <div class="hint">
            <strong>Подсказка:</strong> Количество чисел в примере (от 2 до 5). Например: при значении 3 получится "2 + 3 - 1 = 4"
          </div>
          
          <label>Операции:</label>
          <div class="checkbox-group">
            <label>
              <input type="checkbox" value="+" v-model="formData.operations"> <strong>+</strong> (Сложение)
            </label>
            <label>
              <input type="checkbox" value="-" v-model="formData.operations"> <strong>-</strong> (Вычитание)
            </label>
            <label>
              <input type="checkbox" value="*" v-model="formData.operations"> <strong>×</strong> (Умножение)
            </label>
            <label>
              <input type="checkbox" value="/" v-model="formData.operations"> <strong>÷</strong> (Деление)
            </label>
          </div>
          <div class="hint">
            <strong>Подсказка:</strong> Выберите операции, которые будут использоваться в примерах. Можно выбрать несколько.
          </div>
          
          <label for="range_start">Начало интервала:</label>
          <input 
            type="number" 
            id="range_start" 
            v-model.number="formData.intervalStart" 
            required
          >
          
          <label for="range_end">Конец интервала:</label>
          <input 
            type="number" 
            id="range_end" 
            v-model.number="formData.intervalEnd" 
            required
          >
          <div class="example">
            <strong>Пример диапазона:</strong> от 0 до 100 — числа будут от 0 до 100 включительно
          </div>
          
          <label for="example_count">Количество примеров:</label>
          <input 
            type="number" 
            id="example_count" 
            v-model.number="formData.exampleCount" 
            min="1" 
            max="100" 
            required
          >
          <div class="hint">
            <strong>Рекомендация:</strong> Для одного урока оптимально 10-20 примеров
          </div>
          
          <div class="button-group">
            <button type="submit" :disabled="loading">
              {{ loading ? '⏳ Генерация...' : '📄 Сгенерировать PDF' }}
            </button>
            <router-link to="/" class="btn">🏠 На главную</router-link>
          </div>
        </form>
        
        <!-- Rate Limit ошибка -->
        <RateLimitError 
          v-if="rateLimitError" 
          :error="rateLimitError"
          :is-authenticated="isAuthenticated"
          @countdown-finished="onCountdownFinished"
        />
        
        <!-- Обычная ошибка -->
        <div v-if="error && !rateLimitError" class="error-message">
          <strong>Ошибка:</strong> {{ error }}
        </div>
      </main>
      
      <footer>
        <div class="hint">
          <h3>ℹ️ Информация о генераторе</h3>
          <p>• Генератор создает математические примеры только с <span class="example-green">положительными результатами</span></p>
          <p>• PDF файл будет содержать примеры с ответами для проверки</p>
          <p>• Все примеры генерируются случайно в указанном диапазоне</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
import RateLimitError from '@/components/RateLimitError.vue'

export default {
  name: 'MathGenerator',
  components: {
    RateLimitError
  },
  data() {
    return {
      isDark: false,
      loading: false,
      error: null,
      rateLimitError: null,
      formData: {
        numOperands: 2,
        operations: ['+'],
        intervalStart: 0,
        intervalEnd: 100,
        exampleCount: 10
      }
    }
  },
  mounted() {
    this.loadTheme()
  },
  computed: {
    logoSrc() {
      return this.isDark ? require('../assets/logo_dark.png') : require('../assets/logo.png')
    },
    isAuthenticated() {
      return this.$store.getters['auth/isAuthenticated']
    }
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
    async generateMath() {
      if (this.formData.operations.length === 0) {
        this.error = 'Выберите хотя бы одну операцию'
        return
      }
      
      this.loading = true
      this.error = null
      this.rateLimitError = null
      
      try {
        const formData = new FormData()
        formData.append('num_operands', this.formData.numOperands)
        this.formData.operations.forEach(op => formData.append('operation', op))
        formData.append('interval_start', this.formData.intervalStart)
        formData.append('interval_end', this.formData.intervalEnd)
        formData.append('example_count', this.formData.exampleCount)
        
        const response = await this.$store.state.auth.token
          ? await fetch('http://localhost:8000/api/math-generator', {
              method: 'POST',
              body: formData,
              headers: {
                'Authorization': `Bearer ${this.$store.state.auth.token}`
              }
            })
          : await fetch('http://localhost:8000/api/math-generator', {
              method: 'POST',
              body: formData
            })
        
        if (response.ok) {
          const blob = await response.blob()
          
          // Создаем ссылку для скачивания
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', 'математические_примеры.pdf')
          document.body.appendChild(link)
          link.click()
          link.remove()
          
          // Сохраняем данные для страницы результата
          localStorage.setItem('lastResult', JSON.stringify({
            type: 'math',
            fileName: 'математические_примеры.pdf',
            description: `Сгенерировано ${this.formData.exampleCount} примеров с операциями: ${this.formData.operations.join(', ')}`,
            downloaded: true
          }))
          
          // Переходим на страницу результата
          this.$router.push('/result')
        } else {
          const errorData = await response.json()
          
          // Проверяем, является ли это rate limit ошибкой
          if (response.status === 429 && errorData.code === 'RATE_LIMIT_EXCEEDED') {
            this.rateLimitError = errorData
          } else {
            this.error = errorData.detail || errorData.error || 'Ошибка генерации PDF'
          }
        }
      } catch (err) {
        this.error = 'Ошибка соединения с сервером'
      } finally {
        this.loading = false
      }
    },
    
    onCountdownFinished() {
      // Сбрасываем rate limit ошибку когда таймер закончился
      this.rateLimitError = null
      
      // Можно показать уведомление что лимит сброшен
      console.log('Rate limit сброшен, можно генерировать снова!')
    }
  }
}
</script>

<style scoped>
.error-message {
  background: rgba(244, 67, 54, 0.1);
  border-left: 4px solid var(--error-color);
  padding: 12px 16px;
  margin: 15px 0;
  border-radius: 4px;
  color: var(--error-color);
  font-weight: 500;
}

.checkbox-group {
  margin: 15px 0;
}

.checkbox-group label {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: 1.1em;
}

form {
  text-align: left;
}

.button-group {
  margin-top: 30px;
  text-align: center;
}
</style> 