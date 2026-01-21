import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../shared'),
    },
  },
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
