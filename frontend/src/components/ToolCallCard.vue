<template>
  <div class="tool-call-card">
    <div class="header">
      <el-tag type="warning" size="small">工具调用</el-tag>
      <span class="tool-name">{{ toolName }}</span>
      <el-tag :type="status === 'success' ? 'success' : 'danger'" size="small">{{ status }}</el-tag>
    </div>
    <div class="body" v-if="params">
      <div class="label">参数:</div>
      <pre>{{ params }}</pre>
    </div>
    <div class="body" v-if="result">
      <div class="label">结果:</div>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
defineProps({
  toolName: String,
  params: String,
  result: String,
  status: { type: String, default: 'success' },
})
</script>

<style scoped>
.tool-call-card {
  background: #fafafa; border: 1px solid #e6e6e6; border-radius: 8px;
  padding: 12px; margin: 8px 0; font-size: 13px;
}
.header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.tool-name { font-weight: bold; color: #e6a23c; }
.body { margin-top: 4px; }
.label { color: #999; font-size: 12px; }
pre { background: #f5f5f5; padding: 8px; border-radius: 4px; font-size: 12px; white-space: pre-wrap; }
</style>
