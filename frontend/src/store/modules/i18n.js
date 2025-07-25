import axios from 'axios'

const API_BASE = '/api/i18n'

// Поддерживаемые языки
const SUPPORTED_LANGUAGES = {
  ru: {
    code: 'ru',
    name: 'Русский',
    flag: '🇷🇺',
    nativeName: 'Русский'
  },
  en: {
    code: 'en', 
    name: 'English',
    flag: '🇺🇸',
    nativeName: 'English'
  },
  kk: {
    code: 'kk',
    name: 'Қазақша',
    flag: '🇰🇿', 
    nativeName: 'Қазақ тілі'
  },
  be: {
    code: 'be',
    name: 'Беларуская',
    flag: '🇧🇾',
    nativeName: 'Беларуская мова'
  },
  uk: {
    code: 'uk',
    name: 'Українська',
    flag: '🇺🇦',
    nativeName: 'Українська мова'
  }
}

// Базовые переводы (fallback)
const BASE_TRANSLATIONS = {
  ru: {
    // Общие
    'common.loading': 'Загрузка...',
    'common.error': 'Ошибка',
    'common.success': 'Успешно',
    'common.save': 'Сохранить',
    'common.cancel': 'Отменить',
    'common.delete': 'Удалить',
    'common.edit': 'Редактировать',
    'common.close': 'Закрыть',
    'common.back': 'Назад',
    'common.next': 'Далее',
    'common.previous': 'Предыдущий',
    'common.submit': 'Отправить',
    'common.reset': 'Сбросить',
    'common.search': 'Поиск',
    'common.filter': 'Фильтр',
    
    // Навигация
    'nav.home': 'Главная',
    'nav.math': 'Математика',
    'nav.ktp': 'КТП',
    'nav.analytics': 'Аналитика',
    'nav.profile': 'Профиль',
    'nav.login': 'Войти',
    'nav.register': 'Регистрация',
    'nav.logout': 'Выйти',
    
    // Аутентификация
    'auth.login': 'Вход в систему',
    'auth.register': 'Регистрация',
    'auth.email': 'Электронная почта',
    'auth.password': 'Пароль',
    'auth.fullName': 'Полное имя',
    'auth.school': 'Школа',
    'auth.forgotPassword': 'Забыли пароль?',
    'auth.rememberMe': 'Запомнить меня',
    'auth.agreeTerms': 'Я согласен с условиями использования',
    
    // Математический генератор
    'math.title': 'Генератор математических задач',
    'math.operations': 'Операции',
    'math.operands': 'Количество операндов',
    'math.interval': 'Диапазон чисел',
    'math.examples': 'Количество примеров',
    'math.generate': 'Создать задачи',
    
    // КТП генератор
    'ktp.title': 'Генератор КТП',
    'ktp.startDate': 'Дата начала',
    'ktp.endDate': 'Дата окончания',
    'ktp.weekdays': 'Дни недели',
    'ktp.lessonsPerDay': 'Уроков в день',
    'ktp.holidays': 'Праздники',
    'ktp.generate': 'Создать КТП',
    
    // Профиль
    'profile.title': 'Профиль пользователя',
    'profile.stats': 'Статистика',
    'profile.activity': 'Активность',
    'profile.edit': 'Редактировать профиль',
    'profile.changePassword': 'Изменить пароль',
    
    // Ошибки
    'error.general': 'Произошла ошибка',
    'error.network': 'Ошибка сети',
    'error.validation': 'Ошибка валидации',
    'error.auth': 'Ошибка аутентификации',
    'error.permission': 'Недостаточно прав'
  },
  
  en: {
    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.close': 'Close',
    'common.back': 'Back',
    'common.next': 'Next',
    'common.previous': 'Previous',
    'common.submit': 'Submit',
    'common.reset': 'Reset',
    'common.search': 'Search',
    'common.filter': 'Filter',
    
    // Navigation
    'nav.home': 'Home',
    'nav.math': 'Math',
    'nav.ktp': 'LTP',
    'nav.analytics': 'Analytics',
    'nav.profile': 'Profile',
    'nav.login': 'Login',
    'nav.register': 'Register',
    'nav.logout': 'Logout',
    
    // Authentication
    'auth.login': 'Login',
    'auth.register': 'Registration',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.fullName': 'Full Name',
    'auth.school': 'School',
    'auth.forgotPassword': 'Forgot Password?',
    'auth.rememberMe': 'Remember Me',
    'auth.agreeTerms': 'I agree to the terms of use',
    
    // Math Generator
    'math.title': 'Math Problems Generator',
    'math.operations': 'Operations',
    'math.operands': 'Number of Operands',
    'math.interval': 'Number Range',
    'math.examples': 'Number of Examples',
    'math.generate': 'Generate Problems',
    
    // LTP Generator
    'ktp.title': 'Learning-Thematic Planning Generator',
    'ktp.startDate': 'Start Date',
    'ktp.endDate': 'End Date',
    'ktp.weekdays': 'Weekdays',
    'ktp.lessonsPerDay': 'Lessons per Day',
    'ktp.holidays': 'Holidays',
    'ktp.generate': 'Generate LTP',
    
    // Profile
    'profile.title': 'User Profile',
    'profile.stats': 'Statistics',
    'profile.activity': 'Activity',
    'profile.edit': 'Edit Profile',
    'profile.changePassword': 'Change Password',
    
    // Errors
    'error.general': 'An error occurred',
    'error.network': 'Network error',
    'error.validation': 'Validation error',
    'error.auth': 'Authentication error',
    'error.permission': 'Permission denied'
  }
}

