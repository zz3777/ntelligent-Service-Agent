import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function sendMessage(conversationId, message) {
  const res = await api.post('/chat', { conversation_id: conversationId, message })
  return res.data
}

export async function listConversations() {
  const res = await api.get('/chat/conversations')
  return res.data
}

export async function getConversationMessages(convId) {
  const res = await api.get(`/chat/conversations/${convId}/messages`)
  return res.data
}

export async function deleteConversation(convId) {
  const res = await api.delete(`/chat/conversations/${convId}`)
  return res.data
}

export function streamMessage(conversationId, message, onChunk, onDone) {
  fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, message }),
  }).then(async (response) => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            onDone()
            return
          }
          try {
            const parsed = JSON.parse(data)
            onChunk(parsed)
          } catch {}
        }
      }
    }
    onDone()
  })
}
