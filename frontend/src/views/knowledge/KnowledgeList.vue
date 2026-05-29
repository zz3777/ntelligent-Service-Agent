<template>
  <div>
    <div style="margin-bottom: 16px; display: flex; gap: 12px">
      <el-button type="primary" @click="$router.push('/knowledge/upload')">上传文档</el-button>
      <el-button @click="showQuickExtract = true">快速提取文字</el-button>
      <el-button @click="showTestSearch = true">测试检索</el-button>
    </div>

    <el-table :data="store.documents" v-loading="store.loading" style="width: 100%">
      <el-table-column prop="filename" label="文件名" />
      <el-table-column prop="file_type" label="类型" width="80" />
      <el-table-column prop="file_size" label="大小" width="100">
        <template #default="{ row }">{{ (row.file_size / 1024).toFixed(1) }} KB</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === 'ready' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="chunk_count" label="切片数" width="80" />
      <el-table-column prop="created_at" label="上传时间" width="180" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button text type="primary" @click="viewChunks(row)">切片</el-button>
          <el-button text type="danger" @click="store.removeDocument(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showQuickExtract" title="快速提取文字" width="600px">
      <el-upload drag :auto-upload="false" :on-change="handleQuickExtract">
        <el-icon><UploadFilled /></el-icon>
        <div>拖拽文件到此处，或点击上传</div>
      </el-upload>
      <pre v-if="extractedText" style="margin-top: 12px; background: #f5f5f5; padding: 12px; max-height: 300px; overflow-y: auto">{{ extractedText }}</pre>
    </el-dialog>

    <el-dialog v-model="showTestSearch" title="测试检索" width="500px">
      <el-input v-model="searchQuery" placeholder="输入测试文字" />
      <el-button @click="doTestSearch" style="margin-top: 8px">检索</el-button>
      <div v-for="r in searchResults" :key="r.content" style="margin-top: 8px; padding: 8px; background: #f5f5f5; border-radius: 4px">
        <div>{{ r.content }}</div>
        <el-tag size="small">得分: {{ r.score.toFixed(3) }}</el-tag>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useKnowledgeStore } from '../../stores/knowledge'
import { testSearch } from '../../api/knowledge'
import { UploadFilled } from '@element-plus/icons-vue'

const store = useKnowledgeStore()
const showQuickExtract = ref(false)
const extractedText = ref('')
const showTestSearch = ref(false)
const searchQuery = ref('')
const searchResults = ref([])

onMounted(() => store.fetchDocuments())

function viewChunks(row) { /* 后续实现 */ }

async function handleQuickExtract(file) {
  const formData = new FormData()
  formData.append('file', file.raw)
  const res = await fetch('/api/files/upload-temp', { method: 'POST', body: formData })
  const data = await res.json()
  extractedText.value = data.text
}

async function doTestSearch() {
  searchResults.value = await testSearch(searchQuery.value)
}
</script>
