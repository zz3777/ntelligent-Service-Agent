import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listTasks, listApprovals } from '../api/task'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const total = ref(0)
  const loading = ref(false)
  const approvals = ref([])
  const approvalTotal = ref(0)

  async function fetchTasks(params) {
    loading.value = true
    const data = await listTasks(params)
    tasks.value = data.items
    total.value = data.total
    loading.value = false
  }

  async function fetchApprovals(params) {
    const data = await listApprovals(params)
    approvals.value = data.items
    approvalTotal.value = data.total
  }

  return { tasks, total, loading, approvals, approvalTotal, fetchTasks, fetchApprovals }
})
