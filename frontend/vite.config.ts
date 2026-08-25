import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        host: true,
        port: 5173,
        watch: {
            usePolling: true, // Needed for Docker
        },
        proxy: {
            // Proxy all /api requests to the backend.
            // Browser calls GET /api/v1/health → Vite forwards to http://localhost:8000/api/v1/health
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
})