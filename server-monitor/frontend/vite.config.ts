import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/monitor/',
  server: {
    port: 3000,
    proxy: {
      '/monitor/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/monitor\/api\/v1/, '/api/v1'),
      },
    },
  },
});
