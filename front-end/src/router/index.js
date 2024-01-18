import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/introduction',
    children: [{
      path: 'introduction',
      name: 'Introduction',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '系统介绍', icon: 'hello' }
    }]
  },

  {
    path: '/automatic',
    component: () => import('@/layout/AutomaticLayout/index.vue'),
    redirect: '/automatic/automatic-first',
    name: 'Automatic',
    meta: { title: '智能控制模式', icon: 'automatic' },
    children: [
      {
        path: 'automatic-first',
        name: 'Automatic-First',
        component: () => import('@/views/automatic/automatic-first/index.vue'),
        meta: { title: '智能体交互', icon: 'agent' }
      },
      {
        path: 'automatic-second',
        name: 'Automatic-Second',
        component: () => import('@/views/automatic/automatic-second/index.vue'),
        meta: { title: '环境信息', icon: 'environment' }
      },
      {
        path: 'automatic-third',
        name: 'Automatic-Third',
        component: () => import('@/views/automatic/automatic-third/index.vue'),
        meta: { title: '参数绘图', icon: 'draw' }
      }
    ]
  },

  {
    path: '/expert',
    component: () => import('@/layout/AutomaticLayout/index.vue'),
    redirect: '/expert/expert-first',
    name: 'Expert',
    meta: { title: '专家模式', icon: 'expert' },
    children: [
      {
        path: 'expert-first',
        name: 'Expert-First',
        component: () => import('@/views/expert/expert-first/index.vue'),
        meta: { title: '专家决策', icon: 'eye-open' }
      },
      {
        path: 'expert-second',
        name: 'Expert-Second',
        component: () => import('@/views/automatic/automatic-second/index.vue'),
        meta: { title: '环境信息', icon: 'environment' }
      },
      {
        path: 'expert-third',
        name: 'Expert-Third',
        component: () => import('@/views/automatic/automatic-third/index.vue'),
        meta: { title: '参数绘图', icon: 'draw' }
      }
    ]
  },

  // {
  //   path: 'external-link',
  //   component: Layout,
  //   children: [
  //     {
  //       path: 'https://panjiachen.github.io/vue-element-admin-site/#/',
  //       meta: { title: 'External Link', icon: 'link' }
  //     }
  //   ]
  // },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()
router.afterEach((to, from) => {
  // console.log(to.matched)
  // console.log(to.matched[0].path)
  // console.log(from)
  if (to.matched[0].path === '/automatic') {
    router.app.$store.commit('wsdata/updateOperatingMode', 'automatic')
  }
  if (to.matched[0].path === '/expert') {
    router.app.$store.commit('wsdata/updateOperatingMode', 'expert')
  }
})

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
