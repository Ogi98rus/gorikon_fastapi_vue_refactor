<template>
  <div class="page-container">
    <div id="bg"></div>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo">
        <h1>📊 {{ $t('math.title') }}</h1>
      </header>
      
      <main>
        <form @submit.prevent="generateMath">
          <label for="num_operands">{{ $t('math.operandsLabel') }}</label>
          <input 
            type="number" 
            id="num_operands" 
            v-model.number="formData.numOperands" 
            min="2" 
            max="5" 
            required
          >
          <div class="hint">
            <strong>{{ $t('common.hint') }}:</strong> {{ $t('math.operandsHint') }}
          </div>
          
          <label>{{ $t('math.operationsLabel') }}</label>
          <div class="checkbox-group">
            <label>
              <input type="checkbox" value="+" v-model="formData.operations"> <strong>+</strong> {{ $t('math.addition') }}
            </label>
            <label>
              <input type="checkbox" value="-" v-model="formData.operations"> <strong>-</strong> {{ $t('math.subtraction') }}
            </label>
            <label>
              <input type="checkbox" value="*" v-model="formData.operations"> <strong>×</strong> {{ $t('math.multiplication') }}
            </label>
            <label>
              <input type="checkbox" value="/" v-model="formData.operations"> <strong>÷</strong> {{ $t('math.division') }}
            </label>
          </div>
          <div class="hint">
            <strong>{{ $t('common.hint') }}:</strong> {{ $t('math.operationsHint') }}
          </div>
          
          <label for="range_start">{{ $t('math.intervalStart') }}</label>
          <input 
            type="number" 
            id="range_start" 
            v-model.number="formData.intervalStart" 
            required
          >
          
          <label for="range_end">{{ $t('math.intervalEnd') }}</label>
          <input 
            type="number" 
            id="range_end" 
            v-model.number="formData.intervalEnd" 
            required
          >
          <div class="example">
            <strong>{{ $t('common.example') }}:</strong> {{ $t('math.intervalExample') }}
          </div>
          
          <label for="example_count">{{ $t('math.examplesLabel') }}</label>
          <input 
            type="number" 
            id="example_count" 
            v-model.number="formData.exampleCount" 
            min="1" 
            max="100" 
            required
          >
          <div class="hint">
            <strong>{{ $t('common.recommendation') }}:</strong> {{ $t('math.examplesHint') }}
          </div>
          
          <div class="button-group">
            <button type="submit" :disabled="loading">
              {{ loading ? $t('math.generating') : $t('math.generateButton') }}
            </button>
            <router-link to="/" class="btn">{{ $t('math.homeButton') }}</router-link>
          </div>
        </form>
        
        <!-- Ошибка -->
        <div v-if="error" class="error-message">
          <strong>{{ $t('math.error') }}</strong> {{ error }}
        </div>
      </main>
      
      <footer>
        <div class="hint">
          <h3>{{ $t('math.infoTitle') }}</h3>
          <p>{{ $t('math.infoPositive') }}</p>
          <p>{{ $t('math.infoPDF') }}</p>
          <p>{{ $t('math.infoRandom') }}</p>
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
    
    <!-- Модальное окно выбора варианта скачивания -->
    <div v-if="showDownloadModal" class="modal-overlay" @click="closeDownloadModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('math.downloadModalTitle') }}</h3>
          <button class="modal-close" @click="closeDownloadModal">&times;</button>
        </div>
        
                     <div class="modal-body">
               <div class="download-options">
                 <div class="download-option" @click="downloadPDF(false)">
                   <div class="option-icon">📚</div>
                   <div class="option-content">
                     <h4>{{ $t('math.downloadForStudent') }}</h4>
                     <p>{{ $t('math.studentDescription') }}</p>
                   </div>
                 </div>
                 
                 <div class="download-option" @click="downloadPDF(true)">
                   <div class="option-icon">👨‍🏫</div>
                   <div class="option-content">
                     <h4>{{ $t('math.downloadForTeacher') }}</h4>
                     <p>{{ $t('math.teacherDescription') }}</p>
                   </div>
                 </div>
               </div>
               
               <div class="download-hint">
                 <p>{{ $t('math.downloadBothHint') }}</p>
               </div>
             </div>
        
                     <div class="modal-footer">
               <button class="btn btn-primary" @click="downloadBoth">
                 {{ $t('math.downloadBoth') }}
               </button>
               <button class="btn btn-secondary" @click="closeDownloadModal">
                 {{ $t('math.cancelButton') }}
               </button>
               <button v-if="error" class="btn btn-danger" @click="closeDownloadModal">
                 Закрыть
               </button>
             </div>
      </div>
    </div>
  </div>
</template>

<script>
import i18nMixin from '../utils/i18n-mixin'

