<template>
  <div style="max-width: 600px">
    <el-card>
      <template #header>LLM 配置</template>
      <el-alert type="info" :closable="false" style="margin-bottom: 20px">
        LLM 配置通过后端 .env 文件管理，请在 backend/.env 中修改后重启后端服务。
      </el-alert>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="模型">{{ info.model || '未配置' }}</el-descriptions-item>
        <el-descriptions-item label="API Base URL">{{ info.baseUrl || '未配置' }}</el-descriptions-item>
        <el-descriptions-item label="API Key">{{ info.apiKey || '未配置' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="info.apiKey ? 'success' : 'danger'">
            {{ info.apiKey ? '已配置' : '未配置' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'

const info = reactive({
  baseUrl: '',
  apiKey: '',
  model: '',
})

onMounted(async () => {
  try {
    const res = await fetch('/api/settings/llm')
    const data = await res.json()
    info.baseUrl = data.base_url || ''
    info.apiKey = data.api_key || ''
    info.model = data.model || ''
  } catch {
    // 后端未就绪
  }
})
</script>
