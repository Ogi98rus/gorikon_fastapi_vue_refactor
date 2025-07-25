<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>📝 Регистрация</h2>
        <p>Создайте новый аккаунт для полного доступа</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <!-- Full Name -->
        <div class="form-group">
          <label for="fullName">👤 Полное имя</label>
          <input
            id="fullName"
            v-model="form.full_name"
            type="text"
            required
            :disabled="isLoading"
            placeholder="Иванов Иван Иванович"
            autocomplete="name"
          />
          <div v-if="errors.full_name" class="error-message">{{ errors.full_name }}</div>
        </div>

        <!-- Email -->
        <div class="form-group">
          <label for="email">📧 Электронная почта</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            :disabled="isLoading"
            placeholder="example@school.ru"
            autocomplete="email"
          />
          <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
        </div>

        <!-- School Name -->
        <div class="form-group">
          <label for="schoolName">🏫 Название школы (необязательно)</label>
          <input
            id="schoolName"
            v-model="form.school_name"
            type="text"
            :disabled="isLoading"
            placeholder="МБОУ СОШ №1"
            autocomplete="organization"
          />
          <div v-if="errors.school_name" class="error-message">{{ errors.school_name }}</div>
        </div>

        <!-- Password -->
        <div class="form-group">
          <label for="password">🔒 Пароль</label>
          <div class="password-input">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              :disabled="isLoading"
              placeholder="Минимум 8 символов"
              autocomplete="new-password"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
              :disabled="isLoading"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
          <div class="password-strength">
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :class="passwordStrengthClass"
                :style="{ width: passwordStrength + '%' }"
              ></div>
            </div>
            <small>{{ passwordStrengthText }}</small>
          </div>
        </div>

        <!-- Confirm Password -->
        <div class="form-group">
          <label for="confirmPassword">🔒 Подтвердите пароль</label>
          <div class="password-input">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              :disabled="isLoading"
              placeholder="Повторите пароль"
              autocomplete="new-password"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showConfirmPassword = !showConfirmPassword"
              :disabled="isLoading"
            >
              {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
        </div>

        <!-- Terms Agreement -->
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input
              v-model="form.agreeToTerms"
              type="checkbox"
              required
              :disabled="isLoading"
            />
            📄 Я согласен с <a href="/terms" target="_blank">условиями использования</a>
          </label>
          <div v-if="errors.agreeToTerms" class="error-message">{{ errors.agreeToTerms }}</div>
        </div>

        <!-- Error message -->
        <div v-if="registerError" class="alert alert-error">
          ❌ {{ registerError }}
        </div>

        <!-- Submit button -->
        <button
          type="submit"
          class="btn btn-primary btn-full"
          :disabled="isLoading || !isFormValid"
        >
          <span v-if="isLoading">⏳ Создание аккаунта...</span>
          <span v-else>🚀 Зарегистрироваться</span>
        </button>
      </form>

      <!-- Links -->
      <div class="auth-links">
        <p>
          Уже есть аккаунт?
          <router-link to="/login" class="link">Войти</router-link>
        </p>
      </div>

      <!-- Guest access -->
      <div class="guest-access">
        <p>или</p>
        <router-link to="/" class="btn btn-secondary">
          🏠 Продолжить как гость
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'RegisterForm',
  
  data() {
    return {
      form: {
        full_name: '',
        email: '',
        school_name: '',
        password: '',
        confirmPassword: '',
        agreeToTerms: false
      },
      showPassword: false,
      showConfirmPassword: false,
      errors: {}
    }
  },

  computed: {
    ...mapGetters('auth', ['isLoading', 'registerError']),
    
    isFormValid() {
      return (
        this.form.full_name &&
        this.form.email &&
        this.form.password &&
        this.form.confirmPassword &&
        this.form.agreeToTerms &&
        this.form.email.includes('@') &&
        this.form.password.length >= 8 &&
        this.form.password === this.form.confirmPassword &&
        this.form.full_name.length >= 2
      )
    },

    passwordStrength() {
      const password = this.form.password
      if (!password) return 0
      
      let strength = 0
      
      // Длина
      if (password.length >= 8) strength += 25
      if (password.length >= 12) strength += 15
      
      // Цифры
      if (/\d/.test(password)) strength += 20
      
      // Строчные буквы
      if (/[a-z]/.test(password)) strength += 15
      
      // Заглавные буквы
      if (/[A-Z]/.test(password)) strength += 15
      
      // Специальные символы
      if (/[^a-zA-Z0-9]/.test(password)) strength += 10
      
      return Math.min(strength, 100)
    },

    passwordStrengthClass() {
      if (this.passwordStrength < 30) return 'weak'
      if (this.passwordStrength < 60) return 'medium'
      if (this.passwordStrength < 80) return 'good'
      return 'strong'
    },

    passwordStrengthText() {
      if (!this.form.password) return ''
      if (this.passwordStrength < 30) return 'Слабый пароль'
      if (this.passwordStrength < 60) return 'Средний пароль'
      if (this.passwordStrength < 80) return 'Хороший пароль'
      return 'Отличный пароль'
    }
  },

  watch: {
    // Очищаем ошибки при изменении полей
    'form.full_name'() {
      if (this.errors.full_name) this.errors.full_name = null
    },
    'form.email'() {
      if (this.errors.email) this.errors.email = null
    },
    'form.password'() {
      if (this.errors.password) this.errors.password = null
      if (this.errors.confirmPassword && this.form.confirmPassword) {
        this.validatePasswordMatch()
      }
    },
    'form.confirmPassword'() {
      if (this.errors.confirmPassword) this.errors.confirmPassword = null
      if (this.form.password) {
        this.validatePasswordMatch()
      }
    }
  },

  mounted() {
    this.clearAuthErrors()
  },

  methods: {
    ...mapActions('auth', ['register', 'clearErrors']),

    async handleRegister() {
      // Очищаем предыдущие ошибки
      this.errors = {}
      this.clearAuthErrors()

      // Валидация формы
      if (!this.validateForm()) {
        return
      }

      try {
        const result = await this.register({
          full_name: this.form.full_name.trim(),
          email: this.form.email.trim(),
          password: this.form.password,
          school_name: this.form.school_name.trim() || undefined
        })

        if (result.success) {
          // Показываем уведомление об успехе
          this.$emit('register-success', result.user)
          
          // Перенаправляем на главную
          this.$router.push('/')
          
          // Показываем уведомление
          this.showNotification('Регистрация успешно завершена!', 'success')
        }
      } catch (error) {
        console.error('Register error:', error)
        this.showNotification('Ошибка регистрации', 'error')
      }
    },

    validateForm() {
      let isValid = true

      // Проверка имени
      if (!this.form.full_name) {
        this.errors.full_name = 'Введите полное имя'
        isValid = false
      } else if (this.form.full_name.trim().length < 2) {
        this.errors.full_name = 'Имя должно содержать минимум 2 символа'
        isValid = false
      }

      // Проверка email
      if (!this.form.email) {
        this.errors.email = 'Введите электронную почту'
        isValid = false
      } else if (!this.isValidEmail(this.form.email)) {
        this.errors.email = 'Введите корректный email'
        isValid = false
      }

      // Проверка пароля
      if (!this.form.password) {
        this.errors.password = 'Введите пароль'
        isValid = false
      } else if (this.form.password.length < 8) {
        this.errors.password = 'Пароль должен быть не менее 8 символов'
        isValid = false
      }

      // Проверка подтверждения пароля
      if (!this.form.confirmPassword) {
        this.errors.confirmPassword = 'Подтвердите пароль'
        isValid = false
      } else if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Пароли не совпадают'
        isValid = false
      }

      // Проверка согласия с условиями
      if (!this.form.agreeToTerms) {
        this.errors.agreeToTerms = 'Необходимо согласиться с условиями'
        isValid = false
      }

      return isValid
    },

    validatePasswordMatch() {
      if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Пароли не совпадают'
      } else {
        this.errors.confirmPassword = null
      }
    },

    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },

    clearAuthErrors() {
      this.clearErrors()
    },

    showNotification(message, type = 'info') {
      this.$emit('notification', { message, type })
    }
  }
}
</script>

