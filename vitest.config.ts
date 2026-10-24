import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'node:path';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['frontend/**/*.spec.ts', 'backend/**/*.spec.ts', 'tests/**/*.spec.ts']
  },
  resolve: {
    alias: {
      '@vrm/platform-contracts': resolve(__dirname, 'frontend/packages/platform-contracts/src'),
      '@vrm/shared': resolve(__dirname, 'frontend/packages/shared/src'),
      '@vrm/app-core': resolve(__dirname, 'frontend/packages/app-core/src'),
      '@vrm/ui': resolve(__dirname, 'frontend/packages/ui/src'),
      '@vrm/backend': resolve(__dirname, 'backend/src')
    }
  }
});
