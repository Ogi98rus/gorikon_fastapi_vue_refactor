import axios from 'axios'

const API_BASE = '/api/analytics'

// Состояние аналитики
const state = {
  // Общая статистика
  overview: {
    total_generations: 0,
    math_generations: 0,
    ktp_generations: 0,
    total_users: 0,
    active_users_today: 0,
    active_users_week: 0,
    active_users_month: 0
  },
  
  // Пользовательская статистика
  userStats: {
    total_generations: 0,
    math_generations: 0,
    ktp_generations: 0,
    recent_generations: 0,
    first_generation: null,
    last_generation: null
  },
  
  // История активности
  userActivity: [],
  
  // Дашборд данные
  dashboardData: {
    dailyStats: [],
    popularParams: [],
    userGrowth: [],
    generationTrends: []
  },
  
  // Системная статистика (для админов)
  systemStats: {
    server_uptime: 0,
    average_response_time: 0,
    error_rate: 0,
    peak_concurrent_users: 0,
    database_size: 0,
    file_storage_used: 0
  },
  
  // Состояние загрузки
  isLoading: false,
  error: null,
  
  // Фильтры для аналитики
  filters: {
    dateRange: 'week', // day, week, month, year, custom
    startDate: null,
    endDate: null,
    generationType: 'all' // all, math, ktp
  }
}

