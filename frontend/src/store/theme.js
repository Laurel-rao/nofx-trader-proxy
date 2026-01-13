import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark' || false)
  
  // 切换主题
  function toggleTheme() {
    isDark.value = !isDark.value
    applyTheme()
  }
  
  // 应用主题
  function applyTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }
  
  // 初始化主题
  function initTheme() {
    applyTheme()
  }
  
  return {
    isDark,
    toggleTheme,
    initTheme
  }
})

