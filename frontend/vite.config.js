import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild', // 使用 esbuild 而不是 terser（更快，无需额外依赖）
    // 禁用构建缓存，确保每次都是全新构建
    emptyOutDir: true,
    // 确保生产环境变量正确设置
    define: {
      'import.meta.env.PROD': JSON.stringify(process.env.NODE_ENV === 'production')
    },
    // 确保文件哈希正确生成
    rollupOptions: {
      output: {
        // 确保每次构建都生成新的文件名
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