<style scoped>
/* Используем те же стили что и в LoginForm, но добавляем специфичные для регистрации */
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-card {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px; /* Немного шире для регистрации */
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.password-strength {
  margin-top: 8px;
}

.strength-bar {
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-fill.weak {
  background: #f44336;
}

.strength-fill.medium {
  background: #ff9800;
}

.strength-fill.good {
  background: #2196f3;
}

.strength-fill.strong {
  background: #4caf50;
}

.password-strength small {
  color: var(--text-secondary);
  font-size: 12px;
}

/* Остальные стили наследуются от базовых компонентов */
.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: var(--text-primary);
  margin-bottom: 10px;
  font-size: 24px;
}

.auth-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: var(--input-bg);
  color: var(--text-primary);
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(92, 107, 192, 0.1);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.password-input {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary);
  font-size: 18px;
}

.password-toggle:hover {
  color: var(--accent-primary);
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  cursor: pointer;
  margin-bottom: 0 !important;
}

.checkbox-label input {
  width: auto !important;
  margin-right: 8px !important;
  margin-bottom: 0 !important;
}

.checkbox-label a {
  color: var(--accent-primary);
  text-decoration: none;
}

.checkbox-label a:hover {
  text-decoration: underline;
}

.error-message {
  color: var(--error-color);
  font-size: 12px;
  margin-top: 4px;
}

.alert {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.alert-error {
  background: rgba(244, 67, 54, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(244, 67, 54, 0.3);
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

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(92, 107, 192, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  background: transparent;
  color: var(--accent-primary);
  border: 2px solid var(--accent-primary);
}

.btn-secondary:hover {
  background: var(--accent-primary);
  color: white;
}

.btn-full {
  width: 100%;
}

.auth-links {
  text-align: center;
  margin-bottom: 20px;
}

.auth-links p {
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.link {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

.guest-access {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.guest-access p {
  margin-bottom: 15px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* Мобильная адаптация */
@media (max-width: 480px) {
  .auth-container {
    padding: 10px;
  }
  
  .auth-card {
    padding: 30px 20px;
  }
  
  .auth-header h2 {
    font-size: 20px;
  }
  
  .form-group input {
    font-size: 16px; /* Предотвращает zoom на iOS */
  }
}
</style> 