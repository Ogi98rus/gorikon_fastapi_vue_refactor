/**
 * Простая обертка над fetch для API запросов
 */
export async function fetchApi(url, options = {}) {
  // Создаем копию опций чтобы не мутировать оригинал
  const fetchOptions = { ...options }
  
  // Инициализируем headers если их нет
  if (!fetchOptions.headers) {
    fetchOptions.headers = {}
  }
  
  // Устанавливаем Content-Type для JSON если есть body
  if (fetchOptions.body && !fetchOptions.headers['Content-Type']) {
    fetchOptions.headers['Content-Type'] = 'application/json'
  }
  
  // Делаем запрос к API
  return fetch(url, fetchOptions)
}

/**
 * API методы без авторизации
 */
export const api = {
  get: (url, options = {}) => fetchApi(url, { ...options, method: 'GET' }),
  post: (url, body, options = {}) => {
    const fetchOptions = { ...options, method: 'POST' }
    if (body) {
      fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body)
    }
    return fetchApi(url, fetchOptions)
  },
  put: (url, body, options = {}) => {
    const fetchOptions = { ...options, method: 'PUT' }
    if (body) {
      fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body)
    }
    return fetchApi(url, fetchOptions)
  },
  delete: (url, options = {}) => fetchApi(url, { ...options, method: 'DELETE' })
}

export default api 