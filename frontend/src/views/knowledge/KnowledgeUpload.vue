<template>
  <div>
    <el-upload
      drag
      :auto-upload="false"
      :on-change="handleUpload"
      multiple
      accept=".pdf,.docx,.doc,.xlsx,.xls,.png,.jpg,.jpeg,.bmp"
    >
      <el-icon><UploadFilled /></el-icon>
      <div>拖拽文件到此处，或点击上传</div>
      <template #tip>
        <div>支持 PDF、Word、Excel、图片格式</div>
      </template>
    </el-upload>

    <div v-for="item in uploadList" :key="item.filename" style="margin-top: 12px; padding: 12px; background: #f5f5f5; border-radius: 4px">
      <div>{{ item.filename }} <el-tag :type="item.status === 'ready' ? 'success' : 'warning'" size="small">{{ item.status }}</el-tag></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadDocument } from '../../api/knowledge'
import { UploadFilled } from '@element-plus/icons-vue'

const uploadList = ref([])

async function handleUpload(file) {
  uploadList.value.push({ filename: file.name, status: 'uploading' })
  try {
    const doc = await uploadDocument(file.raw)
    uploadList.value = uploadList.value.map(item =>
      item.filename === file.name ? { ...item, status: doc.status } : item
    )
  } catch {
    uploadList.value = uploadList.value.map(item =>
      item.filename === file.name ? { ...item, status: 'failed' } : item
    )
  }
}
</script>
