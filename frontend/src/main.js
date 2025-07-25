import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// Конфигурация Axios
axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'
axios.defaults.timeout = 30000
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Добавляем axios в глобальные свойства
const app = createApp(App)

// Глобальные свойства
app.config.globalProperties.$http = axios

// Интерсепторы для axios
axios.interceptors.request.use(
  (config) => {
    // Добавляем токен аутентификации если есть
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Обработка ошибок аутентификации
    if (error.response?.status === 401) {
      // Удаляем недействительный токен
      localStorage.removeItem('auth_token')
      store.commit('auth/LOGOUT')
      
      // Перенаправляем на страницу входа если не на публичной странице
      const publicPages = ['/', '/login', '/register']
      if (!publicPages.includes(router.currentRoute.value.path)) {
        router.push('/login')
      }
    }
    
    return Promise.reject(error)
  }
)

// Подключаем плагины
app.use(store)
app.use(router)

// Инициализация приложения
async function initializeApp() {
  try {
    // Инициализируем язык
    await store.dispatch('i18n/initializeLanguage')
    
    // Инициализируем аутентификацию
    await store.dispatch('auth/initAuth')
    
    // Монтируем приложение
    app.mount('#app')
    
  } catch (error) {
    console.error('App initialization failed:', error)
    // Все равно монтируем приложение даже при ошибках инициализации
    app.mount('#app')
  }
}

// Запускаем приложение
initializeApp()
