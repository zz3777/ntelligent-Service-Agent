import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/chat' },
      { path: 'chat', name: 'Chat', component: () => import('../views/chat/ChatView.vue') },
      { path: 'knowledge', name: 'Knowledge', component: () => import('../views/knowledge/KnowledgeList.vue') },
      { path: 'knowledge/upload', name: 'KnowledgeUpload', component: () => import('../views/knowledge/KnowledgeUpload.vue') },
      { path: 'tasks', name: 'Tasks', component: () => import('../views/tasks/TaskAudit.vue') },
      { path: 'approvals', name: 'Approvals', component: () => import('../views/approvals/ApprovalList.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/settings/SettingsView.vue') },
    ],
  },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
