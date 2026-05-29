import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function listTasks(params = {}) {
  const res = await api.get('/tasks', { params })
  return res.data
}

export async function getTaskDetail(taskId) {
  const res = await api.get(`/tasks/${taskId}`)
  return res.data
}

export async function listApprovals(params = {}) {
  const res = await api.get('/approvals', { params })
  return res.data
}

export async function approveApproval(id, comment) {
  const res = await api.post(`/approvals/${id}/approve`, { comment })
  return res.data
}

export async function rejectApproval(id, comment) {
  const res = await api.post(`/approvals/${id}/reject`, { comment })
  return res.data
}
