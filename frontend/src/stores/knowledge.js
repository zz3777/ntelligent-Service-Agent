import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listDocuments, deleteDocument } from '../api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const documents = ref([])
  const loading = ref(false)

  async function fetchDocuments() {
    loading.value = true
    documents.value = await listDocuments()
    loading.value = false
  }

  async function removeDocument(id) {
    await deleteDocument(id)
    documents.value = documents.value.filter(d => d.id !== id)
  }

  return { documents, loading, fetchDocuments, removeDocument }
})
