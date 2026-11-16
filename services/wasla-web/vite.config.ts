import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: true,
    strictPort: false,
    watch: { ignored: ["**/android/**", "**/ios/**", "**/release/**"] },
  },
  test: { environment: "jsdom", setupFiles: "./src/testSetup.ts" },
});
