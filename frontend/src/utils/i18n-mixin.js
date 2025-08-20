import { mapState, mapGetters } from 'vuex'

export default {
  computed: {
    ...mapState('i18n', ['currentLanguage']),
    ...mapGetters('i18n', ['t', 'getCurrentLanguage'])
  },
  
  methods: {
    // Метод для получения перевода
    $t(key, params = {}) {
      try {
        // Прямое обращение к store без геттеров
        if (this.$store && this.$store.getters['i18n/t']) {
          return this.$store.getters['i18n/t'](key, params)
        }
        
        // Fallback - прямое обращение к состоянию store
        if (this.$store && this.$store.state.i18n) {
          const state = this.$store.state.i18n
          const translations = state.translations[state.currentLanguage] || state.translations['ru'] || {}
          let text = translations[key] || key
          
          // Подстановка параметров
          Object.keys(params).forEach(param => {
            text = text.replace(new RegExp(`{${param}}`, 'g'), params[param])
          })
          
          return text
        }
        
        return key
      } catch (error) {
        console.error('Translation error:', error)
        return key
      }
    },
    
    // Метод для получения текущего языка
    $getLanguage() {
      if (this.$store && this.$store.state.i18n) {
        return this.$store.state.i18n.currentLanguage
      }
      return 'ru'
    }
  }
}
