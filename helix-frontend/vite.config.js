import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  cacheDir: '.vite-cache',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        chat: resolve(__dirname, 'chat.html'),
        about: resolve(__dirname, 'about.html'),
      },
    },
    emptyOutDir: false,
  },
})
