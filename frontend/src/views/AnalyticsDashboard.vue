<template>
  <div class="analytics-dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1>📊 Аналитика и статистика</h1>
        <p>Подробная информация об использовании генераторов</p>
      </div>
      
      <!-- Filters -->
      <div class="dashboard-filters">
        <div class="filter-group">
          <label>📅 Период:</label>
          <select v-model="selectedDateRange" @change="updateFilters">
            <option value="day">Сегодня</option>
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
            <option value="year">Год</option>
            <option value="custom">Пользовательский</option>
          </select>
        </div>
        
        <div v-if="selectedDateRange === 'custom'" class="filter-group custom-dates">
          <input
            type="date"
            v-model="customStartDate"
            @change="updateFilters"
            placeholder="Дата начала"
          />
          <span>—</span>
          <input
            type="date"
            v-model="customEndDate"
            @change="updateFilters"
            placeholder="Дата окончания"
          />
        </div>
        
        <div class="filter-group">
          <label>🧮 Тип:</label>
          <select v-model="selectedGenerationType" @change="updateFilters">
            <option value="all">Все</option>
            <option value="math">Математика</option>
            <option value="ktp">КТП</option>
          </select>
        </div>
        
        <button @click="resetFilters" class="btn btn-outline">
          🔄 Сбросить
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка аналитики...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="hasError" class="error-state">
      <div class="error-icon">❌</div>
      <h3>Ошибка загрузки данных</h3>
      <p>{{ error }}</p>
      <button @click="retryLoad" class="btn btn-primary">
        🔄 Попробовать снова
      </button>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Stats Overview -->
      <div class="stats-overview">
        <div class="stat-card total">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <h3>Всего генераций</h3>
            <p class="stat-value">{{ userTotalGenerations }}</p>
            <span class="stat-growth" :class="{ positive: generationsGrowth > 0 }">
              {{ generationsGrowth > 0 ? '+' : '' }}{{ generationsGrowth }}% за период
            </span>
          </div>
        </div>

        <div class="stat-card math">
          <div class="stat-icon">🧮</div>
          <div class="stat-info">
            <h3>Математические задачи</h3>
            <p class="stat-value">{{ userMathGenerations }}</p>
            <span class="stat-percentage">
              {{ mathPercentage }}% от общего
            </span>
          </div>
        </div>

        <div class="stat-card ktp">
          <div class="stat-icon">📅</div>
          <div class="stat-info">
            <h3>КТП планы</h3>
            <p class="stat-value">{{ userKtpGenerations }}</p>
            <span class="stat-percentage">
              {{ ktpPercentage }}% от общего
            </span>
          </div>
        </div>

        <div class="stat-card recent">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <h3>За последний месяц</h3>
            <p class="stat-value">{{ userRecentGenerations }}</p>
            <span class="stat-average">
              {{ averagePerDay }} в среднем в день
            </span>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-card">
          <h3>📈 Активность по дням</h3>
          <div class="chart-placeholder">
            <div class="simple-chart">
              <div
                v-for="(day, index) in dailyStats"
                :key="index"
                class="chart-bar"
                :style="{ height: getBarHeight(day.count) + '%' }"
                :title="`${day.date}: ${day.count} генераций`"
              >
                <span class="bar-value">{{ day.count }}</span>
              </div>
            </div>
            <div class="chart-labels">
              <span
                v-for="(day, index) in dailyStats"
                :key="index"
                class="chart-label"
              >
                {{ formatChartDate(day.date) }}
              </span>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3>🎯 Популярные параметры</h3>
          <div class="popular-params">
            <div
              v-for="param in popularParams"
              :key="param.name"
              class="param-item"
            >
              <div class="param-info">
                <span class="param-name">{{ param.name }}</span>
                <span class="param-count">{{ param.count }} раз</span>
              </div>
              <div class="param-bar">
                <div
                  class="param-fill"
                  :style="{ width: getParamWidth(param.count) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="activity-section">
        <div class="section-header">
          <h3>📝 Последняя активность</h3>
          <router-link to="/profile" class="view-all-link">
            Смотреть все →
          </router-link>
        </div>
        
        <div v-if="hasActivity" class="activity-list">
          <div
            v-for="activity in recentActivity"
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon">
              {{ activity.type === 'math' ? '🧮' : '📅' }}
            </div>
            <div class="activity-info">
              <h4>{{ getActivityTitle(activity) }}</h4>
              <p>{{ getActivityDescription(activity) }}</p>
              <small>{{ formatDateTime(activity.created_at) }}</small>
            </div>
            <div class="activity-actions">
              <button
                @click="downloadActivity(activity)"
                class="btn-icon"
                title="Скачать"
              >
                📥
              </button>
              <button
                @click="repeatActivity(activity)"
                class="btn-icon"
                title="Повторить"
              >
                🔄
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-activity">
          <p>📭 Пока нет активности</p>
          <router-link to="/" class="btn btn-primary">
            🚀 Создать первую генерацию
          </router-link>
        </div>
      </div>

      <!-- Admin Section (if admin) -->
      <div v-if="isAdmin" class="admin-section">
        <h3>👑 Административная панель</h3>
        
        <div class="admin-stats">
          <div class="admin-stat-card">
            <h4>👥 Пользователи</h4>
            <p class="admin-value">{{ totalUsers }}</p>
            <small>{{ activeUsersToday }} активных сегодня</small>
          </div>
          
          <div class="admin-stat-card">
            <h4>📊 Общие генерации</h4>
            <p class="admin-value">{{ totalGenerations }}</p>
            <small>{{ mathGenerations }} математика, {{ ktpGenerations }} КТП</small>
          </div>
          
          <div class="admin-stat-card">
            <h4>⚡ Производительность</h4>
            <p class="admin-value">{{ systemStats.average_response_time }}мс</p>
            <small>{{ systemStats.error_rate }}% ошибок</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'AnalyticsDashboard',
  
  data() {
    return {
      selectedDateRange: 'week',
      selectedGenerationType: 'all',
      customStartDate: '',
      customEndDate: ''
    }
  },

  computed: {
    ...mapGetters('analytics', [
      'isLoading',
      'error',
      'hasError',
      'userStats',
      'userTotalGenerations',
      'userMathGenerations', 
      'userKtpGenerations',
      'userRecentGenerations',
      'generationsGrowth',
      'averageGenerationsPerDay',
      'recentActivity',
      'hasActivity',
      'dailyStats',
      'popularParams',
      'overview',
      'totalUsers',
      'totalGenerations',
      'mathGenerations',
      'ktpGenerations',
      'activeUsersToday',
      'systemStats'
    ]),
    
    ...mapGetters('auth', ['isAdmin']),
    
    mathPercentage() {
      const total = this.userTotalGenerations
      if (total === 0) return 0
      return Math.round((this.userMathGenerations / total) * 100)
    },
    
    ktpPercentage() {
      const total = this.userTotalGenerations
      if (total === 0) return 0
      return Math.round((this.userKtpGenerations / total) * 100)
    },
    
    averagePerDay() {
      return this.averageGenerationsPerDay || 0
    }
  },

  async mounted() {
    await this.loadDashboardData()
  },

  methods: {
    ...mapActions('analytics', [
      'fetchUserStats',
      'fetchUserActivity',
      'fetchDashboardData',
      'fetchOverview',
      'fetchSystemStats',
      'setFilters',
      'resetFilters',
      'trackGeneration'
    ]),

    async loadDashboardData() {
      try {
        // Загружаем основные данные
        await Promise.all([
          this.fetchUserStats(),
          this.fetchUserActivity({ limit: 5 }),
          this.fetchDashboardData()
        ])
        
        // Загружаем административные данные если админ
        if (this.isAdmin) {
          await Promise.all([
            this.fetchOverview(),
            this.fetchSystemStats()
          ])
        }
        
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      }
    },

    async updateFilters() {
      const filters = {
        dateRange: this.selectedDateRange,
        generationType: this.selectedGenerationType
      }
      
      if (this.selectedDateRange === 'custom') {
        filters.startDate = this.customStartDate
        filters.endDate = this.customEndDate
      }
      
      try {
        await this.setFilters(filters)
      } catch (error) {
        console.error('Failed to update filters:', error)
      }
    },

    async resetFilters() {
      this.selectedDateRange = 'week'
      this.selectedGenerationType = 'all'
      this.customStartDate = ''
      this.customEndDate = ''
      
      try {
        await this.resetFilters()
      } catch (error) {
        console.error('Failed to reset filters:', error)
      }
    },

    async retryLoad() {
      await this.loadDashboardData()
    },

    getBarHeight(count) {
      const maxCount = Math.max(...this.dailyStats.map(d => d.count))
      return maxCount > 0 ? (count / maxCount) * 100 : 0
    },

    getParamWidth(count) {
      const maxCount = Math.max(...this.popularParams.map(p => p.count))
      return maxCount > 0 ? (count / maxCount) * 100 : 0
    },

    formatChartDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
    },

    formatDateTime(dateString) {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
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
        const start = params.start_date ? new Date(params.start_date).toLocaleDateString() : 'N/A'
        const end = params.end_date ? new Date(params.end_date).toLocaleDateString() : 'N/A'
        return `Период: ${start} - ${end}`
      }
    },

    async downloadActivity(activity) {
      try {
        const endpoint = activity.type === 'math' ? '/api/math/generate' : '/api/ktp/generate'
        
        const response = await this.$http.post(endpoint, activity.parameters, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', activity.file_name || `${activity.type}_${Date.now()}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        this.$emit('notification', { message: 'Файл скачан', type: 'success' })
        
      } catch (error) {
        console.error('Download error:', error)
        this.$emit('notification', { message: 'Ошибка скачивания файла', type: 'error' })
      }
    },

    repeatActivity(activity) {
      const routeName = activity.type === 'math' ? 'MathGenerator' : 'KtpGenerator'
      
      this.$router.push({
        name: routeName,
        query: { params: JSON.stringify(activity.parameters) }
      })
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.header-content h1 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.header-content p {
  margin: 0;
  color: var(--text-secondary);
}

.dashboard-filters {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.filter-group select,
.filter-group input {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.custom-dates {
  gap: 10px;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 32px;
  padding: 12px;
  border-radius: 8px;
  background: var(--accent-light);
}

.stat-info h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: bold;
  color: var(--accent-primary);
}

.stat-growth,
.stat-percentage,
.stat-average {
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-growth.positive {
  color: #4caf50;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
}

.simple-chart {
  display: flex;
  align-items: end;
  justify-content: space-between;
  height: 120px;
  margin-bottom: 10px;
  gap: 4px;
}

.chart-bar {
  background: var(--accent-primary);
  border-radius: 4px 4px 0 0;
  min-height: 8px;
  flex: 1;
  position: relative;
  cursor: pointer;
  transition: opacity 0.2s;
}

.chart-bar:hover {
  opacity: 0.8;
}

.bar-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: var(--text-secondary);
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  gap: 4px;
}

.chart-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-align: center;
  flex: 1;
}

.popular-params {
  space-y: 12px;
}

.param-item {
  margin-bottom: 12px;
}

.param-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.param-name {
  color: var(--text-primary);
  font-weight: 500;
}

.param-count {
  color: var(--text-secondary);
  font-size: 14px;
}

.param-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.param-fill {
  height: 100%;
  background: var(--accent-primary);
  transition: width 0.3s ease;
}

.activity-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.view-all-link {
  color: var(--accent-primary);
  text-decoration: none;
  font-size: 14px;
}

.view-all-link:hover {
  text-decoration: underline;
}

.activity-list {
  space-y: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 12px;
}

.activity-icon {
  font-size: 20px;
  padding: 8px;
  background: var(--accent-light);
  border-radius: 6px;
}

.activity-info {
  flex: 1;
}

.activity-info h4 {
  margin: 0 0 4px 0;
  color: var(--text-primary);
  font-size: 14px;
}

.activity-info p {
  margin: 0 0 4px 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.activity-info small {
  color: var(--text-muted);
  font-size: 11px;
}

.activity-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  transition: background 0.2s;
  font-size: 14px;
}

.btn-icon:hover {
  background: var(--hover-bg);
}

.empty-activity {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.admin-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
  border-left: 4px solid #ffd700;
}

.admin-section h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
}

.admin-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.admin-stat-card {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color);
}

.admin-stat-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.admin-value {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: bold;
  color: var(--accent-primary);
}

.admin-stat-card small {
  color: var(--text-secondary);
  font-size: 11px;
}

.btn {
  display: inline-block;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
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

.btn-outline {
  background: transparent;
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .dashboard-filters {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .filter-group {
    justify-content: space-between;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .admin-stats {
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
}
</style> 