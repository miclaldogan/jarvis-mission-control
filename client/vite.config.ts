import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

const devProxyTarget = process.env.VITE_DEV_PROXY_TARGET || 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: devProxyTarget,
        changeOrigin: true,
      },
      '/health': {
        target: devProxyTarget,
        changeOrigin: true,
      },
      '/metrics': {
        target: devProxyTarget,
        changeOrigin: true,
      },
    },
  },
})
