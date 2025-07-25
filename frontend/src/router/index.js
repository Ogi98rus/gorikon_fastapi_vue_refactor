import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import MathGenerator from '../views/MathGenerator.vue'
import KtpGenerator from '../views/KtpGenerator.vue'
import Result from '../views/Result.vue'

// Auth components
import LoginForm from '../components/auth/LoginForm.vue'
import RegisterForm from '../components/auth/RegisterForm.vue'
import UserProfile from '../components/auth/UserProfile.vue'

// User views
import UserHistory from '../views/UserHistory.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

// Analytics views (будут созданы позже)
import AnalyticsDashboard from '../views/AnalyticsDashboard.vue'

// Store для проверки аутентификации
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'Главная - Генератор учебных материалов',
      description: 'Создавайте математические задачи и календарно-тематические планы'
    }
  },
  {
    path: '/math',
    name: 'MathGenerator',
    component: MathGenerator,
    meta: {
      title: 'Генератор математических задач',
      description: 'Создание упражнений по математике с настраиваемыми параметрами'
    }
  },
  {
    path: '/ktp',
    name: 'KtpGenerator', 
    component: KtpGenerator,
    meta: {
      title: 'Генератор КТП',
      description: 'Создание календарно-тематического планирования'
    }
  },
  {
    path: '/result',
    name: 'Result',
    component: Result,
    meta: {
      title: 'Результат генерации'
    }
  },
  
  // Auth routes
  {
    path: '/login',
    name: 'Login',
    component: LoginForm,
    meta: {
      title: 'Вход в систему',
      description: 'Войдите в свой аккаунт для доступа к дополнительным функциям',
      requiresGuest: true // Только для неавторизованных
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterForm,
    meta: {
      title: 'Регистрация',
      description: 'Создайте новый аккаунт для полного доступа к сервису',
      requiresGuest: true
    }
  },
  
  // Protected routes (требуют аутентификации)
  {
    path: '/profile',
    name: 'Profile',
    component: UserProfile,
    meta: {
      title: 'Профиль пользователя',
      description: 'Управление аккаунтом и просмотр статистики',
      requiresAuth: true
    }
  },
  {
    path: '/history',
    name: 'UserHistory',
    component: UserHistory,
    meta: {
      title: 'История генераций',
      description: 'Все ваши сгенерированные файлы и возможность их повторного скачивания',
      requiresAuth: true
    }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: AnalyticsDashboard,
    meta: {
      title: 'Аналитика и статистика',
      description: 'Подробная статистика использования сервиса',
      requiresAuth: true
    }
  },
        {
          path: '/admin',
          name: 'AdminDashboard',
          component: AdminDashboard,
          meta: {
            title: 'Панель администратора',
            description: 'Управление пользователями и системой',
            requiresAuth: true,
            requiresAdmin: true
          }
        },
  
  // Redirect old paths
  {
    path: '/math-generator',
    redirect: '/math'
  },
  {
    path: '/ktp-generator', 
    redirect: '/ktp'
  },
  
  // 404 page
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: 'Страница не найдена'
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  
  // Scroll behavior
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Устанавливаем заголовок страницы
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Устанавливаем мета-описание
  if (to.meta.description) {
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', to.meta.description)
    }
  }
  
  // Проверяем аутентификацию при первом запуске
  if (!store.state.auth.user && store.state.auth.token) {
    try {
      await store.dispatch('auth/initAuth')
    } catch (error) {
      console.log('Auth initialization failed:', error)
    }
  }
  
  const isAuthenticated = store.getters['auth/isAuthenticated']
  
  // Проверка для страниц, требующих аутентификации
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // Проверка для страниц, доступных только гостям (login, register)
  if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'Home' })
    return
  }
  
  // Проверка для админских страниц
  if (to.meta.requiresAdmin && isAuthenticated) {
    const isAdmin = store.getters['auth/isAdmin']
    
    if (!isAdmin) {
      next({ name: 'Home' })
      return
    }
  }
  
  next()
})

// После навигации
router.afterEach((to, from) => {
  // Логирование переходов между страницами для аналитики
  if (store.getters['auth/isAuthenticated']) {
    const pageView = {
      page: to.name,
      path: to.path,
      from_page: from.name,
      timestamp: new Date().toISOString()
    }
    
    // Отправляем данные в аналитику (если пользователь авторизован)
    store.dispatch('analytics/trackPageView', pageView).catch(error => {
      console.log('Analytics tracking failed:', error)
    })
  }
})

export default router 