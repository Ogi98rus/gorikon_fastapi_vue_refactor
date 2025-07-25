<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>🔐 Вход в систему</h2>
        <p>Введите свои учетные данные для входа</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
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
              placeholder="Введите пароль"
              autocomplete="current-password"
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
        </div>

        <!-- Remember me -->
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input
              v-model="form.rememberMe"
              type="checkbox"
              :disabled="isLoading"
            />
            🔖 Запомнить меня
          </label>
        </div>

        <!-- Error message -->
        <div v-if="loginError" class="alert alert-error">
          ❌ {{ loginError }}
        </div>

        <!-- Submit button -->
        <button
          type="submit"
          class="btn btn-primary btn-full"
          :disabled="isLoading || !isFormValid"
        >
          <span v-if="isLoading">⏳ Выполняется вход...</span>
          <span v-else>🚀 Войти</span>
        </button>
      </form>

      <!-- Links -->
      <div class="auth-links">
        <p>
          Нет аккаунта?
          <router-link to="/register" class="link">Зарегистрироваться</router-link>
        </p>
        <router-link to="/forgot-password" class="link">Забыли пароль?</router-link>
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
  name: 'LoginForm',
  
  data() {
    return {
      form: {
        email: '',
        password: '',
        rememberMe: false
      },
      showPassword: false,
      errors: {}
    }
  },

  computed: {
    ...mapGetters('auth', ['isLoading', 'loginError']),
    
    isFormValid() {
      return (
        this.form.email &&
        this.form.password &&
        this.form.email.includes('@') &&
        this.form.password.length >= 6
      )
    }
  },

  watch: {
    // Очищаем ошибки при изменении полей
    'form.email'() {
      if (this.errors.email) {
        this.errors.email = null
      }
    },
    'form.password'() {
      if (this.errors.password) {
        this.errors.password = null
      }
    }
  },

  mounted() {
    // Очищаем ошибки при монтировании компонента
    this.clearAuthErrors()
    
    // Автофокус на поле email
    this.$nextTick(() => {
      const emailInput = this.$el.querySelector('#email')
      if (emailInput) {
        emailInput.focus()
      }
    })
  },

  methods: {
    ...mapActions('auth', ['login', 'clearErrors']),

    async handleLogin() {
      // Очищаем предыдущие ошибки
      this.errors = {}
      this.clearAuthErrors()

      // Валидация формы
      if (!this.validateForm()) {
        return
      }

      try {
        const result = await this.login({
          email: this.form.email.trim(),
          password: this.form.password
        })

        if (result.success) {
          // Показываем уведомление об успехе
          this.$emit('login-success', result.user)
          
          // Перенаправляем на главную или предыдущую страницу
          const redirectTo = this.$route.query.redirect || '/'
          this.$router.push(redirectTo)
          
          // Показываем уведомление
          this.showNotification('Добро пожаловать!', 'success')
        }
      } catch (error) {
        console.error('Login error:', error)
        this.showNotification('Ошибка входа в систему', 'error')
      }
    },

    validateForm() {
      let isValid = true

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
      } else if (this.form.password.length < 6) {
        this.errors.password = 'Пароль должен быть не менее 6 символов'
        isValid = false
      }

      return isValid
    },

    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },

    clearAuthErrors() {
      this.clearErrors()
    },

    showNotification(message, type = 'info') {
      // Эмитим событие для показа уведомления в родительском компоненте
      this.$emit('notification', { message, type })
    }
  }
}
</script>

<style scoped>
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
  max-width: 400px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

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