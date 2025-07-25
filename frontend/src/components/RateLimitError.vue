<template>
  <div class="rate-limit-error">
    <div class="error-icon">⏱️</div>
    
    <div class="error-content">
      <h3>Лимит генерации исчерпан</h3>
      <p class="error-message">{{ error.error || 'Превышен лимит запросов' }}</p>
      
      <div v-if="!isAuthenticated && error.suggestion" class="suggestion-block">
        <div class="suggestion-icon">💡</div>
        <p class="suggestion-text">{{ error.suggestion }}</p>
        
        <div class="auth-buttons">
          <router-link to="/register" class="btn btn-primary">
            🚀 Зарегистрироваться
          </router-link>
          <router-link to="/login" class="btn btn-secondary">
            🔐 Войти
          </router-link>
        </div>
      </div>
      
      <div v-if="countdownSeconds > 0" class="countdown-block">
        <div class="countdown-timer">
          <div class="timer-circle">
            <span class="timer-number">{{ countdownSeconds }}</span>
          </div>
          <p class="timer-text">
            Следующая генерация доступна через <strong>{{ formatTime(countdownSeconds) }}</strong>
          </p>
        </div>
        
        <div class="countdown-progress">
          <div 
            class="progress-bar" 
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
      </div>
      
      <div v-if="error.details" class="details">
        <p class="usage-info">
          Использовано: {{ error.details.current_requests }}/{{ error.details.limit }} запросов
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RateLimitError',
  props: {
    error: {
      type: Object,
      required: true
    },
    isAuthenticated: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      countdownSeconds: 0,
      countdownInterval: null,
      initialSeconds: 0
    }
  },
  computed: {
    progressPercentage() {
      if (this.initialSeconds === 0) return 0
      return ((this.initialSeconds - this.countdownSeconds) / this.initialSeconds) * 100
    }
  },
  mounted() {
    this.startCountdown()
  },
  beforeUnmount() {
    this.stopCountdown()
  },
  methods: {
    startCountdown() {
      const seconds = this.error.details?.seconds_to_wait || this.error.details?.retry_after || 60
      this.countdownSeconds = seconds
      this.initialSeconds = seconds
      
      if (seconds > 0) {
        this.countdownInterval = setInterval(() => {
          this.countdownSeconds--
          
          if (this.countdownSeconds <= 0) {
            this.stopCountdown()
            this.$emit('countdown-finished')
          }
        }, 1000)
      }
    },
    
    stopCountdown() {
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval)
        this.countdownInterval = null
      }
    },
    
    formatTime(seconds) {
      if (seconds < 60) {
        return `${seconds} сек.`
      }
      
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      
      if (remainingSeconds === 0) {
        return `${minutes} мин.`
      }
      
      return `${minutes} мин. ${remainingSeconds} сек.`
    }
  }
}
</script>

<style scoped>
.rate-limit-error {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  border-radius: 12px;
  padding: 24px;
  margin: 20px 0;
  color: white;
  box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 48px;
  text-align: center;
  margin-bottom: 16px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.error-content h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  text-align: center;
  font-weight: 600;
}

.error-message {
  margin: 0 0 20px 0;
  font-size: 16px;
  text-align: center;
  opacity: 0.9;
}

.suggestion-block {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  backdrop-filter: blur(10px);
}

.suggestion-icon {
  font-size: 24px;
  text-align: center;
  margin-bottom: 8px;
}

.suggestion-text {
  margin: 0 0 16px 0;
  text-align: center;
  font-weight: 500;
}

.auth-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 140px;
  text-align: center;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
  transform: translateY(-2px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.countdown-block {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  text-align: center;
}

.countdown-timer {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
}

.timer-circle {
  width: 80px;
  height: 80px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.1);
}

.timer-number {
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.timer-text {
  margin: 0;
  font-size: 16px;
}

.countdown-progress {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  height: 8px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #81C784);
  border-radius: 10px;
  transition: width 1s ease;
}

.details {
  text-align: center;
  margin-top: 16px;
}

.usage-info {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

/* Адаптивность */
@media (max-width: 768px) {
  .rate-limit-error {
    padding: 16px;
    margin: 16px 0;
  }
  
  .auth-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 200px;
  }
  
  .timer-circle {
    width: 60px;
    height: 60px;
  }
  
  .timer-number {
    font-size: 18px;
  }
}
</style> 