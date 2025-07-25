import axios from 'axios'

const API_BASE = '/api/auth'

// Состояние аутентификации
const state = {
  user: null,
  token: localStorage.getItem('auth_token') || null,
  isAuthenticated: false,
  isLoading: false,
  loginError: null,
  registerError: null
}

// Мутации
const mutations = {
  SET_USER(state, user) {
    state.user = user
    state.isAuthenticated = !!user
  },
  
  SET_TOKEN(state, token) {
    state.token = token
    if (token) {
      localStorage.setItem('auth_token', token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      localStorage.removeItem('auth_token')
      delete axios.defaults.headers.common['Authorization']
    }
  },
  
  SET_LOADING(state, loading) {
    state.isLoading = loading
  },
  
  SET_LOGIN_ERROR(state, error) {
    state.loginError = error
  },
  
  SET_REGISTER_ERROR(state, error) {
    state.registerError = error
  },
  
  CLEAR_ERRORS(state) {
    state.loginError = null
    state.registerError = null
  },
  
  LOGOUT(state) {
    state.user = null
    state.token = null
    state.isAuthenticated = false
    localStorage.removeItem('auth_token')
    delete axios.defaults.headers.common['Authorization']
  }
}

// Действия
const actions = {
  // Инициализация аутентификации при загрузке приложения
  async initAuth({ commit, state }) {
    if (state.token) {
      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
        const response = await axios.get(`${API_BASE}/me`)
        commit('SET_USER', response.data)
      } catch (error) {
        console.log('Token expired or invalid')
        commit('LOGOUT')
      }
    }
  },
  
  // Проверка статуса аутентификации
  async checkAuthStatus({ commit }) {
    try {
      const response = await axios.get(`${API_BASE}/check`)
      if (response.data.authenticated) {
        commit('SET_USER', response.data.user)
      } else {
        commit('LOGOUT')
      }
      return response.data.authenticated
    } catch (error) {
      commit('LOGOUT')
      return false
    }
  },
  
  // Вход пользователя
  async login({ commit }, credentials) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERRORS')
    
    try {
      // Подготавливаем данные для FormData (как ожидает backend)
      const formData = new FormData()
      formData.append('username', credentials.email) // OAuth2PasswordRequestForm использует 'username'
      formData.append('password', credentials.password)
      
      const response = await axios.post(`${API_BASE}/login`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      const { access_token } = response.data
      
      // Сохраняем токен
      commit('SET_TOKEN', access_token)
      
      // Получаем информацию о пользователе
      const userResponse = await axios.get(`${API_BASE}/me`)
      commit('SET_USER', userResponse.data)
      
      return { success: true, user: userResponse.data }
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка входа в систему'
      commit('SET_LOGIN_ERROR', errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Регистрация пользователя
  async register({ commit }, userData) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERRORS')
    
    try {
      // Подготавливаем данные для FormData
      const formData = new FormData()
      formData.append('email', userData.email)
      formData.append('full_name', userData.full_name)
      formData.append('password', userData.password)
      if (userData.school_name) {
        formData.append('school_name', userData.school_name)
      }
      
      const response = await axios.post(`${API_BASE}/register`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      const { access_token } = response.data
      
      // Сохраняем токен
      commit('SET_TOKEN', access_token)
      
      // Получаем информацию о пользователе
      const userResponse = await axios.get(`${API_BASE}/me`)
      commit('SET_USER', userResponse.data)
      
      return { success: true, user: userResponse.data }
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка регистрации'
      commit('SET_REGISTER_ERROR', errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Выход пользователя
  async logout({ commit, state }) {
    try {
      if (state.token) {
        await axios.post(`${API_BASE}/logout`)
      }
    } catch (error) {
      console.log('Logout error:', error)
    } finally {
      commit('LOGOUT')
    }
  },
  
  // Очистка ошибок
  clearErrors({ commit }) {
    commit('CLEAR_ERRORS')
  }
}

// Геттеры
const getters = {
  isAuthenticated: state => state.isAuthenticated,
  user: state => state.user,
  token: state => state.token,
  isLoading: state => state.isLoading,
  loginError: state => state.loginError,
  registerError: state => state.registerError,
  hasErrors: state => !!(state.loginError || state.registerError),
  
  // Проверка ролей
  isAdmin: state => state.user?.is_superuser || false,
  userName: state => state.user?.full_name || '',
  userEmail: state => state.user?.email || '',
  userSchool: state => state.user?.school_name || ''
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 