// Состояние i18n
const state = {
  // Текущий язык
  currentLanguage: 'ru',
  
  // Доступные языки
  availableLanguages: SUPPORTED_LANGUAGES,
  
  // Переводы
  translations: BASE_TRANSLATIONS,
  
  // Загруженные переводы с сервера
  serverTranslations: {},
  
  // Состояние загрузки
  isLoading: false,
  error: null,
  
  // Настройки локализации
  locale: {
    dateFormat: 'DD.MM.YYYY',
    timeFormat: '24',
    numberFormat: 'ru-RU',
    currency: 'RUB'
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
  
  SET_CURRENT_LANGUAGE(state, language) {
    state.currentLanguage = language
    
    // Обновляем настройки локализации в зависимости от языка
    switch (language) {
      case 'en':
        state.locale = {
          dateFormat: 'MM/DD/YYYY',
          timeFormat: '12',
          numberFormat: 'en-US',
          currency: 'USD'
        }
        break
      case 'kk':
        state.locale = {
          dateFormat: 'DD.MM.YYYY',
          timeFormat: '24',
          numberFormat: 'kk-KZ',
          currency: 'KZT'
        }
        break
      case 'be':
      case 'uk':
        state.locale = {
          dateFormat: 'DD.MM.YYYY',
          timeFormat: '24',
          numberFormat: 'ru-RU',
          currency: 'BYN'
        }
        break
      default: // ru
        state.locale = {
          dateFormat: 'DD.MM.YYYY',
          timeFormat: '24',
          numberFormat: 'ru-RU',
          currency: 'RUB'
        }
    }
  },
  
  SET_TRANSLATIONS(state, { language, translations }) {
    state.serverTranslations[language] = translations
    
    // Объединяем с базовыми переводами
    if (state.translations[language]) {
      state.translations[language] = {
        ...state.translations[language],
        ...translations
      }
    } else {
      state.translations[language] = translations
    }
  },
  
  CLEAR_ERROR(state) {
    state.error = null
  }
}

// Действия
const actions = {
  // Установка языка
  async setLanguage({ commit, dispatch }, language) {
    if (!SUPPORTED_LANGUAGES[language]) {
      throw new Error(`Unsupported language: ${language}`)
    }
    
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      // Устанавливаем язык
      commit('SET_CURRENT_LANGUAGE', language)
      
      // Сохраняем в localStorage
      localStorage.setItem('selected_language', language)
      
      // Загружаем переводы с сервера если их еще нет
      if (!state.serverTranslations[language]) {
        await dispatch('loadTranslations', language)
      }
      
      // Отправляем на сервер для установки языка сессии
      try {
        await axios.post(`${API_BASE}/set-language`, { language })
      } catch (error) {
        console.warn('Failed to set server language:', error)
      }
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Ошибка установки языка'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // Загрузка переводов с сервера
  async loadTranslations({ commit }, language) {
    try {
      const response = await axios.get(`${API_BASE}/translations/${language}`)
      commit('SET_TRANSLATIONS', { language, translations: response.data })
    } catch (error) {
      console.warn(`Failed to load translations for ${language}:`, error)
      // Игнорируем ошибки загрузки переводов, используем базовые
    }
  },
  
  // Инициализация языка при загрузке приложения
  async initializeLanguage({ commit, dispatch }) {
    try {
      // Получаем сохраненный язык или определяем из браузера
      const savedLanguage = localStorage.getItem('selected_language')
      const browserLanguage = navigator.language.split('-')[0]
      
      let language = savedLanguage
      if (!language && Object.keys(SUPPORTED_LANGUAGES).includes(browserLanguage)) {
        language = browserLanguage
      }
      if (!language) {
        language = 'ru' // Язык по умолчанию
      }
      
      await dispatch('setLanguage', language)
      
    } catch (error) {
      console.warn('Language initialization failed:', error)
      // Устанавливаем русский по умолчанию при ошибке
      commit('SET_CURRENT_LANGUAGE', 'ru')
    }
  },
  
  // Предзагрузка переводов для всех языков
  async preloadAllTranslations({ dispatch }) {
    const languages = Object.keys(SUPPORTED_LANGUAGES)
    
    try {
      await Promise.allSettled(
        languages.map(lang => dispatch('loadTranslations', lang))
      )
    } catch (error) {
      console.warn('Failed to preload translations:', error)
    }
  },
  
  // Очистка ошибок
  clearError({ commit }) {
    commit('CLEAR_ERROR')
  }
}

// Геттеры
const getters = {
  isLoading: state => state.isLoading,
  error: state => state.error,
  hasError: state => !!state.error,
  
  // Текущий язык
  currentLanguage: state => state.currentLanguage,
  currentLanguageInfo: state => SUPPORTED_LANGUAGES[state.currentLanguage],
  
  // Доступные языки
  availableLanguages: state => Object.values(state.availableLanguages),
  supportedLanguageCodes: state => Object.keys(state.availableLanguages),
  
  // Переводы
  translations: state => state.translations[state.currentLanguage] || {},
  
  // Функция перевода
  t: (state) => (key, params = {}) => {
    const translations = state.translations[state.currentLanguage] || state.translations['ru'] || {}
    let text = translations[key] || key
    
    // Подстановка параметров
    Object.keys(params).forEach(param => {
      text = text.replace(new RegExp(`{${param}}`, 'g'), params[param])
    })
    
    return text
  },
  
  // Настройки локализации
  locale: state => state.locale,
  dateFormat: state => state.locale.dateFormat,
  timeFormat: state => state.locale.timeFormat,
  numberFormat: state => state.locale.numberFormat,
  currency: state => state.locale.currency,
  
  // Помощники для форматирования
  formatDate: (state) => (date) => {
    if (!date) return ''
    const options = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }
    return new Date(date).toLocaleDateString(state.locale.numberFormat, options)
  },
  
  formatDateTime: (state) => (date) => {
    if (!date) return ''
    const options = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }
    return new Date(date).toLocaleDateString(state.locale.numberFormat, options)
  },
  
  formatNumber: (state) => (number) => {
    if (number === null || number === undefined) return ''
    return new Intl.NumberFormat(state.locale.numberFormat).format(number)
  },
  
  formatCurrency: (state) => (amount) => {
    if (amount === null || amount === undefined) return ''
    return new Intl.NumberFormat(state.locale.numberFormat, {
      style: 'currency',
      currency: state.locale.currency
    }).format(amount)
  },
  
  // Проверки RTL/LTR
  isRTL: (state) => {
    const rtlLanguages = ['ar', 'he', 'fa']
    return rtlLanguages.includes(state.currentLanguage)
  },
  
  textDirection: (state, getters) => getters.isRTL ? 'rtl' : 'ltr'
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 