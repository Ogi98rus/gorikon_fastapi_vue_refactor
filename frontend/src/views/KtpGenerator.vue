<template>
  <div class="page-container">
    <div id="bg"></div>
    <button class="theme-toggle" @click="toggleTheme">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo">
        <h1>📅 {{ $t('ktp.title') }}</h1>
      </header>
      
      <main>
        <form @submit.prevent="generateSchedule">
          <label for="start_date">{{ $t('ktp.startDateLabel') }}</label>
          <input 
            type="date" 
            id="start_date" 
            v-model="formData.startDate" 
            required
          >
          
          <label for="end_date">{{ $t('ktp.endDateLabel') }}</label>
          <input 
            type="date" 
            id="end_date" 
            v-model="formData.endDate" 
            required
          >
          <div class="hint">
            <strong>{{ $t('common.hint') }}:</strong> {{ $t('ktp.dateHint') }}
          </div>
          
          <label>{{ $t('ktp.weekdaysLabel') }}</label>
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
                :placeholder="$t('ktp.lessonsPlaceholder')"
              >
            </div>
          </div>
          <div class="hint">
            <strong>{{ $t('common.hint') }}:</strong> {{ $t('ktp.weekdaysHint') }}
          </div>
          
          <label for="holidays">{{ $t('ktp.holidaysLabel') }}</label>
          <input 
            type="text" 
            id="holidays" 
            v-model="formData.holidays" 
            :placeholder="$t('ktp.holidaysPlaceholder')"
          >
          <div class="example">
            <strong>{{ $t('common.example') }}:</strong> <span class="example-red">{{ $t('ktp.holidaysExample') }} 08.03.2025,01.05.2025,09.05.2025</span>
          </div>
          
          <label for="autumn_start">{{ $t('ktp.autumnStart') }}</label>
          <input 
            type="date" 
            id="autumn_start" 
            v-model="formData.autumnStart"
          >
          
          <label for="autumn_end">{{ $t('ktp.autumnEnd') }}</label>
          <input 
            type="date" 
            id="autumn_end" 
            v-model="formData.autumnEnd"
          >
          
          <label for="winter_start">{{ $t('ktp.winterStart') }}</label>
          <input 
            type="date" 
            id="winter_start" 
            v-model="formData.winterStart"
          >
          
          <label for="winter_end">{{ $t('ktp.winterEnd') }}</label>
          <input 
            type="date" 
            id="winter_end" 
            v-model="formData.winterEnd"
          >
          
          <label for="spring_start">{{ $t('ktp.springStart') }}</label>
          <input 
            type="date" 
            id="spring_start" 
            v-model="formData.springStart"
          >
          
          <label for="spring_end">{{ $t('ktp.springEnd') }}</label>
          <input 
            type="date" 
            id="spring_end" 
            v-model="formData.springEnd"
          >
          <div class="hint">
            <strong>{{ $t('common.hint') }}:</strong> {{ $t('ktp.holidaysHint') }}
          </div>
          
          <div class="first-grade-section">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.includeFirstGradeVacation"
              >
              <strong>+ {{ $t('ktp.firstClassHolidays') }}</strong>
            </label>
            
            <div v-if="formData.includeFirstGradeVacation" class="first-grade-dates">
              <label for="first_grade_start">{{ $t('ktp.firstGradeStart') }}</label>
              <input 
                type="date" 
                id="first_grade_start" 
                v-model="formData.firstGradeStart"
              >
              
              <label for="first_grade_end">{{ $t('ktp.firstGradeEnd') }}</label>
              <input 
                type="date" 
                id="first_grade_end" 
                v-model="formData.firstGradeEnd"
              >
              <div class="example">
                <strong>{{ $t('ktp.firstGradeHint') }}</strong>
              </div>
            </div>
          </div>
          
          <label for="file_name">{{ $t('ktp.filenameLabel') }}</label>
          <input 
            type="text" 
            id="file_name" 
            v-model="formData.fileName" 
            :placeholder="$t('ktp.filenamePlaceholder')"
          >
          <div class="example">
            <strong>{{ $t('common.example') }}:</strong> {{ $t('ktp.filenameExample') }}
          </div>
          
          <div class="button-group">
            <button type="submit" :disabled="loading">
              {{ loading ? $t('ktp.generating') : $t('ktp.generateButton') }}
            </button>
            <router-link to="/" class="btn">{{ $t('ktp.homeButton') }}</router-link>
          </div>
        </form>
        
        <!-- Ошибка -->
        <div v-if="error" class="error-message">
          <strong>{{ $t('common.error') }}:</strong> {{ error }}
        </div>
      </main>
      
      <footer>
        <div class="hint">
          <h3>{{ $t('ktp.importantNote') }}</h3>
          <p><span class="example-green">{{ $t('ktp.workdayTransfer') }}</span></p>
          <p>{{ $t('ktp.workdayTransferHint') }}</p>
        </div>
        
        <div class="hint">
          <h3>{{ $t('ktp.generatorInfo') }}</h3>
          <p>{{ $t('ktp.generatorInfo1') }}</p>
          <p>{{ $t('ktp.generatorInfo2') }}</p>
          <p>{{ $t('ktp.generatorInfo3') }}</p>
          <p>{{ $t('ktp.generatorInfo4') }}</p>
          <p>{{ $t('ktp.generatorInfo5') }}</p>
        </div>
        
        <!-- Блок поддержки сервера -->
        <div class="server-support">
          <h3>{{ $t('common.serverSupport') }} 🍪✨</h3>
          <div class="iframe-container">
            <iframe
              src="hhttps://yoomoney.ru/quickpay/fundraise/button?billNumber=159RQI2K3KC.240916&"
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
  name: 'KtpGenerator',
  mixins: [i18nMixin],
  data() {
    return {
      isDark: false,
      loading: false,
      error: null,

      weekDays: [],
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
    
    currentLanguage() {
      return this.$store.state.i18n.currentLanguage
    }
  },
  
  watch: {
    currentLanguage() {
      // Обновляем дни недели при смене языка
      this.initializeWeekDays()
    }
  },
  mounted() {
    this.loadTheme()
    this.setDefaultDates()
    this.initializeWeekDays()
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
    initializeWeekDays() {
      this.weekDays = [
        this.$t('ktp.weekdayMonday'),
        this.$t('ktp.weekdayTuesday'),
        this.$t('ktp.weekdayWednesday'),
        this.$t('ktp.weekdayThursday'),
        this.$t('ktp.weekdayFriday'),
        this.$t('ktp.weekdaySaturday'),
        this.$t('ktp.weekdaySunday')
      ]
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
        this.error = this.$t('ktp.selectWeekdayError')
        return
      }
      
      this.loading = true
      this.error = null
      
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
        
        const response = await fetch('/api/ktp-generator', {
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
          
          // Показываем сообщение об успехе
          this.error = null
        } else {
          const errorData = await response.json()
          
          this.error = errorData.detail || errorData.error || 'Ошибка генерации Excel'
        }
      } catch (err) {
        this.error = 'Ошибка соединения с сервером'
      } finally {
        this.loading = false
      }
    },
    

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