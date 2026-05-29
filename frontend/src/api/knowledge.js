import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/knowledge/upload', formData)
  return res.data
}

export async function listDocuments() {
  const res = await api.get('/knowledge/list')
  return res.data
}

export async function deleteDocument(id) {
  const res = await api.delete(`/knowledge/${id}`)
  return res.data
}

export async function testSearch(query) {
  const res = await api.post('/knowledge/test-search', { query })
  return res.data
}
