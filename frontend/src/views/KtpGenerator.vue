<template>
  <div class="page-container">
    <div id="bg"></div>
    <button class="theme-toggle" @click="toggleTheme">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo">
        <h1>📅 Генератор для КТП</h1>
      </header>
      
      <main>
        <form @submit.prevent="generateSchedule">
          <label for="start_date">Начальная дата:</label>
          <input 
            type="date" 
            id="start_date" 
            v-model="formData.startDate" 
            required
          >
          
          <label for="end_date">Конечная дата:</label>
          <input 
            type="date" 
            id="end_date" 
            v-model="formData.endDate" 
            required
          >
          <div class="hint">
            <strong>Подсказка:</strong> Укажите период учебного года (например, с 01.09.2024 по 31.05.2025)
          </div>
          
          <label>Дни недели и количество уроков в день:</label>
          <div class="weekday-section">
            <div v-for="(day, index) in weekDays" :key="index" class="weekday-row">
              <label class="weekday-label">
                <input 
                  type="checkbox" 
                  :value="index" 
                  v-model="formData.weekdays"
                >
                <strong>{{ day }}</strong>
              </label>
              <input 
                type="number" 
                v-model.number="formData.lessonsPerDay[index]" 
                min="1" 
                max="10"
                :disabled="!formData.weekdays.includes(index)"
                placeholder="Уроков"
              >
            </div>
          </div>
          <div class="hint">
            <strong>Подсказка:</strong> Выберите рабочие дни недели и укажите количество уроков в каждый день
          </div>
          
          <label for="holidays">Праздничные дни (разделитель - запятая):</label>
          <input 
            type="text" 
            id="holidays" 
            v-model="formData.holidays" 
            placeholder="08.03.2025, 01.05.2025, 09.05.2025"
          >
          <div class="example">
            <strong>Пример:</strong> <span class="example-red">08.03.2025,01.05.2025,09.05.2025</span>
          </div>
          
          <label for="autumn_start">Начало осенних каникул:</label>
          <input 
            type="date" 
            id="autumn_start" 
            v-model="formData.autumnStart"
          >
          
          <label for="autumn_end">Конец осенних каникул:</label>
          <input 
            type="date" 
            id="autumn_end" 
            v-model="formData.autumnEnd"
          >
          
          <label for="winter_start">Начало зимних каникул:</label>
          <input 
            type="date" 
            id="winter_start" 
            v-model="formData.winterStart"
          >
          
          <label for="winter_end">Конец зимних каникул:</label>
          <input 
            type="date" 
            id="winter_end" 
            v-model="formData.winterEnd"
          >
          
          <label for="spring_start">Начало весенних каникул:</label>
          <input 
            type="date" 
            id="spring_start" 
            v-model="formData.springStart"
          >
          
          <label for="spring_end">Конец весенних каникул:</label>
          <input 
            type="date" 
            id="spring_end" 
            v-model="formData.springEnd"
          >
          <div class="hint">
            <strong>Подсказка:</strong> Укажите периоды каникул. Эти дни будут исключены из расписания
          </div>
          
          <div class="first-grade-section">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.includeFirstGradeVacation"
              >
              <strong>+ Каникулы для 1 классов</strong>
            </label>
            
            <div v-if="formData.includeFirstGradeVacation" class="first-grade-dates">
              <label for="first_grade_start">Начало дополнительных каникул для 1 классов:</label>
              <input 
                type="date" 
                id="first_grade_start" 
                v-model="formData.firstGradeStart"
              >
              
              <label for="first_grade_end">Конец дополнительных каникул для 1 классов:</label>
              <input 
                type="date" 
                id="first_grade_end" 
                v-model="formData.firstGradeEnd"
              >
              <div class="example">
                <strong>Обычно:</strong> дополнительные каникулы для 1 классов проводятся в феврале (например, с 14.02 по 20.02)
              </div>
            </div>
          </div>
          
          <label for="file_name">Имя файла для сохранения:</label>
          <input 
            type="text" 
            id="file_name" 
            v-model="formData.fileName" 
            placeholder="schedule"
          >
          <div class="example">
            <strong>Пример:</strong> КТП_математика_5класс
          </div>
          
          <div class="button-group">
            <button type="submit" :disabled="loading">
              {{ loading ? '⏳ Генерация...' : '📊 Сгенерировать расписание' }}
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
          <h3>⚠️ ВАЖНО! ДАТЫ КОТОРЫЕ НЕОБХОДИМО ДОБАВИТЬ ВРУЧНУЮ</h3>
          <p><span class="example-green">28.12.2024 Суббота - работаем по вторнику</span></p>
          <p>Такие переносы рабочих дней нужно добавлять в расписание самостоятельно</p>
        </div>
        
        <div class="hint">
          <h3>ℹ️ Информация о генераторе</h3>
          <p>• Генератор создает календарно-тематическое планирования в формате Excel</p>
          <p>• Автоматически исключает праздники и каникулы</p>
          <p>• Учитывает количество уроков по дням недели</p>
          <p>• Поддерживает дополнительные каникулы для 1 классов</p>
          <p>• Формат дат в файле: ДД.ММ для удобства</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
