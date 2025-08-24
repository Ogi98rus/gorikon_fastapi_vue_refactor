нф<template>
  <div class="page-container">
    <div id="bg"></div>
    
    <div class="container">
      <header>
        <img :src="logoSrc" alt="Логотип Gorikon" class="logo">
        <h1>🎮 {{ $t('nav.mathGame') }}</h1>
        <p>Развивайте математические навыки в увлекательной игровой форме!</p>
      </header>
      
      <main>
        <!-- Настройки игры -->
        <div v-if="!gameStarted && !gameCompleted" class="game-settings">
          <h2>⚙️ Настройки игры</h2>
          
          <form @submit.prevent="startGame">
            <div class="form-group">
              <label>Типы операций:</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.operations" value="addition">
                  <span>➕ Сложение</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.operations" value="subtraction">
                  <span>➖ Вычитание</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.operations" value="multiplication">
                  <span>✖️ Умножение</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="settings.operations" value="division">
                  <span>➗ Деление</span>
                </label>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="min_number">Минимальное число:</label>
                <input 
                  type="number" 
                  id="min_number"
                  v-model="settings.min_number" 
                  min="1" 
                  max="100"
                  required
                >
              </div>
              <div class="form-group">
                <label for="max_number">Максимальное число:</label>
                <input 
                  type="number" 
                  id="max_number"
                  v-model="settings.max_number" 
                  min="1" 
                  max="1000"
                  required
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="examples_count">Количество примеров:</label>
                <input 
                  type="number" 
                  id="examples_count"
                  v-model="settings.examples_count" 
                  min="5" 
                  max="50"
                  required
                >
              </div>
              <div class="form-group">
                <label for="time_limit">Время на ответ (сек):</label>
                <input 
                  type="number" 
                  id="time_limit"
                  v-model="settings.time_limit" 
                  min="10" 
                  max="300" 
                  placeholder="Без ограничений"
                >
              </div>
            </div>

            <div class="button-group">
              <button type="submit" class="btn" :disabled="!canStartGame">
                🚀 Начать игру
              </button>
              <router-link to="/" class="btn btn-secondary">
                🏠 На главную
              </router-link>
            </div>
          </form>
        </div>

        <!-- Игровой процесс -->
        <div v-if="gameStarted && !gameCompleted" class="game-play">
          <div class="game-header">
            <div class="progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
              </div>
              <span class="progress-text">{{ currentExampleIndex + 1 }} / {{ totalExamples }}</span>
            </div>
            
            <div v-if="settings.time_limit" class="timer">
              ⏱️ {{ formatTime(timeLeft) }}
            </div>
          </div>

          <div v-if="currentExample" class="question-card">
            <h2 class="question">{{ currentExample.question }}</h2>
            
            <div class="options">
              <button
                v-for="option in currentExample.options"
                :key="option"
                @click="selectAnswer(option)"
                class="option-btn"
                :class="{ 'selected': selectedAnswer === option }"
              >
                {{ option }}
              </button>
            </div>

            <div class="game-actions">
              <button @click="submitAnswer" class="btn btn-success" :disabled="selectedAnswer === null">
                ✅ Ответить
              </button>
              <button @click="skipExample" class="btn btn-secondary">
                ⏭️ Следующий пример
              </button>
            </div>
          </div>
        </div>

        <!-- Результаты игры -->
        <div v-if="gameCompleted" class="game-results">
          <h2>🏆 Результаты игры</h2>
          
          <div class="results-card">
            <div class="result-item">
              <span class="label">Правильных ответов:</span>
              <span class="value correct">{{ gameResult.correct_answers }}</span>
            </div>
            
            <div class="result-item">
              <span class="label">Всего примеров:</span>
              <span class="value">{{ gameResult.total_examples }}</span>
            </div>
            
            <div class="result-item">
              <span class="label">Процент правильных:</span>
              <span class="value">{{ gameResult.percentage.toFixed(1) }}%</span>
            </div>
            
            <div class="result-item">
              <span class="label">Время игры:</span>
              <span class="value">{{ formatTime(gameResult.time_spent) }}</span>
            </div>
            
            <div class="result-item score">
              <span class="label">Оценка:</span>
              <span class="value score-value" :class="'score-' + gameResult.score">
                {{ gameResult.score }}
              </span>
            </div>
          </div>

          <div class="button-group">
            <button @click="playAgain" class="btn">
              🔄 Играть снова
            </button>
            <router-link to="/" class="btn btn-secondary">
              🏠 На главную
            </router-link>
          </div>
        </div>
        
        <!-- Yandex.RTB Реклама -->
        <Advertisement />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api'
import Advertisement from '@/components/Advertisement.vue'

