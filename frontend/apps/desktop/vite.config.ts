import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "node:path";

export default defineConfig({
  plugins: [vue()],
  root: resolve(__dirname, "src/renderer"),
  base: "./",
  resolve: {
    alias: {
      "@vrm/platform-contracts": resolve(
        __dirname,
        "../../packages/platform-contracts/src",
      ),
      "@vrm/shared": resolve(__dirname, "../../packages/shared/src"),
      "@vrm/app-core": resolve(__dirname, "../../packages/app-core/src"),
      "@vrm/ui": resolve(__dirname, "../../packages/ui/src"),
    },
  },
  build: {
    outDir: resolve(__dirname, "dist"),
    emptyOutDir: true,
    sourcemap: true,
  },
});
