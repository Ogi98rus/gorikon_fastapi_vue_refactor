import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import MathGenerator from '../views/MathGenerator.vue'
import KtpGenerator from '../views/KtpGenerator.vue'
import MathGame from '../views/MathGame.vue'

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
    path: '/math-game',
    name: 'MathGame',
    component: MathGame,
    meta: {
      title: 'Математическая игра - Развитие навыков',
      description: 'Увлекательная игра для развития математических способностей с настраиваемыми параметрами'
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
router.beforeEach((to, from, next) => {
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
  
  next()
})



export default router 