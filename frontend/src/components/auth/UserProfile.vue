<template>
  <div class="profile-container">
    <!-- Profile Header -->
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar">
          {{ avatarInitials }}
        </div>
        <div class="user-info">
          <h2>{{ user?.full_name || 'Пользователь' }}</h2>
          <p class="email">{{ user?.email }}</p>
          <p class="school" v-if="user?.school_name">🏫 {{ user.school_name }}</p>
          <span class="user-status" :class="{ 'admin': isAdmin }">
            {{ isAdmin ? '👑 Администратор' : '👤 Пользователь' }}
          </span>
        </div>
      </div>
      
      <div class="profile-actions">
        <router-link to="/history" class="btn btn-primary">
          📊 История генераций
        </router-link>
        <button @click="toggleEditMode" class="btn btn-secondary">
          {{ isEditing ? '❌ Отменить' : '✏️ Редактировать' }}
        </button>
        <button @click="handleLogout" class="btn btn-outline">
          🚪 Выйти
        </button>
      </div>
    </div>

    <!-- Edit Profile Form -->
    <div v-if="isEditing" class="edit-section">
      <h3>📝 Редактирование профиля</h3>
      
      <form @submit.prevent="handleUpdateProfile" class="edit-form">
        <div class="form-row">
          <div class="form-group">
            <label>👤 Полное имя</label>
            <input
              v-model="editForm.full_name"
              type="text"
              required
              :disabled="isLoading"
              placeholder="Введите полное имя"
            />
            <div v-if="errors.full_name" class="error-message">{{ errors.full_name }}</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>📧 Email</label>
            <input
              v-model="editForm.email"
              type="email"
              required
              :disabled="isLoading"
              placeholder="Введите email"
            />
            <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>🏫 Название школы</label>
            <input
              v-model="editForm.school_name"
              type="text"
              :disabled="isLoading"
              placeholder="Введите название школы (необязательно)"
            />
            <div v-if="errors.school_name" class="error-message">{{ errors.school_name }}</div>
          </div>
        </div>

        <!-- Password Change Section -->
        <div class="password-section">
          <div class="section-header">
            <h4>🔒 Изменение пароля</h4>
            <small>Оставьте пустым, если не хотите менять пароль</small>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>🔒 Новый пароль</label>
              <div class="password-input">
                <input
                  v-model="editForm.new_password"
                  :type="showNewPassword ? 'text' : 'password'"
                  :disabled="isLoading"
                  placeholder="Минимум 8 символов"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showNewPassword = !showNewPassword"
                >
                  {{ showNewPassword ? '👁️' : '👁️‍🗨️' }}
                </button>
              </div>
              <div v-if="errors.new_password" class="error-message">{{ errors.new_password }}</div>
            </div>
          </div>

          <div class="form-row" v-if="editForm.new_password">
            <div class="form-group">
              <label>🔒 Подтвердите новый пароль</label>
              <div class="password-input">
                <input
                  v-model="editForm.confirm_password"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  :disabled="isLoading"
                  placeholder="Повторите новый пароль"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
                </button>
              </div>
              <div v-if="errors.confirm_password" class="error-message">{{ errors.confirm_password }}</div>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="isLoading || !isFormValid"
          >
            <span v-if="isLoading">⏳ Сохранение...</span>
            <span v-else>💾 Сохранить изменения</span>
          </button>
          <button
            type="button"
            @click="cancelEdit"
            class="btn btn-secondary"
            :disabled="isLoading"
          >
            ❌ Отменить
          </button>
        </div>
      </form>
    </div>

    <!-- Profile Statistics -->
    <div class="stats-section">
      <div class="stats-header">
      <h3>📊 Статистика активности</h3>
        <router-link to="/history" class="view-all-link">
          📋 Посмотреть всю историю →
        </router-link>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <h4>Всего генераций</h4>
            <p class="stat-value">{{ stats.total_generations || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🧮</div>
          <div class="stat-info">
            <h4>Математические задачи</h4>
            <p class="stat-value">{{ stats.math_generations || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-info">
            <h4>КТП планы</h4>
            <p class="stat-value">{{ stats.ktp_generations || 0 }}</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <h4>За последний месяц</h4>
            <p class="stat-value">{{ stats.recent_generations || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Generations -->
    <div class="recent-section">
      <div class="recent-header">
        <h3>📁 Последние генерации</h3>
        <router-link to="/history" class="view-all-link">
          📋 Посмотреть все →
        </router-link>
      </div>
      
      <div v-if="recentGenerations.length > 0" class="recent-list">
        <div
          v-for="item in recentGenerations.slice(0, 5)" 
          :key="item.id"
          class="recent-item"
        >
          <div class="recent-icon">
            {{ item.generator_type === 'math' ? '🧮' : '📅' }}
          </div>
          <div class="recent-info">
            <div class="recent-name">{{ item.original_file_name }}</div>
            <div class="recent-meta">
              {{ formatDate(item.created_at) }} • {{ formatFileSize(item.file_size) }}
          </div>
          </div>
          <div class="recent-actions">
            <router-link 
              :to="`/history?highlight=${item.id}`" 
              class="btn btn-sm btn-secondary"
            >
              👁️ Открыть
            </router-link>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-recent">
        <p>📭 Пока нет сохраненных генераций</p>
        <div class="empty-actions">
          <router-link to="/math" class="btn btn-primary">
            🧮 Создать математические задачи
          </router-link>
          <router-link to="/ktp" class="btn btn-primary">
            📅 Создать КТП
        </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import axios from 'axios'

export default {
  name: 'UserProfile',
  
  data() {
    return {
      isEditing: false,
      isLoading: false,
      showNewPassword: false,
      showConfirmPassword: false,
      
      editForm: {
        full_name: '',
        email: '',
        school_name: '',
        new_password: '',
        confirm_password: ''
      },
      
      errors: {},
      stats: {}
    }
  },

  computed: {
    ...mapGetters('auth', ['user', 'isAuthenticated', 'isAdmin']),
    ...mapGetters('history', ['recentGenerations']),
    
    avatarInitials() {
      if (!this.user?.full_name) return '👤'
      return this.user.full_name
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase()
    },

    isFormValid() {
      if (!this.editForm.full_name || !this.editForm.email) {
        return false
      }
      
      if (this.editForm.new_password) {
        return (
          this.editForm.new_password.length >= 8 &&
          this.editForm.new_password === this.editForm.confirm_password
        )
      }
      
      return true
    }
  },

  async mounted() {
    if (!this.isAuthenticated) {
      this.$router.push('/login')
      return
    }
    
    await this.loadProfileData()
  },

  methods: {
    ...mapActions('auth', ['logout']),
    ...mapActions('history', ['fetchProfile', 'fetchGenerations']),

    async loadProfileData() {
      try {
        this.isLoading = true
        
        // Загружаем профиль с расширенной статистикой
        const profileData = await this.fetchProfile()
        this.stats = {
          total_generations: profileData.total_generations,
          math_generations: profileData.math_generations,
          ktp_generations: profileData.ktp_generations,
          recent_generations: profileData.math_generations + profileData.ktp_generations
        }
        
        // Загружаем последние генерации для отображения
        await this.fetchGenerations({ page: 1, per_page: 5 })
        
      } catch (error) {
        console.error('Failed to load profile data:', error)
        this.showNotification('Ошибка загрузки данных профиля', 'error')
      } finally {
        this.isLoading = false
      }
    },

    toggleEditMode() {
      if (this.isEditing) {
        this.cancelEdit()
      } else {
        this.startEdit()
      }
    },

    startEdit() {
      this.isEditing = true
      this.editForm = {
        full_name: this.user?.full_name || '',
        email: this.user?.email || '',
        school_name: this.user?.school_name || '',
        new_password: '',
        confirm_password: ''
      }
      this.errors = {}
    },

    cancelEdit() {
      this.isEditing = false
      this.editForm = {
        full_name: '',
        email: '',
        school_name: '',
        new_password: '',
        confirm_password: ''
      }
      this.errors = {}
      this.showNewPassword = false
      this.showConfirmPassword = false
    },

    async handleUpdateProfile() {
      this.errors = {}
      
      if (!this.validateForm()) {
        return
      }

      try {
        this.isLoading = true
        
        const updateData = {
          full_name: this.editForm.full_name.trim(),
          email: this.editForm.email.trim(),
          school_name: this.editForm.school_name.trim() || null
        }
        
        if (this.editForm.new_password) {
          updateData.password = this.editForm.new_password
        }
        
        const response = await axios.patch('/api/auth/profile', updateData)
        
        // Обновляем данные пользователя в store
        this.$store.commit('auth/SET_USER', response.data)
        
        this.showNotification('Профиль успешно обновлен!', 'success')
        this.cancelEdit()
        
      } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Ошибка обновления профиля'
        this.showNotification(errorMessage, 'error')
      } finally {
        this.isLoading = false
      }
    },

    validateForm() {
      let isValid = true

      if (!this.editForm.full_name.trim()) {
        this.errors.full_name = 'Введите полное имя'
        isValid = false
      }

      if (!this.editForm.email.trim()) {
        this.errors.email = 'Введите email'
        isValid = false
      } else if (!this.isValidEmail(this.editForm.email)) {
        this.errors.email = 'Введите корректный email'
        isValid = false
      }

      if (this.editForm.new_password) {
        if (this.editForm.new_password.length < 8) {
          this.errors.new_password = 'Пароль должен быть не менее 8 символов'
          isValid = false
        }
        
        if (this.editForm.new_password !== this.editForm.confirm_password) {
          this.errors.confirm_password = 'Пароли не совпадают'
          isValid = false
        }
      }

      return isValid
    },

    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },

    async handleLogout() {
      try {
        await this.logout()
        this.$router.push('/login')
        this.showNotification('Вы успешно вышли из системы', 'info')
      } catch (error) {
        console.error('Logout error:', error)
      }
    },

    getActivityTitle(activity) {
      return activity.type === 'math' 
        ? 'Математические задачи' 
        : 'КТП планирование'
    },

    getActivityDescription(activity) {
      if (activity.type === 'math') {
        const params = activity.parameters
        return `${params.example_count || 'N/A'} примеров, операции: ${(params.operations || []).join(', ')}`
      } else {
        const params = activity.parameters
        const startDate = params.start_date ? new Date(params.start_date).toLocaleDateString() : 'N/A'
        const endDate = params.end_date ? new Date(params.end_date).toLocaleDateString() : 'N/A'
        return `Период: ${startDate} - ${endDate}`
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Б'
      const k = 1024
      const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    showNotification(message, type = 'info') {
      this.$emit('notification', { message, type })
    }
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.user-info h2 {
  margin: 0 0 5px 0;
  color: var(--text-primary);
}

.user-info .email {
  color: var(--text-secondary);
  margin: 0 0 5px 0;
}

.user-info .school {
  color: var(--text-secondary);
  margin: 0 0 10px 0;
  font-size: 14px;
}

.user-status {
  background: var(--accent-light);
  color: var(--accent-primary);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.user-status.admin {
  background: #ffd700;
  color: #8b6914;
}

.profile-actions {
  display: flex;
  gap: 10px;
}

.edit-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
}

.edit-section h3 {
  margin: 0 0 25px 0;
  color: var(--text-primary);
}

.edit-form {
  max-width: 600px;
}

.form-row {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
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

.password-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.section-header {
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0 0 5px 0;
  color: var(--text-primary);
}

.section-header small {
  color: var(--text-secondary);
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
  color: var(--text-secondary);
  font-size: 18px;
}

.error-message {
  color: var(--error-color);
  font-size: 12px;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.stats-section,
.activity-section {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
}

.stats-section h3,
.activity-section h3 {
  margin: 0 0 25px 0;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid var(--border-color);
}

.stat-icon {
  font-size: 24px;
  padding: 12px;
  background: var(--accent-light);
  border-radius: 8px;
}

.stat-info h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: var(--accent-primary);
}

.activity-list {
  space-y: 15px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 15px;
}

.activity-icon {
  font-size: 20px;
  padding: 10px;
  background: var(--accent-light);
  border-radius: 8px;
}

.activity-info {
  flex: 1;
}

.activity-info h4 {
  margin: 0 0 5px 0;
  color: var(--text-primary);
  font-size: 16px;
}

.activity-info p {
  margin: 0 0 5px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.activity-info small {
  color: var(--text-muted);
  font-size: 12px;
}

.activity-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.2s;
  font-size: 16px;
}

.btn-icon:hover {
  background: var(--hover-bg);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
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

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-outline {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Мобильная адаптация */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-actions {
    align-self: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .activity-actions {
    align-self: stretch;
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

.stats-header,
.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-header h3,
.recent-header h3 {
  margin: 0;
}

.view-all-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}

.view-all-link:hover {
  opacity: 0.8;
}

/* Recent generations styles */
.recent-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: var(--bg-primary);
  border-radius: 8px;
  transition: transform 0.2s;
}

.recent-item:hover {
  transform: translateY(-1px);
}

.recent-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.recent-info {
  flex: 1;
}

.recent-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.recent-meta {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.recent-actions {
  flex-shrink: 0;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.empty-recent {
  text-align: center;
  padding: 40px 20px;
}

.empty-recent p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.empty-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Адаптивность для новых элементов */
@media (max-width: 768px) {
  .stats-header,
  .recent-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .recent-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .recent-actions {
    width: 100%;
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .profile-actions {
    flex-direction: column;
    width: 100%;
  }
}
</style> 