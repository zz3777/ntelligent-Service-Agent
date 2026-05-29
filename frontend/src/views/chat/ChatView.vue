<template>
  <div class="chat-layout">
    <!-- 左侧会话列表 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <el-button type="primary" @click="chatStore.newConversation" :icon="Plus" circle />
        <span class="sidebar-title">会话列表</span>
      </div>
      <div class="conv-list">
        <div
          v-for="conv in chatStore.conversations"
          :key="conv.id"
          :class="['conv-item', { active: chatStore.currentConversationId === conv.id }]"
          @click="chatStore.switchConversation(conv.id)"
        >
          <span class="conv-title">{{ conv.title }}</span>
          <el-button
            class="conv-delete"
            type="danger"
            :icon="Delete"
            size="small"
            circle
            plain
            @click.stop="chatStore.removeConversation(conv.id)"
          />
        </div>
        <div v-if="chatStore.conversations.length === 0" class="empty-tip">暂无会话</div>
      </div>
      <div class="sidebar-footer">
        <el-switch v-model="chatStore.memoryEnabled" active-text="记忆" inactive-text="无记忆" />
      </div>
    </div>

    <!-- 右侧聊天区 -->
    <div class="chat-main">
      <div class="message-list" ref="messageListRef">
        <div v-if="chatStore.currentMessages.length === 0" class="welcome">
          <div class="welcome-icon">🤖</div>
          <div class="welcome-text">企业智能服务 Agent</div>
          <div class="welcome-sub">有什么可以帮您？</div>
        </div>
        <MessageBubble
          v-for="(msg, i) in chatStore.currentMessages"
          :key="i"
          :role="msg.role"
          :content="msg.content"
        />
        <div v-if="chatStore.isProcessing" class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            :autosize="{ minRows: 1, maxRows: 6 }"
            placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
            @keydown.enter.exact.prevent="send"
            :disabled="chatStore.isProcessing"
          />
          <el-button
            type="primary"
            :icon="Promotion"
            circle
            class="send-btn"
            @click="send"
            :loading="chatStore.isProcessing"
            :disabled="!inputMessage.trim()"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { Plus, Delete, Promotion } from '@element-plus/icons-vue'
import { useChatStore } from '../../stores/chat'
import { streamMessage } from '../../api/chat'
import MessageBubble from '../../components/MessageBubble.vue'

const chatStore = useChatStore()
const inputMessage = ref('')
const messageListRef = ref(null)

chatStore.loadConversations()

function scrollToBottom() {
  nextTick(() => {
    const el = messageListRef.value
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
    }
  })
}

watch(() => chatStore.currentMessages.length, scrollToBottom)
watch(() => {
  const msgs = chatStore.currentMessages
  if (msgs.length > 0) return msgs[msgs.length - 1].content
  return ''
}, scrollToBottom)

function send() {
  const text = inputMessage.value.trim()
  if (!text || chatStore.isProcessing) return

  chatStore.addMessage({ role: 'user', content: text })
  chatStore.addMessage({ role: 'assistant', content: '' })
  chatStore.setProcessing(true)
  inputMessage.value = ''

  const convId = chatStore.memoryEnabled ? chatStore.currentConversationId : null

  streamMessage(
    convId,
    text,
    (data) => {
      const msgs = chatStore.currentMessages
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        last.content += data.content
        scrollToBottom()
      }
      if (data.conversation_id && !chatStore.currentConversationId) {
        chatStore.currentConversationId = data.conversation_id
        chatStore.loadConversations()
      }
    },
    () => {
      chatStore.setProcessing(false)
      if (chatStore.currentConversationId) {
        chatStore.loadConversations()
      }
    }
  )
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: calc(100vh - 120px);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

/* 左侧会话列表 */
.sidebar {
  width: 240px;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}
.sidebar-header {
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #e8e8e8;
}
.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.conv-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  transition: background 0.2s;
}
.conv-item:hover {
  background: #e8e8e8;
}
.conv-item.active {
  background: #d0e8ff;
}
.conv-title {
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.conv-delete {
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}
.conv-item:hover .conv-delete {
  opacity: 1;
}
.empty-tip {
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 40px 0;
}
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #e8e8e8;
}

/* 右侧聊天区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}
.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.welcome-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.welcome-sub {
  font-size: 14px;
}

/* 输入区 */
.input-area {
  padding: 12px 20px 16px;
  border-top: 1px solid #e8e8e8;
}
.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 8px 12px;
}
.input-wrapper :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  box-shadow: none;
  resize: none;
  padding: 4px 0;
}
.send-btn {
  flex-shrink: 0;
}

/* 打字动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  margin-left: 48px;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409EFF;
  animation: bounce 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}
</style>
