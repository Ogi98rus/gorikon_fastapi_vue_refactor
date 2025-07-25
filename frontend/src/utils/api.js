import store from '@/store'

/**
 * Обертка над fetch с автоматической подстановкой токена авторизации
 */
export async function fetchWithAuth(url, options = {}) {
  // Получаем токен из store
  const token = store.state.auth.token
  
  // Создаем копию опций чтобы не мутировать оригинал
  const fetchOptions = { ...options }
  
  // Добавляем CORS настройки
  fetchOptions.credentials = 'include'
  
  // Инициализируем headers если их нет
  if (!fetchOptions.headers) {
    fetchOptions.headers = {}
  }
  
  // Добавляем токен если он есть
  if (token) {
    fetchOptions.headers['Authorization'] = `Bearer ${token}`
  }
  
  // Делаем запрос
  return fetch(url, fetchOptions)
}

/**
 * API методы с авторизацией
 */
export const api = {
  get: (url, options = {}) => fetchWithAuth(url, { ...options, method: 'GET' }),
  post: (url, body, options = {}) => fetchWithAuth(url, { ...options, method: 'POST', body }),
  put: (url, body, options = {}) => fetchWithAuth(url, { ...options, method: 'PUT', body }),
  delete: (url, options = {}) => fetchWithAuth(url, { ...options, method: 'DELETE' })
}

export default api 