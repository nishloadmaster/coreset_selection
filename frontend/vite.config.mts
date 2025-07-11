import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Bind to all available network interfaces
    port: 3058,
    proxy: {
      '/improve_model': 'http://0.0.0.0:8050'
    }
  }
});