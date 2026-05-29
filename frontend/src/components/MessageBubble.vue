<template>
  <div :class="['message-bubble', role]">
    <div class="avatar">
      <el-avatar :icon="role === 'user' ? 'UserFilled' : 'ChatDotRound'" :style="role === 'user' ? {} : { background: '#409EFF' }" />
    </div>
    <div class="content">
      <TypewriterText
        v-if="role === 'assistant' && streaming"
        :content="content"
        :streaming="streaming"
      />
      <div v-else v-html="renderedContent" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import TypewriterText from './TypewriterText.vue'

const props = defineProps({
  role: { type: String, default: 'user' },
  content: { type: String, default: '' },
  streaming: { type: Boolean, default: false },
})

const renderedContent = computed(() => marked(props.content))
</script>

<style scoped>
.message-bubble { display: flex; margin-bottom: 16px; gap: 12px; }
.message-bubble.user { flex-direction: row-reverse; }
.content {
  max-width: 70%; padding: 12px 16px; border-radius: 8px; line-height: 1.6;
  background: v-bind('props.role === "user" ? "#409EFF" : "#fff"');
  color: v-bind('props.role === "user" ? "#fff" : "#333"');
  border: v-bind('props.role === "user" ? "none" : "1px solid #e6e6e6"');
}
.content :deep(pre) { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; }
.content :deep(code) { font-size: 14px; }
</style>
