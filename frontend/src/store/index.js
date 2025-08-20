import { createStore } from 'vuex'
import i18nModule from './modules/i18n'

export default createStore({
  state: {
    // Глобальное состояние приложения
    appName: 'Генератор учебных материалов',
    version: '2.0.0',
    loading: false,
    error: null,
    success: null
  },
  
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
      if (error) {
        console.error('App Error:', error)
      }
    },
    
    SET_SUCCESS(state, message) {
      state.success = message
    },
    
    CLEAR_MESSAGES(state) {
      state.error = null
      state.success = null
    }
  },
  
  actions: {
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },
    
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    },
    
    setSuccess({ commit }, message) {
      commit('SET_SUCCESS', message)
    },
    
    clearMessages({ commit }) {
      commit('CLEAR_MESSAGES')
    }
  },
  
  getters: {
    isLoading: state => state.loading,
    hasError: state => !!state.error,
    hasSuccess: state => !!state.success,
    errorMessage: state => state.error,
    successMessage: state => state.success
  },
  
  modules: {
    i18n: i18nModule
  }
}) 