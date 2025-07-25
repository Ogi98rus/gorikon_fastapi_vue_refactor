<template>
  <div class="history-container">
    <!-- Header -->
    <div class="history-header">
      <div class="header-content">
        <h1>📊 История генераций</h1>
        <p>Все ваши сгенерированные файлы в одном месте</p>
      </div>
      
      <div class="header-actions">
        <router-link to="/profile" class="btn btn-secondary">
          👤 Назад к профилю
        </router-link>
      </div>
    </div>

    <!-- Статистика -->
    <div class="stats-row" v-if="profileStats">
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ profileStats.total_generations }}</div>
          <div class="stat-label">Всего генераций</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🧮</div>
        <div class="stat-content">
          <div class="stat-value">{{ profileStats.math_generations }}</div>
          <div class="stat-label">Математика</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <div class="stat-value">{{ profileStats.ktp_generations }}</div>
          <div class="stat-label">КТП</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📥</div>
        <div class="stat-content">
          <div class="stat-value">{{ profileStats.total_downloads }}</div>
          <div class="stat-label">Скачиваний</div>
        </div>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filters-section">
      <div class="filter-group">
        <label>🔍 Тип генератора:</label>
        <select v-model="selectedFilter" @change="handleFilterChange">
          <option value="">Все</option>
          <option value="math">📊 Математика</option>
          <option value="ktp">📅 КТП</option>
        </select>
      </div>
      
      <div class="filter-stats">
        Показано: {{ generations.length }} из {{ totalCount }}
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>⏳ Загрузка истории...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="hasError" class="error-state">
      <div class="error-icon">❌</div>
      <h3>Ошибка загрузки</h3>
      <p>{{ error }}</p>
      <button @click="loadHistory" class="btn btn-primary">
        🔄 Попробовать снова
      </button>
    </div>

    <!-- Пустое состояние -->
    <div v-else-if="generations.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h3>История пуста</h3>
      <p>У вас пока нет сохраненных генераций</p>
      <div class="empty-actions">
        <router-link to="/math" class="btn btn-primary">
          🧮 Создать математические задачи
        </router-link>
        <router-link to="/ktp" class="btn btn-primary">
          📅 Создать КТП
        </router-link>
      </div>
    </div>

    <!-- Список генераций -->
    <div v-else class="generations-list">
      <div
        v-for="generation in generations"
        :key="generation.id"
        class="generation-card"
        :class="{ 'unavailable': !generation.is_available }"
      >
        <!-- Иконка типа -->
        <div class="generation-icon">
          {{ generation.generator_type === 'math' ? '🧮' : '📅' }}
        </div>

        <!-- Информация о файле -->
        <div class="generation-info">
          <h3 class="file-name">{{ generation.original_file_name }}</h3>
          
          <div class="generation-meta">
            <span class="generation-type">
              {{ generation.generator_type === 'math' ? 'Математика' : 'КТП' }}
            </span>
            <span class="file-size">{{ formatFileSize(generation.file_size) }}</span>
            <span class="creation-date">{{ formatDate(generation.created_at) }}</span>
          </div>

          <div class="generation-details">
            <span v-if="generation.examples_generated" class="detail">
              📊 {{ generation.examples_generated }} примеров
            </span>
            <span v-if="generation.total_lessons" class="detail">
              📚 {{ generation.total_lessons }} уроков
            </span>
            <span class="detail">
              📥 {{ generation.download_count }} скачиваний
            </span>
          </div>

          <!-- Срок хранения -->
          <div v-if="generation.expires_at" class="expiry-info">
            <span class="expiry-label">🕒 Хранится до:</span>
            <span class="expiry-date" :class="{ 'expiring-soon': isExpiringSoon(generation.expires_at) }">
              {{ formatDate(generation.expires_at) }}
            </span>
          </div>
        </div>

        <!-- Действия -->
        <div class="generation-actions">
          <button
            v-if="generation.is_available"
            @click="downloadFile(generation.id)"
            class="btn btn-primary btn-sm"
            :disabled="downloadingIds.includes(generation.id)"
          >
            <span v-if="downloadingIds.includes(generation.id)">⏳ Скачивание...</span>
            <span v-else>📥 Скачать</span>
          </button>
          
          <button
            @click="showGenerationDetails(generation)"
            class="btn btn-secondary btn-sm"
          >
            👁️ Подробнее
          </button>
          
          <button
            @click="confirmDelete(generation)"
            class="btn btn-danger btn-sm"
          >
            🗑️ Удалить
          </button>
        </div>

        <!-- Статус недоступности -->
        <div v-if="!generation.is_available" class="unavailable-overlay">
          <span>⚠️ Файл недоступен</span>
        </div>
      </div>
    </div>

    <!-- Пагинация -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="!hasPrevPage"
        class="btn btn-secondary"
      >
        ⬅️ Предыдущая
      </button>
      
      <div class="page-info">
        Страница {{ currentPage }} из {{ totalPages }}
      </div>
      
      <button
        @click="changePage(currentPage + 1)"
        :disabled="!hasNextPage"
        class="btn btn-secondary"
      >
        Следующая ➡️
      </button>
    </div>

    <!-- Модальное окно с деталями -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📋 Детали генерации</h3>
          <button @click="closeDetailsModal" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body" v-if="selectedGeneration">
          <div class="detail-group">
            <label>📄 Имя файла:</label>
            <span>{{ selectedGeneration.original_file_name }}</span>
          </div>
          
          <div class="detail-group">
            <label>🔧 Тип генератора:</label>
            <span>{{ selectedGeneration.generator_type === 'math' ? 'Математический' : 'КТП' }}</span>
          </div>
          
          <div class="detail-group">
            <label>📏 Размер файла:</label>
            <span>{{ formatFileSize(selectedGeneration.file_size) }}</span>
          </div>
          
          <div class="detail-group">
            <label>📅 Дата создания:</label>
            <span>{{ formatDateTime(selectedGeneration.created_at) }}</span>
          </div>
          
          <div v-if="selectedGeneration.parameters" class="detail-group">
            <label>⚙️ Параметры генерации:</label>
            <pre class="parameters-json">{{ JSON.stringify(selectedGeneration.parameters, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>⚠️ Подтверждение удаления</h3>
          <button @click="closeDeleteModal" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body">
          <p>Вы уверены, что хотите удалить эту генерацию?</p>
          <p><strong>{{ generationToDelete?.original_file_name }}</strong></p>
          <p class="warning-text">Это действие нельзя отменить!</p>
        </div>
        
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-secondary">
            ❌ Отменить
          </button>
          <button @click="deleteGeneration" class="btn btn-danger" :disabled="isDeleting">
            <span v-if="isDeleting">⏳ Удаление...</span>
            <span v-else>🗑️ Удалить</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'UserHistory',
  
  data() {
    return {
      selectedFilter: '',
      downloadingIds: [],
      
      // Модальные окна
      showDetailsModal: false,
      selectedGeneration: null,
      showDeleteModal: false,
      generationToDelete: null,
      isDeleting: false
    }
  },

  computed: {
    ...mapGetters('history', [
      'generations', 'isLoading', 'error', 'hasError',
      'currentPage', 'totalPages', 'totalCount', 'hasNextPage', 'hasPrevPage',
      'profileStats'
    ]),
    ...mapGetters('auth', ['isAuthenticated'])
  },

  async mounted() {
    if (!this.isAuthenticated) {
      this.$router.push('/login')
      return
    }
    
    await this.loadHistory()
  },

  methods: {
    ...mapActions('history', [
      'fetchGenerations', 'fetchProfile', 'downloadGeneration', 
      'deleteGeneration', 'setFilterType'
    ]),

    async loadHistory() {
      try {
        // Загружаем профиль и историю параллельно
        await Promise.all([
          this.fetchProfile(),
          this.fetchGenerations({ 
            page: 1, 
            generator_type: this.selectedFilter || null 
          })
        ])
      } catch (error) {
        console.error('Error loading history:', error)
      }
    },

    async handleFilterChange() {
      await this.setFilterType(this.selectedFilter || null)
    },

    async changePage(page) {
      if (page < 1 || page > this.totalPages) return
      
      await this.fetchGenerations({
        page,
        generator_type: this.selectedFilter || null
      })
    },

    async downloadFile(generationId) {
      this.downloadingIds.push(generationId)
      
      try {
        const result = await this.downloadGeneration(generationId)
        
        this.$emit('notification', {
          message: `Файл "${result.filename}" успешно скачан!`,
          type: 'success'
        })
      } catch (error) {
        this.$emit('notification', {
          message: error.message || 'Ошибка скачивания файла',
          type: 'error'
        })
      } finally {
        this.downloadingIds = this.downloadingIds.filter(id => id !== generationId)
      }
    },

    showGenerationDetails(generation) {
      this.selectedGeneration = generation
      this.showDetailsModal = true
    },

    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedGeneration = null
    },

    confirmDelete(generation) {
      this.generationToDelete = generation
      this.showDeleteModal = true
    },

    closeDeleteModal() {
      this.showDeleteModal = false
      this.generationToDelete = null
      this.isDeleting = false
    },

    async deleteGeneration() {
      if (!this.generationToDelete) return
      
      this.isDeleting = true
      
      try {
        await this.deleteGeneration(this.generationToDelete.id)
        
        this.$emit('notification', {
          message: 'Генерация успешно удалена из истории',
          type: 'success'
        })
        
        this.closeDeleteModal()
      } catch (error) {
        this.$emit('notification', {
          message: error.message || 'Ошибка удаления генерации',
          type: 'error'
        })
      } finally {
        this.isDeleting = false
      }
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Б'
      const k = 1024
      const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    },

    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    isExpiringSoon(expiryDate) {
      const now = new Date()
      const expiry = new Date(expiryDate)
      const diffDays = (expiry - now) / (1000 * 60 * 60 * 24)
      return diffDays <= 3 && diffDays > 0
    }
  }
}
</script>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.header-content h1 {
  margin: 0 0 5px 0;
  color: var(--text-primary);
}

.header-content p {
  margin: 0;
  color: var(--text-secondary);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 15px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.generations-list {
  display: grid;
  gap: 20px;
}

.generation-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
  transition: transform 0.2s;
}

.generation-card:hover {
  transform: translateY(-2px);
}

.generation-card.unavailable {
  opacity: 0.6;
}

.generation-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.generation-info {
  flex: 1;
}

.file-name {
  margin: 0 0 10px 0;
  color: var(--text-primary);
  font-size: 1.2rem;
}

.generation-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.generation-meta span {
  background: var(--bg-primary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.generation-details {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.detail {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.expiry-info {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 0.85rem;
}

.expiry-date.expiring-soon {
  color: var(--warning-color);
  font-weight: bold;
}

.generation-actions {
  display: flex;
  gap: 10px;
  flex-direction: column;
  flex-shrink: 0;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.unavailable-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--warning-color);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-info {
  color: var(--text-secondary);
}

/* Состояния */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon, .error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

/* Модальные окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 20px;
}

.detail-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  align-items: flex-start;
}

.detail-group label {
  font-weight: bold;
  min-width: 150px;
  color: var(--text-primary);
}

.parameters-json {
  background: var(--bg-primary);
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
  max-width: 400px;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.warning-text {
  color: var(--warning-color);
  font-weight: bold;
}

/* Адаптивность */
@media (max-width: 768px) {
  .history-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .filters-section {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .generation-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .generation-actions {
    flex-direction: row;
    width: 100%;
  }
  
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style> 