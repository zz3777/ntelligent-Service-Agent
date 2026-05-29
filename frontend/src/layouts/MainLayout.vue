<template>
  <el-container style="height: 100vh">
    <el-aside v-if="!isChat" width="220px" style="background-color: #304156">
      <div class="logo">企业智能 Agent</div>
      <el-menu
        :default-active="route.path"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能对话</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Document /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务审计</span>
        </el-menu-item>
        <el-menu-item index="/approvals">
          <el-icon><CircleCheck /></el-icon>
          <span>审批待办</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统状态</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header v-if="!isChat" style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: flex-end">
        <span>管理员</span>
      </el-header>
      <el-main :style="isChat ? { padding: 0, background: '#f0f2f5' } : { background: '#f0f2f5' }">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChatDotRound, Document, List, CircleCheck, Setting } from '@element-plus/icons-vue'
const route = useRoute()
const isChat = computed(() => route.path === '/chat')
</script>

<style scoped>
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
}
</style>
