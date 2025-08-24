<template>
  <div class="advertisement-container">
    <div id="yandex_rtb_R-A-16924544-1"></div>
  </div>
</template>

<script>
export default {
  name: 'YandexAdvertisement',
  mounted() {
    this.initializeAdvertisement()
  },
  methods: {
    initializeAdvertisement() {
      // Проверяем, что API Яндекса загружен
      if (window.yaContextCb && window.Ya && window.Ya.Context) {
        window.yaContextCb.push(() => {
          // eslint-disable-next-line no-undef
          Ya.Context.AdvManager.render({
            "blockId": "R-A-16924544-1",
            "renderTo": "yandex_rtb_R-A-16924544-1"
          })
        })
      } else {
        // Если API еще не загружен, ждем его загрузки
        const checkYaAPI = setInterval(() => {
          if (window.yaContextCb && window.Ya && window.Ya.Context) {
            clearInterval(checkYaAPI)
            window.yaContextCb.push(() => {
              // eslint-disable-next-line no-undef
              Ya.Context.AdvManager.render({
                "blockId": "R-A-16924544-1",
                "renderTo": "yandex_rtb_R-A-16924544-1"
              })
            })
          }
        }, 100)
        
        // Останавливаем проверку через 10 секунд
        setTimeout(() => clearInterval(checkYaAPI), 10000)
      }
    }
  }
}
</script>

<style scoped>
/* Стили для рекламы */
.advertisement-container {
  margin-top: 30px;
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.advertisement-container #yandex_rtb_R-A-16924544-1 {
  display: inline-block;
  margin: 0 auto;
}

/* Адаптивность для рекламы */
@media (max-width: 768px) {
  .advertisement-container {
    padding: 15px;
    margin: 20px 15px;
  }
}

@media (max-width: 480px) {
  .advertisement-container {
    padding: 15px;
    margin: 15px 10px;
  }
}
</style>