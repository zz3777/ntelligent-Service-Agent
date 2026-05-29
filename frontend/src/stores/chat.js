import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listConversations, getConversationMessages, deleteConversation } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversationId = ref(null)
  const currentMessages = ref([])
  const isProcessing = ref(false)
  const memoryEnabled = ref(true)

  async function loadConversations() {
    conversations.value = await listConversations()
  }

  async function switchConversation(convId) {
    currentConversationId.value = convId
    if (convId) {
      const msgs = await getConversationMessages(convId)
      currentMessages.value = msgs
    } else {
      currentMessages.value = []
    }
  }

  function newConversation() {
    currentConversationId.value = null
    currentMessages.value = []
  }

  function addMessage(msg) {
    currentMessages.value.push(msg)
  }

  function updateLastMessage(content) {
    if (currentMessages.value.length > 0) {
      currentMessages.value[currentMessages.value.length - 1].content = content
    }
  }

  function setProcessing(val) {
    isProcessing.value = val
  }

  async function removeConversation(convId) {
    await deleteConversation(convId)
    if (currentConversationId.value === convId) {
      newConversation()
    }
    await loadConversations()
  }

  return {
    conversations, currentConversationId, currentMessages,
    isProcessing, memoryEnabled,
    loadConversations, switchConversation, newConversation,
    addMessage, updateLastMessage, setProcessing, removeConversation,
  }
})
