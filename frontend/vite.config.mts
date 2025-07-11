import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Bind to all available network interfaces
    port: 3058,
    proxy: {
      '/improve_model': 'http://0.0.0.0:8050',
      '/upload_zip': 'http://0.0.0.0:8050',
      '/list_images': 'http://0.0.0.0:8050',
      '/delete_image': 'http://0.0.0.0:8050',
      '/list_uploads': 'http://0.0.0.0:8050',
      '/delete_upload': 'http://0.0.0.0:8050',
      '/list_upload_folders': 'http://0.0.0.0:8050',
      '/delete_upload_folder': 'http://0.0.0.0:8050'
    }
  }
});