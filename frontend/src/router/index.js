import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import TherapyChat from '../views/TherapyChat.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/therapy',
      name: 'therapy',
      component: TherapyChat
    }
  ]
})

export default router









// import { createRouter, createWebHistory } from 'vue-router'
// import HomePage from '../views/HomePage.vue'
// import TherapyChat from '../views/TherapyChat.vue'
// import Test from '../views/Test.vue'


// const router = createRouter({
//   history: createWebHistory(import.meta.env.BASE_URL),
//   routes: [
//     {
//       path: '/',
//       name: 'home',
//       component: HomePage,
//     },
//     {
//       path: '/therapy',
//       name: 'TherapyChat',
//       component: TherapyChat
//     },
//     {
//       path: '/about',
//       name: 'about',
//       // route level code-splitting
//       // this generates a separate chunk (About.[hash].js) for this route
//       // which is lazy-loaded when the route is visited.
//       component: () => import('../views/AboutView.vue'),
//     },
//     {
//       path: '/therapy',
//       component: Test
//     }
//   ],
// })

// export default router
