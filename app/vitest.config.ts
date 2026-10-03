import { defineConfig } from "vitest/config";

// Separate from vite.config.ts: the Cloudflare plugin isn't needed for unit tests.
export default defineConfig({
  test: { include: ["shared/**/*.test.ts", "src/**/*.test.ts"] },
});
