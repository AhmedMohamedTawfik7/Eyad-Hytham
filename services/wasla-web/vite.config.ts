import { readFileSync } from "node:fs";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

const certificatePath = process.env.WASLA_TLS_CERT;
const privateKeyPath = process.env.WASLA_TLS_KEY;
const https = certificatePath && privateKeyPath
  ? { cert: readFileSync(certificatePath), key: readFileSync(privateKeyPath) }
  : undefined;

export default defineConfig(({ command }) => {
  if (command === "serve" && process.env.VITEST !== "true" && !https) {
    throw new Error("Vite requires WASLA_TLS_CERT and WASLA_TLS_KEY; run `python app.py --setup-tls`.");
  }
  return {
    plugins: [react()],
    server: {
      host: "127.0.0.1",
      https,
      strictPort: false,
      watch: { ignored: ["**/android/**", "**/ios/**", "**/release/**"] },
    },
    test: { environment: "jsdom", setupFiles: "./src/testSetup.ts" },
  };
});
