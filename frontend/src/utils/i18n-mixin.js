import { mapState, mapGetters } from 'vuex'

export default {
  computed: {
    ...mapState('i18n', ['currentLanguage']),
    ...mapGetters('i18n', ['t', 'getCurrentLanguage'])
  },
  
  methods: {
    // Метод для получения перевода
    $t(key, params = {}) {
      return this.t(key, params)
    },
    
    // Метод для получения текущего языка
    $getLanguage() {
      return this.getCurrentLanguage()
    }
  }
}
