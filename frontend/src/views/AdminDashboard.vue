<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1>🛡️ Панель администратора</h1>
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-label">Всего пользователей:</span>
          <span class="stat-value">{{ systemStats.users?.total || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Активных:</span>
          <span class="stat-value active">{{ systemStats.users?.active || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Заблокированных:</span>
          <span class="stat-value banned">{{ systemStats.users?.banned || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Генераций:</span>
          <span class="stat-value">{{ systemStats.generations?.total || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Фильтры и поиск -->
    <div class="filters-section">
      <div class="search-box">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="🔍 Поиск по email или имени..."
          @input="debouncedSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="roleFilter" @change="loadUsers">
          <option value="">Все роли</option>
          <option value="user">👤 Пользователь</option>
          <option value="admin">👑 Администратор</option>
          <option value="moderator">🛡️ Модератор</option>
          <option value="banned">🚫 Заблокированный</option>
        </select>
        <select v-model="statusFilter" @change="loadUsers">
          <option value="">Все статусы</option>
          <option value="active">✅ Активный</option>
          <option value="inactive">⏸️ Неактивный</option>
          <option value="suspended">⏳ Приостановлен</option>
          <option value="banned">🚫 Заблокирован</option>
        </select>
      </div>
    </div>

    <!-- Список пользователей -->
    <div v-if="isLoading" class="loading">
      <div class="loader"></div>
      <p>Загрузка пользователей...</p>
    </div>

    <div v-else-if="users.length === 0" class="empty-state">
      <p>👥 Пользователи не найдены</p>
    </div>

    <div v-else class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пользователь</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Последний вход</th>
            <th>Генерации</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" :class="getUserRowClass(user)">
            <td>#{{ user.id }}</td>
            <td class="user-info">
              <div class="user-details">
                <div class="user-name">{{ user.full_name }}</div>
                <div class="user-email">{{ user.email }}</div>
                <div v-if="user.school_name" class="user-school">{{ user.school_name }}</div>
              </div>
            </td>
            <td>
              <span :class="['role-badge', user.role]">
                {{ getRoleLabel(user.role) }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', user.status]">
                {{ getStatusLabel(user.status) }}
              </span>
              <div v-if="user.banned_until" class="ban-info">
                До: {{ formatDate(user.banned_until) }}
              </div>
            </td>
            <td>
              <span v-if="user.last_login">{{ formatDate(user.last_login) }}</span>
              <span v-else class="text-muted">Никогда</span>
            </td>
            <td class="stats-cell">
              <button @click="showUserProfile(user.id)" class="btn-link">
                📊 Статистика
              </button>
            </td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button 
                  @click="editUser(user)" 
                  class="btn btn-sm btn-secondary"
                  :disabled="user.id === currentUser.id"
                >
                  ✏️
                </button>
                <button 
                  v-if="user.status !== 'banned'"
                  @click="banUser(user)" 
                  class="btn btn-sm btn-danger"
                  :disabled="user.id === currentUser.id"
                >
                  🚫
                </button>
                <button 
                  v-else
                  @click="unbanUser(user)" 
                  class="btn btn-sm btn-success"
                >
                  ✅
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагинация -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary"
      >
        ← Назад
      </button>
      <span class="page-info">
        Страница {{ currentPage }} из {{ totalPages }}
      </span>
      <button 
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary"
      >
        Вперед →
      </button>
    </div>

    <!-- Модальное окно редактирования пользователя -->
    <div v-if="selectedUser" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <h3>Редактирование пользователя</h3>
        <form @submit.prevent="saveUser">
          <div class="form-group">
            <label>Полное имя:</label>
            <input v-model="editForm.full_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Школа:</label>
            <input v-model="editForm.school_name" type="text" />
          </div>
          <div class="form-group">
            <label>Роль:</label>
            <select v-model="editForm.role">
              <option value="user">👤 Пользователь</option>
              <option value="admin">👑 Администратор</option>
              <option value="moderator">🛡️ Модератор</option>
            </select>
          </div>
          <div class="form-group">
            <label>Статус:</label>
            <select v-model="editForm.status">
              <option value="active">✅ Активный</option>
              <option value="inactive">⏸️ Неактивный</option>
              <option value="suspended">⏳ Приостановлен</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeEditModal" class="btn btn-secondary">
              Отмена
            </button>
            <button type="submit" class="btn btn-primary">
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно блокировки -->
    <div v-if="showBanModal" class="modal-overlay" @click="closeBanModal">
      <div class="modal-content" @click.stop>
        <h3>Блокировка пользователя</h3>
        <p>Пользователь: <strong>{{ userToBan?.full_name }}</strong></p>
        <form @submit.prevent="confirmBan">
          <div class="form-group">
            <label>Причина блокировки:</label>
            <textarea v-model="banForm.reason" required rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>
              <input v-model="banForm.permanent" type="checkbox" />
              Постоянная блокировка
            </label>
          </div>
          <div v-if="!banForm.permanent" class="form-group">
            <label>Длительность (часов):</label>
            <input v-model.number="banForm.duration" type="number" min="1" max="8760" />
          </div>
          <div class="form-actions">
            <button type="button" @click="closeBanModal" class="btn btn-secondary">
              Отмена
            </button>
            <button type="submit" class="btn btn-danger">
              🚫 Заблокировать
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно профиля пользователя -->
    <div v-if="showProfileModal" class="modal-overlay" @click="closeProfileModal">
      <div class="modal-content large" @click.stop>
        <h3>Профиль пользователя</h3>
        <div v-if="userProfile" class="user-profile">
          <div class="profile-section">
            <h4>Основная информация</h4>
            <div class="profile-grid">
              <div><strong>ID:</strong> {{ userProfile.user.id }}</div>
              <div><strong>Email:</strong> {{ userProfile.user.email }}</div>
              <div><strong>Имя:</strong> {{ userProfile.user.full_name }}</div>
              <div><strong>Школа:</strong> {{ userProfile.user.school_name || 'Не указана' }}</div>
              <div><strong>Роль:</strong> {{ getRoleLabel(userProfile.user.role) }}</div>
              <div><strong>Статус:</strong> {{ getStatusLabel(userProfile.user.status) }}</div>
            </div>
          </div>
          <div class="profile-section">
            <h4>Статистика</h4>
            <div class="stats-grid">
              <div class="stat-box">
                <div class="stat-number">{{ userProfile.statistics.total_generations }}</div>
                <div class="stat-label">Всего генераций</div>
              </div>
              <div class="stat-box">
                <div class="stat-number">{{ userProfile.statistics.math_generations }}</div>
                <div class="stat-label">Мат. примеры</div>
              </div>
              <div class="stat-box">
                <div class="stat-number">{{ userProfile.statistics.ktp_generations }}</div>
                <div class="stat-label">КТП</div>
              </div>
              <div class="stat-box">
                <div class="stat-number">{{ userProfile.statistics.total_downloads }}</div>
                <div class="stat-label">Скачиваний</div>
              </div>
            </div>
          </div>
          <div class="profile-section">
            <h4>Последние генерации</h4>
            <div v-if="userProfile.recent_generations.length > 0" class="recent-generations">
              <div v-for="gen in userProfile.recent_generations" :key="gen.id" class="generation-item">
                <span class="gen-type">{{ gen.generator_type === 'math' ? '🧮' : '📅' }}</span>
                <span class="gen-name">{{ gen.file_name }}</span>
                <span class="gen-date">{{ formatDate(gen.created_at) }}</span>
                <span class="gen-downloads">{{ gen.download_count }} скачиваний</span>
              </div>
            </div>
            <div v-else class="no-generations">
              Генераций пока нет
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button @click="closeProfileModal" class="btn btn-secondary">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import axios from 'axios'

export default {
  name: 'AdminDashboard',

  data() {
    return {
      users: [],
      systemStats: {},
      isLoading: false,
      searchQuery: '',
      roleFilter: '',
      statusFilter: '',
      currentPage: 1,
      perPage: 20,
      totalCount: 0,
      searchTimeout: null,

      // Модальные окна
      selectedUser: null,
      showBanModal: false,
      userToBan: null,
      showProfileModal: false,
      userProfile: null,

      // Формы
      editForm: {
        full_name: '',
        school_name: '',
        role: '',
        status: ''
      },
      banForm: {
        reason: '',
        permanent: false,
        duration: 24
      }
    }
  },

  computed: {
    ...mapGetters('auth', ['currentUser', 'isAdmin']),
    
    totalPages() {
      return Math.ceil(this.totalCount / this.perPage)
    }
  },

  async mounted() {
    if (!this.isAdmin) {
      this.$router.push('/')
      return
    }

    await this.loadSystemStats()
    await this.loadUsers()
  },

  methods: {
    async loadSystemStats() {
      try {
        const response = await axios.get('/api/admin/stats')
        this.systemStats = response.data
      } catch (error) {
        console.error('Ошибка загрузки статистики:', error)
      }
    },

    async loadUsers() {
      this.isLoading = true
      try {
        const params = {
          page: this.currentPage,
          per_page: this.perPage
        }
        
        if (this.searchQuery) params.search = this.searchQuery
        if (this.roleFilter) params.role = this.roleFilter
        if (this.statusFilter) params.status = this.statusFilter

        const response = await axios.get('/api/admin/users', { params })
        this.users = response.data.users
        this.totalCount = response.data.total_count
      } catch (error) {
        console.error('Ошибка загрузки пользователей:', error)
        this.showNotification('Ошибка загрузки пользователей', 'error')
      } finally {
        this.isLoading = false
      }
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.loadUsers()
      }, 500)
    },

    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadUsers()
      }
    },

    editUser(user) {
      this.selectedUser = user
      this.editForm = {
        full_name: user.full_name,
        school_name: user.school_name || '',
        role: user.role,
        status: user.status
      }
    },

    async saveUser() {
      try {
        await axios.put(`/api/admin/users/${this.selectedUser.id}`, this.editForm)
        this.showNotification('Пользователь успешно обновлен', 'success')
        this.closeEditModal()
        await this.loadUsers()
      } catch (error) {
        console.error('Ошибка сохранения пользователя:', error)
        this.showNotification('Ошибка сохранения пользователя', 'error')
      }
    },

    banUser(user) {
      this.userToBan = user
      this.showBanModal = true
      this.banForm = {
        reason: '',
        permanent: false,
        duration: 24
      }
    },

    async confirmBan() {
      try {
        const data = {
          ban_reason: this.banForm.reason,
          permanent: this.banForm.permanent
        }
        
        if (!this.banForm.permanent) {
          data.ban_duration_hours = this.banForm.duration
        }

        await axios.post(`/api/admin/users/${this.userToBan.id}/ban`, data)
        this.showNotification('Пользователь заблокирован', 'success')
        this.closeBanModal()
        await this.loadUsers()
      } catch (error) {
        console.error('Ошибка блокировки пользователя:', error)
        this.showNotification('Ошибка блокировки пользователя', 'error')
      }
    },

    async unbanUser(user) {
      try {
        await axios.post(`/api/admin/users/${user.id}/unban`, {
          reason: 'Разблокировка администратором'
        })
        this.showNotification('Пользователь разблокирован', 'success')
        await this.loadUsers()
      } catch (error) {
        console.error('Ошибка разблокировки пользователя:', error)
        this.showNotification('Ошибка разблокировки пользователя', 'error')
      }
    },

    async showUserProfile(userId) {
      try {
        const response = await axios.get(`/api/admin/users/${userId}/profile`)
        this.userProfile = response.data
        this.showProfileModal = true
      } catch (error) {
        console.error('Ошибка загрузки профиля:', error)
        this.showNotification('Ошибка загрузки профиля', 'error')
      }
    },

    closeEditModal() {
      this.selectedUser = null
    },

    closeBanModal() {
      this.showBanModal = false
      this.userToBan = null
    },

    closeProfileModal() {
      this.showProfileModal = false
      this.userProfile = null
    },

    getUserRowClass(user) {
      return {
        'user-banned': user.status === 'banned',
        'user-inactive': user.status === 'inactive',
        'user-admin': user.role === 'admin'
      }
    },

    getRoleLabel(role) {
      const roles = {
        user: '👤 Пользователь',
        admin: '👑 Администратор',
        moderator: '🛡️ Модератор',
        banned: '🚫 Заблокированный'
      }
      return roles[role] || role
    },

    getStatusLabel(status) {
      const statuses = {
        active: '✅ Активный',
        inactive: '⏸️ Неактивный',
        suspended: '⏳ Приостановлен',
        banned: '🚫 Заблокирован'
      }
      return statuses[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return 'Неизвестно'
      return new Date(dateString).toLocaleString('ru-RU')
    },

    showNotification(message, type = 'info') {
      // Реализация уведомлений (может быть через toast library)
      console.log(`${type.toUpperCase()}: ${message}`)
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.stats-bar {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-width: 150px;
}

.stat-label {
  display: block;
  color: #666;
  font-size: 0.9em;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 1.5em;
  font-weight: bold;
  color: #2c3e50;
}

.stat-value.active {
  color: #27ae60;
}

.stat-value.banned {
  color: #e74c3c;
}

.filters-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
}

.search-box input {
  width: 300px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filter-group {
  display: flex;
  gap: 10px;
}

.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: 50px;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.users-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f8f9fa;
  padding: 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.users-table td {
  padding: 15px;
  border-bottom: 1px solid #dee2e6;
}

.user-info {
  min-width: 200px;
}

.user-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.user-email {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 2px;
}

.user-school {
  color: #888;
  font-size: 0.8em;
}

.role-badge, .status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
}

.role-badge.user {
  background: #e3f2fd;
  color: #1976d2;
}

.role-badge.admin {
  background: #fff3e0;
  color: #f57c00;
}

.role-badge.moderator {
  background: #f3e5f5;
  color: #7b1fa2;
}

.role-badge.banned {
  background: #ffebee;
  color: #c62828;
}

.status-badge.active {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #f5f5f5;
  color: #616161;
}

.status-badge.suspended {
  background: #fff8e1;
  color: #f57f17;
}

.status-badge.banned {
  background: #ffebee;
  color: #c62828;
}

.ban-info {
  font-size: 0.8em;
  color: #e74c3c;
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  font-size: 0.9em;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.8em;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-link {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  text-decoration: underline;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.page-info {
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 800px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.profile-section {
  margin-bottom: 30px;
}

.profile-section h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 8px;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.stat-box {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #2c3e50;
}

.recent-generations {
  max-height: 200px;
  overflow-y: auto;
}

.generation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.gen-type {
  font-size: 1.2em;
}

.gen-name {
  flex: 1;
  font-weight: 500;
}

.gen-date {
  color: #666;
  font-size: 0.9em;
}

.gen-downloads {
  color: #28a745;
  font-size: 0.9em;
}

.user-banned {
  background-color: #fff5f5;
}

.user-inactive {
  opacity: 0.6;
}

.user-admin {
  background-color: #fef9e7;
}

.empty-state {
  text-align: center;
  padding: 50px;
  color: #666;
}

@media (max-width: 768px) {
  .stats-bar {
    flex-direction: column;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .users-table {
    font-size: 0.9em;
  }
  
  .users-table th,
  .users-table td {
    padding: 10px;
  }
}
</style> 