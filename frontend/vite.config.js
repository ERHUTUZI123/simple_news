import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/news': 'http://127.0.0.1:8000'
    }
  },
  plugins: [react()],
})