// Мутации
const mutations = {
  SET_LOADING(state, loading) {
    state.isLoading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  SET_OVERVIEW(state, overview) {
    state.overview = { ...state.overview, ...overview }
  },
  
  SET_USER_STATS(state, stats) {
    state.userStats = { ...state.userStats, ...stats }
  },
  
  SET_USER_ACTIVITY(state, activity) {
    state.userActivity = activity
  },
  
  SET_DASHBOARD_DATA(state, data) {
    state.dashboardData = { ...state.dashboardData, ...data }
  },
  
  SET_SYSTEM_STATS(state, stats) {
    state.systemStats = { ...state.systemStats, ...stats }
  },
  
  SET_FILTERS(state, filters) {
    state.filters = { ...state.filters, ...filters }
  },
  
  ADD_USER_ACTIVITY(state, activity) {
    state.userActivity.unshift(activity)
    // Ограничиваем до 50 последних записей
    if (state.userActivity.length > 50) {
      state.userActivity = state.userActivity.slice(0, 50)
    }
  },
  
  CLEAR_ERROR(state) {
    state.error = null
  }
}

// Действия
const actions = {
  // Получение обзорной статистики
  async fetchOverview({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get(`${API_BASE}/overview`)
      commit('SET_OVERVIEW', response.data)
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка загрузки статистики'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Получение пользовательской статистики
  async fetchUserStats({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get(`${API_BASE}/user/stats`)
      commit('SET_USER_STATS', response.data)
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка загрузки пользовательской статистики'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Получение истории активности пользователя
  async fetchUserActivity({ commit }, { limit = 20, offset = 0 } = {}) {
    try {
      const response = await axios.get(`${API_BASE}/user/activity`, {
        params: { limit, offset }
      })
      
      if (offset === 0) {
        commit('SET_USER_ACTIVITY', response.data)
      } else {
        // Добавляем к существующим данным (пагинация)
        const currentActivity = state.userActivity
        commit('SET_USER_ACTIVITY', [...currentActivity, ...response.data])
      }
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка загрузки истории активности'
      commit('SET_ERROR', errorMessage)
      throw error
    }
  },
  
  // Получение данных для дашборда
  async fetchDashboardData({ commit, state }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const params = {
        date_range: state.filters.dateRange,
        generation_type: state.filters.generationType
      }
      
      if (state.filters.startDate) {
        params.start_date = state.filters.startDate
      }
      if (state.filters.endDate) {
        params.end_date = state.filters.endDate
      }
      
      const response = await axios.get(`${API_BASE}/dashboard`, { params })
      commit('SET_DASHBOARD_DATA', response.data)
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка загрузки данных дашборда'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Получение системной статистики (для админов)
  async fetchSystemStats({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.get(`${API_BASE}/system`)
      commit('SET_SYSTEM_STATS', response.data)
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка загрузки системной статистики'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Отслеживание просмотра страницы
  async trackPageView(context, pageData) {
    try {
      await axios.post(`${API_BASE}/track/page-view`, pageData)
      // Не обновляем состояние, это фоновая операция
    } catch (error) {
      // Тихо игнорируем ошибки трекинга
      console.warn('Page view tracking failed:', error)
    }
  },
  
  // Отслеживание события генерации
  async trackGeneration({ commit }, generationData) {
    try {
      await axios.post(`${API_BASE}/track/generation`, generationData)
      
      // Добавляем в локальную историю активности
      commit('ADD_USER_ACTIVITY', {
        id: Date.now(), // Временный ID
        type: generationData.type,
        parameters: generationData.parameters,
        created_at: new Date().toISOString(),
        file_name: generationData.file_name
      })
      
    } catch (error) {
      console.warn('Generation tracking failed:', error)
    }
  },
  
  // Установка фильтров
  setFilters({ commit, dispatch }, filters) {
    commit('SET_FILTERS', filters)
    
    // Автоматически обновляем данные дашборда при изменении фильтров
    return dispatch('fetchDashboardData')
  },
  
  // Сброс фильтров
  resetFilters({ commit, dispatch }) {
    commit('SET_FILTERS', {
      dateRange: 'week',
      startDate: null,
      endDate: null,
      generationType: 'all'
    })
    
    return dispatch('fetchDashboardData')
  },
  
  // Очистка ошибок
  clearError({ commit }) {
    commit('CLEAR_ERROR')
  },
  
  // Инициализация аналитики для аутентифицированного пользователя
  async initializeAnalytics({ dispatch }) {
    try {
      await Promise.all([
        dispatch('fetchUserStats'),
        dispatch('fetchUserActivity', { limit: 10 })
      ])
    } catch (error) {
      console.warn('Analytics initialization failed:', error)
    }
  }
}

// Геттеры
const getters = {
  isLoading: state => state.isLoading,
  error: state => state.error,
  hasError: state => !!state.error,
  
  // Обзорная статистика
  overview: state => state.overview,
  totalGenerations: state => state.overview.total_generations,
  mathGenerations: state => state.overview.math_generations,
  ktpGenerations: state => state.overview.ktp_generations,
  totalUsers: state => state.overview.total_users,
  activeUsersToday: state => state.overview.active_users_today,
  
  // Пользовательская статистика
  userStats: state => state.userStats,
  userTotalGenerations: state => state.userStats.total_generations,
  userMathGenerations: state => state.userStats.math_generations,
  userKtpGenerations: state => state.userStats.ktp_generations,
  userRecentGenerations: state => state.userStats.recent_generations,
  
  // История активности
  userActivity: state => state.userActivity,
  recentActivity: state => state.userActivity.slice(0, 5),
  hasActivity: state => state.userActivity.length > 0,
  
  // Дашборд данные
  dashboardData: state => state.dashboardData,
  dailyStats: state => state.dashboardData.dailyStats || [],
  popularParams: state => state.dashboardData.popularParams || [],
  userGrowth: state => state.dashboardData.userGrowth || [],
  generationTrends: state => state.dashboardData.generationTrends || [],
  
  // Системная статистика
  systemStats: state => state.systemStats,
  
  // Фильтры
  filters: state => state.filters,
  currentDateRange: state => state.filters.dateRange,
  currentGenerationType: state => state.filters.generationType,
  
  // Вычисляемые значения
  generationsGrowth: state => {
    const recent = state.userStats.recent_generations || 0
    const total = state.userStats.total_generations || 0
    if (total === 0) return 0
    return Math.round((recent / total) * 100)
  },
  
  mostPopularType: state => {
    const math = state.userStats.math_generations || 0
    const ktp = state.userStats.ktp_generations || 0
    return math >= ktp ? 'math' : 'ktp'
  },
  
  averageGenerationsPerDay: state => {
    const total = state.userStats.total_generations || 0
    const firstGen = state.userStats.first_generation
    if (!firstGen || total === 0) return 0
    
    const daysSinceFirst = Math.max(1, Math.floor((Date.now() - new Date(firstGen).getTime()) / (1000 * 60 * 60 * 24)))
    return Math.round((total / daysSinceFirst) * 10) / 10
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 