export default {
  name: 'MathGame',
  components: {
    Advertisement
  },
  setup() {
    
    // Состояние игры
    const gameStarted = ref(false)
    const gameCompleted = ref(false)
    const gameSession = ref(null)
    const currentExampleIndex = ref(0)
    const selectedAnswer = ref(null)
    const timeLeft = ref(0)
    const timer = ref(null)
    
    // Определяем темную тему
    const isDarkTheme = ref(false)
    
    // Логотип
    const logoSrc = computed(() => {
      return isDarkTheme.value ? require('@/assets/logo_dark.png') : require('@/assets/logo.png')
    })
    
    // Проверяем тему при загрузке
    let themeObserver = null
    
    onMounted(() => {
      checkTheme()
      // Слушаем изменения темы
      themeObserver = observeThemeChanges()
    })
    
    // Очистка при размонтировании
    onUnmounted(() => {
      if (themeObserver) {
        themeObserver.disconnect()
      }
      if (timer.value) {
        clearInterval(timer.value)
      }
    })
    
    const checkTheme = () => {
      // Проверяем атрибут data-theme как в других компонентах
      isDarkTheme.value = document.documentElement.hasAttribute('data-theme')
      console.log('🎮 MathGame: Тема загружена, isDark =', isDarkTheme.value)
    }
    
    // Слушаем изменения темы через MutationObserver
    const observeThemeChanges = () => {
      const themeObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            checkTheme()
          }
        })
      })
      
      themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
      })
      
      return themeObserver
    }
    
    // Настройки игры
    const settings = ref({
      operations: ['addition', 'subtraction'],
      min_number: 1,
      max_number: 20,
      examples_count: 10,
      time_limit: null
    })
    
    // Результаты
    const gameResult = ref(null)
    
    // Вычисляемые свойства
    const canStartGame = computed(() => {
      return settings.value.operations.length > 0 && 
             settings.value.min_number < settings.value.max_number
    })
    
    const currentExample = computed(() => {
      if (!gameSession.value || !gameSession.value.examples || currentExampleIndex.value >= gameSession.value.examples.length) {
        return null
      }
      return gameSession.value.examples[currentExampleIndex.value]
    })
    
    const totalExamples = computed(() => {
      return gameSession.value ? gameSession.value.examples.length : 0
    })
    
    const progressPercentage = computed(() => {
      return totalExamples.value > 0 ? ((currentExampleIndex.value + 1) / totalExamples.value) * 100 : 0
    })
    
    // Методы
    const startGame = async () => {
      try {
        const response = await api.post('/api/math-game/start', settings.value)
        const data = await response.json()
        gameSession.value = data
        gameStarted.value = true
        currentExampleIndex.value = 0
        selectedAnswer.value = null
        
        // Запускаем таймер если установлен
        if (settings.value.time_limit) {
          startTimer()
        }
      } catch (error) {
        console.error('Ошибка при запуске игры:', error)
        alert('Не удалось запустить игру. Попробуйте еще раз.')
      }
    }
    
    const startTimer = () => {
      timeLeft.value = settings.value.time_limit
      timer.value = setInterval(() => {
        timeLeft.value--
        if (timeLeft.value <= 0) {
          clearInterval(timer.value)
          skipExample()
        }
      }, 1000)
    }
    
    const selectAnswer = (answer) => {
      selectedAnswer.value = answer
    }
    
    const submitAnswer = async () => {
      if (selectedAnswer.value === null || !gameSession.value) return
      
      try {
        const response = await api.post(`/api/math-game/answer/${gameSession.value.session_id}`, {
          answer: selectedAnswer.value
        })
        const data = await response.json()
        
        if (data.game_completed) {
          finishGame()
        } else {
          nextExample()
        }
      } catch (error) {
        console.error('Ошибка при отправке ответа:', error)
      }
    }
    
    const skipExample = async () => {
      if (!gameSession.value) return
      
      try {
        const response = await api.post(`/api/math-game/skip/${gameSession.value.session_id}`)
        const data = await response.json()
        
        if (data.game_completed) {
          finishGame()
        } else {
          nextExample()
        }
      } catch (error) {
        console.error('Ошибка при пропуске примера:', error)
      }
    }
    
    const nextExample = () => {
      currentExampleIndex.value++
      selectedAnswer.value = null
      
      // Перезапускаем таймер
      if (timer.value) {
        clearInterval(timer.value)
      }
      if (settings.value.time_limit) {
        startTimer()
      }
    }
    
    const finishGame = async () => {
      if (timer.value) {
        clearInterval(timer.value)
      }
      
      try {
        const response = await api.get(`/api/math-game/result/${gameSession.value.session_id}`)
        const data = await response.json()
        gameResult.value = data
        gameCompleted.value = true
        console.log('Результаты игры:', data)
      } catch (error) {
        console.error('Ошибка при получении результатов:', error)
        // Создаем базовый результат если API не работает
        gameResult.value = {
          total_examples: gameSession.value.examples.length,
          correct_answers: gameSession.value.correct_answers,
          score: Math.ceil((gameSession.value.correct_answers / gameSession.value.examples.length) * 5),
          time_spent: 0,
          percentage: (gameSession.value.correct_answers / gameSession.value.examples.length) * 100
        }
        gameCompleted.value = true
      }
    }
    
    const playAgain = () => {
      gameStarted.value = false
      gameCompleted.value = false
      gameSession.value = null
      currentExampleIndex.value = 0
      selectedAnswer.value = null
      if (timer.value) {
        clearInterval(timer.value)
      }
    }
    
    const formatTime = (seconds) => {
      if (seconds < 60) {
        return `${seconds}с`
      }
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}м ${remainingSeconds}с`
    }
    
    return {
      // Состояние
      gameStarted,
      gameCompleted,
      currentExampleIndex,
      selectedAnswer,
      timeLeft,
      settings,
      gameResult,
      
      // Вычисляемые свойства
      canStartGame,
      currentExample,
      totalExamples,
      progressPercentage,
      logoSrc,
      
      // Методы
      startGame,
      selectAnswer,
      submitAnswer,
      skipExample,
      playAgain,
      formatTime
    }
  }
}
</script>

<style scoped>
/* Используем стили как в других компонентах */
.page-container {
  overflow: hidden;
}

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 50vh;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

header h1 {
  font-size: 2.5rem;
  margin: 20px 0 10px 0;
  color: var(--text-primary);
}

header p {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin: 0;
}

main {
  width: 100%;
  max-width: 800px;
}

/* Настройки игры */
.game-settings {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px var(--shadow-color);
}

.game-settings h2 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 30px;
  font-size: 1.8rem;
}

form {
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input[type="number"] {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: var(--input-bg);
  color: var(--text-primary);
}

.form-group input[type="number"]:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(92, 107, 192, 0.1);
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 15px;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.3s ease;
  background: var(--bg-secondary);
}

.checkbox-item:hover {
  border-color: var(--accent-primary);
  background: var(--bg-container);
  transform: translateY(-2px);
}

.checkbox-item input[type="checkbox"] {
  margin-right: 10px;
  transform: scale(1.2);
}

.checkbox-item span {
  color: var(--text-primary);
  font-weight: 500;
}

/* Игровой процесс */
.game-play {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px var(--shadow-color);
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--bg-container);
  border-radius: 15px;
  border: 1px solid var(--border-color);
}

.progress {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  width: 200px;
  height: 10px;
  background: var(--border-color);
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-hover) 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-weight: 600;
  color: var(--text-primary);
}

.timer {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--error-color);
  padding: 10px 20px;
  background: var(--bg-container);
  border-radius: 10px;
  border: 2px solid var(--error-color);
}

.question-card {
  text-align: center;
}

.question {
  font-size: 3rem;
  color: var(--text-primary);
  margin-bottom: 40px;
  font-weight: 700;
}

.options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.option-btn {
  padding: 20px;
  font-size: 1.5rem;
  font-weight: 600;
  border: 3px solid var(--border-color);
  border-radius: 15px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-btn:hover {
  border-color: var(--accent-primary);
  background: var(--bg-container);
  transform: translateY(-2px);
}

.option-btn.selected {
  border-color: var(--accent-primary);
  background: var(--accent-primary);
  color: var(--button-text);
}

.game-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

/* Результаты */
.game-results {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px var(--shadow-color);
}

.game-results h2 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.results-card {
  max-width: 500px;
  margin: 0 auto 30px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid var(--border-color);
}

.result-item:last-child {
  border-bottom: none;
}

.result-item.score {
  font-size: 1.2rem;
  font-weight: 700;
  padding: 20px 0;
}

.label {
  color: var(--text-secondary);
  font-weight: 500;
}

.value {
  font-weight: 600;
  color: var(--text-primary);
}

.value.correct {
  color: var(--success-color);
}

.score-value {
  font-size: 2rem;
  padding: 10px 20px;
  border-radius: 10px;
}

.score-5 { background: rgba(76, 175, 80, 0.2); color: var(--success-color); }
.score-4 { background: rgba(33, 150, 243, 0.2); color: #2196f3; }
.score-3 { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
.score-2 { background: rgba(255, 87, 34, 0.2); color: #ff5722; }
.score-1 { background: rgba(244, 67, 54, 0.2); color: var(--error-color); }

/* Кнопки */
.button-group {
  margin-top: 30px;
  text-align: center;
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-block;
  padding: 15px 30px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  text-align: center;
  background: var(--accent-primary);
  color: var(--button-text);
}

.btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(92, 107, 192, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success {
  background: var(--success-color);
}

.btn-success:hover {
  background: #45a049;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-container);
}

/* Адаптивность */
@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  
  header h1 {
    font-size: 2rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .options {
    grid-template-columns: 1fr;
  }
  
  .game-actions {
    flex-direction: column;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .game-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .progress-bar {
    width: 150px;
  }
}
</style>

