import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    plugins: [react(), tailwindcss()],
    server: {
        port: 5173,
    },
    test: {
        globals: true,
        environment: "jsdom",
        setupFiles: "./src/test/setup.ts",
        coverage: {
            provider: "v8",
            reporter: ["text", "html"],
            exclude: [
                "src/test/**",
                "src/main.tsx",
                "src/vite-env.d.ts",
                "*.config.*",
            ],
        },
    },
});
