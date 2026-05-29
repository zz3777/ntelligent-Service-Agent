<template>
  <div>
    <el-form :inline="true" style="margin-bottom: 16px">
      <el-form-item label="状态">
        <el-select v-model="filter.status" clearable placeholder="全部" @change="search">
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="待审批" value="pending_approval" />
        </el-select>
      </el-form-item>
      <el-form-item label="工具">
        <el-input v-model="filter.tool_name" placeholder="工具名称" @keyup.enter="search" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="store.tasks" v-loading="store.loading" style="width: 100%">
      <el-table-column prop="task_id" label="任务 ID" width="160" />
      <el-table-column prop="action" label="操作" width="200" />
      <el-table-column prop="tool_name" label="工具" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration_ms" label="耗时(ms)" width="100" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :total="store.total"
      :page-size="20"
      layout="prev, pager, next"
      @change="search"
      style="margin-top: 16px"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useTaskStore } from '../../stores/task'

const store = useTaskStore()
const page = ref(1)
const filter = reactive({ status: '', tool_name: '' })

onMounted(() => search())

function search() {
  store.fetchTasks({ ...filter, page: page.value })
}
</script>
