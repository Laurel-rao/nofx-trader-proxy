import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    providers: []
  }),
  
  actions: {
    async fetchProviders() {
      // 将在组件中直接调用 API
    }
  }
})

