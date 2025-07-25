import axios from 'axios'

const API_BASE = '/user'

// Состояние истории генераций
const state = {
  generations: [],
  currentGeneration: null,
  isLoading: false,
  error: null,
  
  // Пагинация
  currentPage: 1,
  perPage: 10,
  totalCount: 0,
  
  // Фильтры
  filterType: null, // 'math' или 'ktp'
  
  // Статистика профиля
  profileStats: null
}

// Мутации
const mutations = {
  SET_GENERATIONS(state, { generations, total_count, page, per_page }) {
    state.generations = generations
    state.totalCount = total_count
    state.currentPage = page
    state.perPage = per_page
  },
  
  SET_CURRENT_GENERATION(state, generation) {
    state.currentGeneration = generation
  },
  
  SET_LOADING(state, loading) {
    state.isLoading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  CLEAR_ERROR(state) {
    state.error = null
  },
  
  SET_FILTER_TYPE(state, type) {
    state.filterType = type
  },
  
  SET_PROFILE_STATS(state, stats) {
    state.profileStats = stats
  },
  
  REMOVE_GENERATION(state, generationId) {
    state.generations = state.generations.filter(gen => gen.id !== generationId)
    state.totalCount = Math.max(0, state.totalCount - 1)
  },
  
  INCREMENT_DOWNLOAD_COUNT(state, generationId) {
    const generation = state.generations.find(gen => gen.id === generationId)
    if (generation) {
      generation.download_count += 1
    }
    if (state.currentGeneration && state.currentGeneration.id === generationId) {
      state.currentGeneration.download_count += 1
    }
  }
}

// Действия
const actions = {
  // Загрузка списка генераций
  async fetchGenerations({ commit }, { page = 1, per_page = 10, generator_type = null } = {}) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const params = {
        page,
        per_page,
        ...(generator_type && { generator_type })
      }
      
      const response = await axios.get(`${API_BASE}/generations`, { params })
      commit('SET_GENERATIONS', response.data)
      return response.data
      
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Ошибка загрузки истории генераций'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Загрузка конкретной генерации
  async fetchGeneration({ commit }, generationId) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get(`${API_BASE}/generations/${generationId}`)
      commit('SET_CURRENT_GENERATION', response.data.generation)
      return response.data.generation
      
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Ошибка загрузки генерации'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Скачивание файла генерации
  async downloadGeneration({ commit }, generationId) {
    try {
      const response = await axios.get(`${API_BASE}/generations/${generationId}/download`, {
        responseType: 'blob'
      })
      
      // Создаем blob и ссылку для скачивания
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      
      // Получаем имя файла из заголовков
      const contentDisposition = response.headers['content-disposition']
      let filename = 'download'
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
        }
      }
      
      // Создаем временную ссылку и кликаем по ней
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      
      // Очищаем
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      // Увеличиваем счетчик скачиваний
      commit('INCREMENT_DOWNLOAD_COUNT', generationId)
      
      return { success: true, filename }
      
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Ошибка скачивания файла'
      commit('SET_ERROR', errorMessage)
      throw new Error(errorMessage)
    }
  },
  
  // Удаление генерации
  async deleteGeneration({ commit }, generationId) {
    try {
      await axios.delete(`${API_BASE}/generations/${generationId}`)
      commit('REMOVE_GENERATION', generationId)
      return { success: true }
      
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Ошибка удаления генерации'
      commit('SET_ERROR', errorMessage)
      throw new Error(errorMessage)
    }
  },
  
  // Загрузка расширенного профиля
  async fetchProfile({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await axios.get(`${API_BASE}/profile`)
      commit('SET_PROFILE_STATS', response.data)
      return response.data
      
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Ошибка загрузки профиля'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Загрузка статистики пользователя
  async fetchUserStatistics({ commit }) {
    try {
      const response = await axios.get(`${API_BASE}/statistics`)
      return response.data.statistics
      
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Ошибка загрузки статистики'
      commit('SET_ERROR', errorMessage)
      throw error
    }
  },
  
  // Обновление фильтра
  setFilterType({ commit, dispatch }, type) {
    commit('SET_FILTER_TYPE', type)
    // Перезагружаем список с новым фильтром
    return dispatch('fetchGenerations', { 
      page: 1, 
      generator_type: type 
    })
  },
  
  // Очистка данных
  clearHistory({ commit }) {
    commit('SET_GENERATIONS', { generations: [], total_count: 0, page: 1, per_page: 10 })
    commit('SET_CURRENT_GENERATION', null)
    commit('SET_PROFILE_STATS', null)
    commit('CLEAR_ERROR')
  }
}

// Геттеры
const getters = {
  generations: state => state.generations,
  currentGeneration: state => state.currentGeneration,
  isLoading: state => state.isLoading,
  error: state => state.error,
  hasError: state => !!state.error,
  
  // Пагинация
  currentPage: state => state.currentPage,
  perPage: state => state.perPage,
  totalCount: state => state.totalCount,
  totalPages: state => Math.ceil(state.totalCount / state.perPage),
  hasNextPage: state => state.currentPage < Math.ceil(state.totalCount / state.perPage),
  hasPrevPage: state => state.currentPage > 1,
  
  // Фильтры
  filterType: state => state.filterType,
  
  // Статистика
  profileStats: state => state.profileStats,
  
  // Группировка генераций по типу
  mathGenerations: state => state.generations.filter(gen => gen.generator_type === 'math'),
  ktpGenerations: state => state.generations.filter(gen => gen.generator_type === 'ktp'),
  
  // Статистика по генерациям
  totalGenerations: state => state.generations.length,
  totalDownloads: state => state.generations.reduce((sum, gen) => sum + gen.download_count, 0),
  averageFileSize: state => {
    if (state.generations.length === 0) return 0
    const totalSize = state.generations.reduce((sum, gen) => sum + gen.file_size, 0)
    return Math.round(totalSize / state.generations.length)
  },
  
  // Последние генерации
  recentGenerations: state => state.generations.slice(0, 5),
  
  // Проверка доступности
  isGenerationAvailable: state => (generationId) => {
    const generation = state.generations.find(gen => gen.id === generationId)
    return generation?.is_available && 
           (!generation.expires_at || new Date(generation.expires_at) > new Date())
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 