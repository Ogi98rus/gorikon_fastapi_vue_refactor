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
    'common.hint': 'Подсказка',
    'common.example': 'Пример',
    'common.recommendation': 'Рекомендация',
    'common.russian': 'Русский',
    'common.english': 'English',
    'common.toggleTheme': 'Toggle theme',
    
    // Навигация
    'nav.home': 'Главная',
    'nav.math': 'Математика',
    'nav.ktp': 'КТП',
    'nav.mathGame': 'Примеры онлайн',
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
    
    // Главная страница
    'home.title': 'ВЫБЕРИТЕ ГЕНЕРАТОР',
    'home.mathGenerator': '📊 Генератор Математических Примеров',
    'home.ktpGenerator': '📅 Генератор Дат для КТП',
    'home.mathGame': '🎮 Примеры онлайн',
    'home.advice': 'Совет: Выберите нужный генератор выше для создания учебных материалов.',
    
    // Математический генератор
    'math.title': 'Генерация математических примеров',
    'math.operations': 'Операции',
    'math.operands': 'Количество операндов',
    'math.interval': 'Диапазон чисел',
    'math.examples': 'Количество примеров',
    'math.generate': 'Создать задачи',
    'math.operandsLabel': 'Количество операндов:',
    'math.operandsHint': 'Подсказка: Количество чисел в примере (от 2 до 5). Например: при значении 3 получится "2 + 3 - 1 = 4"',
    'math.operationsLabel': 'Операции:',
    'math.addition': '+ (Сложение)',
    'math.subtraction': '- (Вычитание)',
    'math.multiplication': '× (Умножение)',
    'math.division': '÷ (Деление)',
    'math.operationsHint': 'Подсказка: Выберите операции, которые будут использоваться в примерах. Можно выбрать несколько.',
    'math.intervalStart': 'Начало интервала:',
    'math.intervalEnd': 'Конец интервала:',
    'math.intervalExample': 'Пример диапазона: от 0 до 100 — числа будут от 0 до 100 включительно',
    'math.examplesLabel': 'Количество примеров:',
    'math.examplesHint': 'Рекомендация: Для одного урока оптимально 10-20 примеров',
    'math.generateButton': '📄 Сгенерировать PDF',
    'math.generating': '⏳ Генерация...',
    'math.homeButton': '🏠 На главную',
    'math.error': 'Ошибка:',
    'math.selectOperation': 'Выберите хотя бы одну операцию',
    'math.connectionError': 'Ошибка соединения с сервером',
    'math.pdfError': 'Ошибка генерации PDF',
    'math.infoTitle': 'ℹ️ Информация о генераторе',
    'math.infoPositive': '• Генератор создает математические примеры только с положительными результатами',
    'math.infoPDF': '• PDF файл будет содержать примеры в сетке для решения',
    'math.infoRandom': '• Все примеры генерируются случайно в указанном диапазоне',
    'math.downloadModalTitle': 'Выберите вариант для скачивания',
    'math.downloadForStudent': '📚 Для ученика',
    'math.downloadForTeacher': '👨‍🏫 Для учителя',
    'math.studentDescription': 'Примеры в сетке без ответов',
    'math.teacherDescription': 'Примеры с ответами для проверки',
    'math.downloadButton': 'Скачать',
    'math.cancelButton': 'Отмена',
    'math.downloadBoth': 'Скачать оба варианта',
    'math.downloadBothHint': 'Скачать PDF для ученика и учителя',
            'common.serverSupport': 'Поддержать проект',
    
    // КТП генератор
    'ktp.title': 'Генератор для КТП',
    'ktp.startDate': 'Дата начала',
    'ktp.endDate': 'Дата окончания',
    'ktp.weekdays': 'Дни недели',
    'ktp.lessonsPerDay': 'Уроков в день',
    'ktp.holidays': 'Праздники',
    'ktp.generate': 'Создать КТП',
    'ktp.startDateLabel': 'Начальная дата:',
    'ktp.endDateLabel': 'Конечная дата:',
    'ktp.dateHint': 'Укажите период учебного года (например, с 01.09.2024 по 31.05.2025)',
    'ktp.weekdaysLabel': 'Дни недели и количество уроков в день:',
    'ktp.weekdaysHint': 'Выберите рабочие дни недели и укажите количество уроков в каждый день',
    'ktp.holidaysLabel': 'Праздничные дни (разделитель - запятая):',
    'ktp.holidaysPlaceholder': '04.11.2025, 23.02.2026, 09.03.2026, 11.05.2026',
    'ktp.holidaysExample': 'Пример:',
    'ktp.autumnStart': 'Начало осенних каникул:',
    'ktp.autumnEnd': 'Конец осенних каникул:',
    'ktp.winterStart': 'Начало зимних каникул:',
    'ktp.winterEnd': 'Конец зимних каникул:',
    'ktp.springStart': 'Начало весенних каникул:',
    'ktp.springEnd': 'Конец весенних каникул:',
    'ktp.lessonsPlaceholder': 'Уроков',
    'ktp.generateButton': '📄 Сгенерировать КТП',
    'ktp.generating': '⏳ Генерация...',
    'ktp.homeButton': '🏠 На главную',
    'ktp.weekdayMonday': 'Понедельник',
    'ktp.weekdayTuesday': 'Вторник',
    'ktp.weekdayWednesday': 'Среда',
    'ktp.weekdayThursday': 'Четверг',
    'ktp.weekdayFriday': 'Пятница',
    'ktp.weekdaySaturday': 'Суббота',
    'ktp.weekdaySunday': 'Воскресенье',
    'ktp.firstClassHolidays': 'Каникулы для 1 классов',
    'ktp.filenameLabel': 'Имя файла для сохранения:',
    'ktp.filenamePlaceholder': 'schedule',
    'ktp.filenameExample': 'Пример: КТП_математика_5класс',
    'ktp.importantNote': '⚠️ ВАЖНО!',
    'ktp.workdayTransfer': '',
    'ktp.workdayTransferHint': 'Не забывайте, что есть даты, которые необходимо править вручную, например когда вторник, но работаем по понедельнику.',
    'ktp.generatorInfo': 'ℹ️ Информация о генераторе',
    'ktp.generatorInfo1': '• Генератор создает календарно-тематическое планирования в формате Excel',
    'ktp.generatorInfo2': '• Автоматически исключает праздники и каникулы',
    'ktp.generatorInfo3': '• Учитывает количество уроков по дням недели',
    'ktp.generatorInfo4': '• Поддерживает дополнительные каникулы для 1 классов',
    'ktp.generatorInfo5': '• Формат дат в файле: ДД.ММ для удобства',
    'ktp.firstGradeStart': 'Начало дополнительных каникул для 1 классов:',
    'ktp.firstGradeEnd': 'Конец дополнительных каникул для 1 классов:',
    'ktp.firstGradeHint': 'Обычно: дополнительные каникулы для 1 классов проводятся в феврале (например, с 16.02 по 22.02)',
    'ktp.selectWeekdayError': 'Выберите хотя бы один день недели',
    'ktp.holidaysHint': 'Укажите периоды каникул. Эти дни будут исключены из расписания',
    
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
    'common.hint': 'Hint',
    'common.example': 'Example',
    'common.recommendation': 'Recommendation',
    'common.russian': 'Русский',
    'common.english': 'English',
    
    // Navigation
    'nav.home': 'Home',
    'nav.math': 'Math',
    'nav.ktp': 'LTP',
    'nav.mathGame': 'Online Examples',
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
    
    // Home Page
    'home.title': 'SELECT GENERATOR',
    'home.mathGenerator': '📊 Math Problems Generator',
    'home.ktpGenerator': '📅 LTP Date Generator',
    'home.mathGame': '🎮 Online Examples',
    'home.advice': 'Tip: Select the generator above to create educational materials.',
    
    // Math Generator
    'math.title': 'Math Problems Generator',
    'math.operations': 'Operations',
    'math.operands': 'Number of Operands',
    'math.interval': 'Number Range',
    'math.examples': 'Number of Examples',
    'math.generate': 'Generate Problems',
    'math.operandsLabel': 'Number of operands:',
    'math.operandsHint': 'Hint: Number of numbers in the example (from 2 to 5). For example: with value 3 you will get "2 + 3 - 1 = 4"',
    'math.operationsLabel': 'Operations:',
    'math.addition': '+ (Addition)',
    'math.subtraction': '- (Subtraction)',
    'math.multiplication': '× (Multiplication)',
    'math.division': '÷ (Division)',
    'math.operationsHint': 'Hint: Select operations that will be used in examples. You can select several.',
    'math.intervalStart': 'Range start:',
    'math.intervalEnd': 'Range end:',
    'math.intervalExample': 'Range example: from 0 to 100 — numbers will be from 0 to 100 inclusive',
    'math.examplesLabel': 'Number of examples:',
    'math.examplesHint': 'Recommendation: For one lesson, 10-20 examples are optimal',
    'math.generateButton': '📄 Generate PDF',
    'math.generating': '⏳ Generating...',
    'math.homeButton': '🏠 Home',
    'math.error': 'Error:',
    'math.selectOperation': 'Select at least one operation',
    'math.connectionError': 'Server connection error',
    'math.pdfError': 'PDF generation error',
    'math.infoTitle': 'ℹ️ Generator Information',
    'math.infoPositive': '• Generator creates math examples with positive results only',
    'math.infoPDF': '• PDF file will contain examples in grid for solving',
    'math.infoRandom': '• All examples are generated randomly in the specified range',
    'math.downloadModalTitle': 'Select download option',
    'math.downloadForStudent': '📚 For Student',
    'math.downloadForTeacher': '👨‍🏫 For Teacher',
    'math.studentDescription': 'Examples in grid without answers',
    'math.teacherDescription': 'Examples with answers for checking',
    'math.downloadButton': 'Download',
    'math.cancelButton': 'Cancel',
    'math.downloadBoth': 'Download Both',
    'math.downloadBothHint': 'Download PDF for student and teacher',
            'common.serverSupport': 'Support the project',
    
    // LTP Generator
    'ktp.title': 'LTP Generator',
    'ktp.startDate': 'Start Date',
    'ktp.endDate': 'End Date',
    'ktp.weekdays': 'Weekdays',
    'ktp.lessonsPerDay': 'Lessons per Day',
    'ktp.holidays': 'Holidays',
    'ktp.generate': 'Generate LTP',
    'ktp.startDateLabel': 'Start date:',
    'ktp.endDateLabel': 'End date:',
    'ktp.dateHint': 'Hint: Specify the academic year period (e.g., from 01.09.2024 to 31.05.2025)',
    'ktp.weekdaysLabel': 'Weekdays and number of lessons per day:',
    'ktp.weekdaysHint': 'Hint: Select working weekdays and specify the number of lessons for each day',
    'ktp.holidaysLabel': 'Holidays (separator - comma):',
    'ktp.holidaysPlaceholder': '04.11.2025, 23.02.2026, 09.03.2026, 11.05.2026',
    'ktp.holidaysExample': 'Example:',
    'ktp.autumnStart': 'Autumn holidays start:',
    'ktp.autumnEnd': 'Autumn holidays end:',
    'ktp.winterStart': 'Winter holidays start:',
    'ktp.winterEnd': 'Winter holidays end:',
    'ktp.springStart': 'Spring holidays start:',
    'ktp.springEnd': 'Spring holidays end:',
    'ktp.lessonsPlaceholder': 'Lessons',
    'ktp.generateButton': '📄 Generate LTP',
    'ktp.generating': '⏳ Generating...',
    'ktp.homeButton': '🏠 Home',
    'ktp.weekdayMonday': 'Monday',
    'ktp.weekdayTuesday': 'Tuesday',
    'ktp.weekdayWednesday': 'Wednesday',
    'ktp.weekdayThursday': 'Thursday',
    'ktp.weekdayFriday': 'Friday',
    'ktp.weekdaySaturday': 'Saturday',
    'ktp.weekdaySunday': 'Sunday',
    'ktp.firstClassHolidays': 'Holidays for 1st grade',
    'ktp.filenameLabel': 'Filename for saving:',
    'ktp.filenamePlaceholder': 'schedule',
    'ktp.filenameExample': 'Example: LTP_math_5grade',
    'ktp.importantNote': '⚠️ IMPORTANT! DATES THAT NEED TO BE EDITED MANUALLY',
    'ktp.workdayTransfer': '28.12.2024 Saturday - working on Tuesday',
    'ktp.workdayTransferHint': 'Don\'t forget that there are dates that need to be edited manually, for example when it\'s Tuesday but we work on Monday.',
    'ktp.generatorInfo': 'ℹ️ Generator Information',
    'ktp.generatorInfo1': '• Generator creates calendar-thematic planning in Excel format',
    'ktp.generatorInfo2': '• Automatically excludes holidays and vacations',
    'ktp.generatorInfo3': '• Considers the number of lessons per weekday',
    'ktp.generatorInfo4': '• Supports additional holidays for 1st grade',
    'ktp.generatorInfo5': '• Date format in file: DD.MM for convenience',
    'ktp.firstGradeStart': 'Start of additional holidays for 1st grade:',
    'ktp.firstGradeEnd': 'End of additional holidays for 1st grade:',
    'ktp.firstGradeHint': 'Usually: additional holidays for 1st grade are held in February (e.g., from 14.02 to 20.02)',
    'ktp.selectWeekdayError': 'Select at least one weekday',
    'ktp.holidaysHint': 'Specify vacation periods. These days will be excluded from the schedule',
    
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
  getCurrentLanguage: state => state.currentLanguage,
  
  // Доступные языки
  availableLanguages: state => Object.values(state.availableLanguages),
  supportedLanguageCodes: state => Object.keys(state.availableLanguages),
  
  // Переводы
  translations: state => {
    const currentLang = state.currentLanguage
    const translations = state.translations[currentLang] || state.translations['ru'] || {}
    return translations
  },
  
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