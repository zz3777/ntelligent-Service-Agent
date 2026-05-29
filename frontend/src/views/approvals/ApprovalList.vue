<template>
  <div>
    <el-table :data="store.approvals" v-loading="store.loading" style="width: 100%">
      <el-table-column prop="task_id" label="任务 ID" width="160" />
      <el-table-column prop="tool_name" label="工具" width="120" />
      <el-table-column prop="reason" label="原因" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'approved' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" v-if="hasPending">
        <template #default="{ row }">
          <el-button type="success" size="small" @click="handleAction(row.id, 'approve')">批准</el-button>
          <el-button type="danger" size="small" @click="handleAction(row.id, 'reject')">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useTaskStore } from '../../stores/task'
import { approveApproval, rejectApproval } from '../../api/task'

const store = useTaskStore()
const hasPending = computed(() => store.approvals.some(a => a.status === 'pending'))

onMounted(() => store.fetchApprovals({}))

async function handleAction(id, action) {
  if (action === 'approve') await approveApproval(id, '')
  else await rejectApproval(id, '')
  store.fetchApprovals({})
}
</script>