import RateLimitError from '@/components/RateLimitError.vue'

export default {
  name: 'KtpGenerator',
  components: {
    RateLimitError
  },
  data() {
    return {
      isDark: false,
      loading: false,
      error: null,
      rateLimitError: null,
      weekDays: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
      formData: {
        startDate: '',
        endDate: '',
        weekdays: [0, 1, 2, 3, 4], // По умолчанию рабочие дни
        lessonsPerDay: [1, 1, 1, 1, 1, 0, 0], // По умолчанию по 1 уроку в рабочие дни
        holidays: '',
        autumnStart: '',
        autumnEnd: '',
        winterStart: '',
        winterEnd: '',
        springStart: '',
        springEnd: '',
        fileName: 'schedule',
        includeFirstGradeVacation: false,
        firstGradeStart: '',
        firstGradeEnd: ''
      }
    }
  },
  computed: {
    logoSrc() {
      return this.isDark ? require('../assets/logo_dark.png') : require('../assets/logo.png')
    },
    isAuthenticated() {
      return this.$store.getters['auth/isAuthenticated']
    }
  },
  mounted() {
    this.loadTheme()
    this.setDefaultDates()
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
    setDefaultDates() {
      const now = new Date()
      const currentYear = now.getFullYear()
      
      // Устанавливаем примерные даты учебного года
      this.formData.startDate = `${currentYear}-09-01`
      this.formData.endDate = `${currentYear + 1}-05-31`
      
      // Примерные каникулы
      this.formData.autumnStart = `${currentYear}-10-26`
      this.formData.autumnEnd = `${currentYear}-11-03`
      this.formData.winterStart = `${currentYear}-12-25`
      this.formData.winterEnd = `${currentYear + 1}-01-08`
      this.formData.springStart = `${currentYear + 1}-03-25`
      this.formData.springEnd = `${currentYear + 1}-04-02`
      
      // Дополнительные каникулы для 1 классов (обычно в феврале)
      this.formData.firstGradeStart = `${currentYear + 1}-02-14`
      this.formData.firstGradeEnd = `${currentYear + 1}-02-20`
    },
    formatDateForBackend(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit', 
        year: 'numeric'
      })
    },
    async generateSchedule() {
      if (this.formData.weekdays.length === 0) {
        this.error = 'Выберите хотя бы один день недели'
        return
      }
      
      this.loading = true
      this.error = null
      this.rateLimitError = null
      
      try {
        const formData = new FormData()
        formData.append('start_date', this.formData.startDate)
        formData.append('end_date', this.formData.endDate)
        
        this.formData.weekdays.forEach(day => formData.append('weekdays', day))
        this.formData.lessonsPerDay.forEach(lessons => formData.append('lessons_per_day', lessons))
        
        // Обрабатываем праздники
        if (this.formData.holidays) {
          this.formData.holidays.split(',').forEach(holiday => {
            const trimmed = holiday.trim()
            if (trimmed) formData.append('holidays', trimmed)
          })
        }
        
        // Обрабатываем каникулы
        const vacationDates = []
        
        if (this.formData.autumnStart && this.formData.autumnEnd) {
          const start = new Date(this.formData.autumnStart)
          const end = new Date(this.formData.autumnEnd)
          for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            vacationDates.push(this.formatDateForBackend(d.toISOString().split('T')[0]))
          }
        }
        
        if (this.formData.winterStart && this.formData.winterEnd) {
          const start = new Date(this.formData.winterStart)
          const end = new Date(this.formData.winterEnd)
          for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            vacationDates.push(this.formatDateForBackend(d.toISOString().split('T')[0]))
          }
        }
        
        if (this.formData.springStart && this.formData.springEnd) {
          const start = new Date(this.formData.springStart)
          const end = new Date(this.formData.springEnd)
          for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            vacationDates.push(this.formatDateForBackend(d.toISOString().split('T')[0]))
          }
        }

        if (this.formData.includeFirstGradeVacation) {
          if (this.formData.firstGradeStart && this.formData.firstGradeEnd) {
            const start = new Date(this.formData.firstGradeStart)
            const end = new Date(this.formData.firstGradeEnd)
            for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
              vacationDates.push(this.formatDateForBackend(d.toISOString().split('T')[0]))
            }
          }
        }
        
        vacationDates.forEach(date => formData.append('vacation', date))
        formData.append('file_name', this.formData.fileName)
        
        const response = await this.$store.state.auth.token
          ? await fetch('http://localhost:8000/api/ktp-generator', {
              method: 'POST',
              body: formData,
              credentials: 'include',
              headers: {
                'Authorization': `Bearer ${this.$store.state.auth.token}`
              }
            })
          : await fetch('http://localhost:8000/api/ktp-generator', {
              method: 'POST',
              body: formData,
              credentials: 'include'
            })
        
        if (response.ok) {
          const blob = await response.blob()
          
          // Создаем ссылку для скачивания
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', `${this.formData.fileName}.xlsx`)
          document.body.appendChild(link)
          link.click()
          link.remove()
          
          // Сохраняем данные для страницы результата
          localStorage.setItem('lastResult', JSON.stringify({
            type: 'ktp',
            fileName: `${this.formData.fileName}.xlsx`,
            description: `Расписание с ${this.formData.startDate} по ${this.formData.endDate}`,
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
            this.error = errorData.detail || errorData.error || 'Ошибка генерации Excel'
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

.weekday-section {
  background: rgba(92, 107, 192, 0.05);
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
}

.weekday-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.weekday-row:hover {
  background-color: rgba(92, 107, 192, 0.1);
}

.weekday-label {
  display: flex;
  align-items: center;
  min-width: 150px;
  margin: 0;
  font-weight: 500;
}

.weekday-label input[type="checkbox"] {
  margin-right: 10px;
  width: auto;
}

.weekday-row input[type="number"] {
  width: 100px;
  margin: 0;
}

.weekday-row input[type="number"]:disabled {
  opacity: 0.5;
  background-color: var(--bg-secondary);
}

form {
  text-align: left;
}

.button-group {
  margin-top: 30px;
  text-align: center;
}

.first-grade-section {
  background: rgba(92, 107, 192, 0.05);
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 10px;
  width: auto;
}

.first-grade-dates {
  margin-left: 20px;
}

.first-grade-dates label {
  display: block;
  margin-bottom: 8px;
  font-weight: 400;
}

.first-grade-dates input[type="date"] {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  box-sizing: border-box;
  margin-bottom: 10px;
}

.first-grade-dates .example {
  font-size: 0.9em;
  color: var(--text-secondary);
  margin-top: 5px;
}
</style> 