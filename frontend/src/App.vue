<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <h1>AI 模型中转站</h1>
        </div>
        <div class="header-right">
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="header-menu"
          >
            <el-menu-item index="/logs">
              <el-icon><Document /></el-icon>
              <span>请求日志</span>
            </el-menu-item>
            <el-menu-item index="/config">
              <el-icon><Setting /></el-icon>
              <span>配置管理</span>
            </el-menu-item>
            <el-menu-item index="/stats">
              <el-icon><DataAnalysis /></el-icon>
              <span>统计监控</span>
            </el-menu-item>
            <el-menu-item index="/test">
              <el-icon><Promotion /></el-icon>
              <span>API 测试</span>
            </el-menu-item>
            <el-menu-item index="/whitelist">
              <el-icon><Lock /></el-icon>
              <span>IP 白名单</span>
            </el-menu-item>
          </el-menu>
          <el-button
            :icon="themeStore.isDark ? Sunny : Moon"
            circle
            @click="themeStore.toggleTheme"
            class="theme-toggle"
          />
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Setting, DataAnalysis, Promotion, Sunny, Moon, Lock } from '@element-plus/icons-vue'
import { useThemeStore } from './store/theme'

const route = useRoute()
const activeMenu = computed(() => route.path)
const themeStore = useThemeStore()
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

.app-header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 100%;
}

.header-left h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-menu {
  border-bottom: none;
  background-color: transparent;
}

.theme-toggle {
  margin-left: 12px;
}

.app-main {
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: calc(100vh - 60px);
  transition: background-color 0.3s ease;
}

</style>

<style>
/* 暗黑模式样式（全局样式） */
.dark .header-left h1 {
  background: linear-gradient(135deg, #66b1ff 0%, #85ce61 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>