export default {
  name: 'MathGenerator',
  mixins: [i18nMixin],
  data() {
    return {
      isDark: false,
      loading: false,
      error: null,

      formData: {
        numOperands: 2,
        operations: ['+'],
        intervalStart: 0,
        intervalEnd: 100,
        exampleCount: 10
      },
      showDownloadModal: false
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
  computed: {
    logoSrc() {
      return this.isDark ? require('../assets/logo_dark.png') : require('../assets/logo.png')
    }
  },
  methods: {
    loadTheme() {
      this.isDark = document.documentElement.hasAttribute('data-theme')
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
    },
    
    async generateMath() {
      if (this.formData.operations.length === 0) {
        this.error = this.$t('math.selectOperation')
        return
      }
      
      // Показываем модальное окно выбора варианта
      this.showDownloadModal = true
    },
    
    closeDownloadModal() {
      this.showDownloadModal = false
    },
    
    async downloadPDF(forTeacher = false) {
      this.loading = true
      this.error = null
      // Не закрываем модальное окно сразу, чтобы пользователь мог скачать оба варианта
      
      try {
        const formData = new FormData()
        formData.append('num_operands', this.formData.numOperands)
        this.formData.operations.forEach(op => formData.append('operations', op))
        formData.append('interval_start', this.formData.intervalStart)
        formData.append('interval_end', this.formData.intervalEnd)
        formData.append('example_count', this.formData.exampleCount)
        formData.append('for_teacher', forTeacher)
        
        const response = await fetch('/api/math-generator', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        })
        
        if (response.ok) {
          const blob = await response.blob()
          
          // Отладочная информация
          console.log(`PDF скачан: размер ${blob.size} байт, тип: ${blob.type}`)
          
          if (blob.size < 1000) {
            console.warn('ВНИМАНИЕ: PDF файл слишком маленький, возможно есть проблема')
            this.error = 'PDF файл слишком маленький, возможно есть проблема генерации'
            return
          }
          
          // Создаем ссылку для скачивания
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          
          // Формируем имя файла
          const variant = forTeacher ? 'teacher' : 'student'
          const filename = `математические_примеры_${this.formData.exampleCount}_${variant}.pdf`
          link.setAttribute('download', filename)
          
          document.body.appendChild(link)
          link.click()
          link.remove()
          
          // Очищаем URL
          window.URL.revokeObjectURL(url)
          
          // Показываем сообщение об успехе
          this.error = null
          
          // Закрываем модальное окно после успешного скачивания
          this.showDownloadModal = false
        } else {
          const errorData = await response.json()
          this.error = errorData.detail || errorData.error || this.$t('math.pdfError')
          // Не закрываем модальное окно при ошибке
        }
      } catch (err) {
        this.error = this.$t('math.connectionError')
        // Не закрываем модальное окно при ошибке
      } finally {
        this.loading = false
      }
    },
    
    async downloadBoth() {
      this.loading = true
      this.error = null
      
      try {
        // Создаем FormData с параметрами
        const formData = new FormData()
        formData.append('num_operands', this.formData.numOperands)
        this.formData.operations.forEach(op => formData.append('operations', op))
        formData.append('interval_start', this.formData.intervalStart)
        formData.append('interval_end', this.formData.intervalEnd)
        formData.append('example_count', this.formData.exampleCount)
        
        // Используем новый endpoint для скачивания ОБОИХ вариантов
        const response = await fetch('/api/math-generator-both', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        })
        
        if (response.ok) {
          const blob = await response.blob()
          
          // Отладочная информация
          console.log(`ZIP архив скачан: размер ${blob.size} байт, тип: ${blob.type}`)
          
          if (blob.size < 1000) {
            console.warn('ВНИМАНИЕ: ZIP архив слишком маленький, возможно есть проблема')
            this.error = 'ZIP архив слишком маленький, возможно есть проблема генерации'
            return
          }
          
          // Создаем ссылку для скачивания
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          
          // Формируем имя файла
          const filename = `математические_примеры_${this.formData.exampleCount}_оба_варианта.zip`
          link.setAttribute('download', filename)
          
          document.body.appendChild(link)
          link.click()
          link.remove()
          
          // Очищаем URL
          window.URL.revokeObjectURL(url)
          
          // Показываем сообщение об успехе
          this.error = null
          
          // Закрываем модальное окно после успешного скачивания
          this.showDownloadModal = false
        } else {
          const errorData = await response.json()
          this.error = errorData.detail || errorData.error || this.$t('math.pdfError')
        }
      } catch (err) {
        this.error = this.$t('math.connectionError')
      } finally {
        this.loading = false
      }
    },
    
    async downloadPDFInternal(forTeacher = false) {
      // Внутренний метод для скачивания без закрытия модального окна
      const formData = new FormData()
      formData.append('num_operands', this.formData.numOperands)
      this.formData.operations.forEach(op => formData.append('operations', op))
      formData.append('interval_start', this.formData.intervalStart)
      formData.append('interval_end', this.formData.intervalEnd)
      formData.append('example_count', this.formData.exampleCount)
      formData.append('for_teacher', forTeacher)
      
              const response = await fetch('/api/math-generator', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })
      
      if (response.ok) {
        const blob = await response.blob()
        
        // Отладочная информация
        console.log(`PDF скачан: размер ${blob.size} байт, тип: ${blob.type}`)
        
        if (blob.size < 1000) {
          console.warn('ВНИМАНИЕ: PDF файл слишком маленький, возможно есть проблема')
          throw new Error('PDF файл слишком маленький, возможно есть проблема генерации')
        }
        
        // Создаем ссылку для скачивания
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Формируем имя файла
        const variant = forTeacher ? 'teacher' : 'student'
        const filename = `математические_примеры_${this.formData.exampleCount}_${variant}.pdf`
        link.setAttribute('download', filename)
        
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        // Очищаем URL
        window.URL.revokeObjectURL(url)
        
        return true
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || errorData.error || this.$t('math.pdfError'))
      }
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

/* Стили для модального окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.download-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.download-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.download-option:hover {
  border-color: var(--accent-primary);
  background: var(--hover-bg);
  transform: translateY(-2px);
}

.option-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.option-content h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.option-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.4;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  text-align: right;
}

.download-hint {
  margin-top: 20px;
  padding: 15px;
  background: rgba(92, 107, 192, 0.1);
  border-radius: 8px;
  text-align: center;
}

.download-hint p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--hover-bg);
}

.btn-danger {
  background: var(--error-color);
  color: white;
}

.btn-danger:hover {
  background: #d32f2f;
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