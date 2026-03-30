import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import reactPlugin from "eslint-plugin-react";
import jsxA11y from "eslint-plugin-jsx-a11y";
import tseslint from "typescript-eslint";
import prettierConfig from "eslint-config-prettier";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
    globalIgnores(["dist", "node_modules", "vite.config.ts"]),
    {
        files: ["**/*.{ts,tsx}"],
        extends: [
            js.configs.recommended,
            tseslint.configs.strictTypeChecked,
            tseslint.configs.stylisticTypeChecked,
            reactHooks.configs.flat.recommended,
            reactRefresh.configs.vite,
            jsxA11y.flatConfigs.recommended,
            prettierConfig,
        ],
        plugins: {
            react: reactPlugin,
        },
        languageOptions: {
            ecmaVersion: 2023,
            globals: globals.browser,
            parserOptions: {
                project: ["./tsconfig.app.json"],
                tsconfigRootDir: import.meta.dirname,
            },
        },
        rules: {
            // Naming conventions (≈ Ruff N rules)
            "@typescript-eslint/naming-convention": [
                "error",
                {
                    selector: "variable",
                    format: ["camelCase", "PascalCase", "UPPER_CASE"],
                },
                {
                    selector: "function",
                    format: ["camelCase", "PascalCase"],
                },
                {
                    selector: "typeLike",
                    format: ["PascalCase"],
                },
                {
                    selector: "interface",
                    format: ["PascalCase"],
                },
            ],
            // No explicit any (≈ Ruff ANN rules)
            "@typescript-eslint/no-explicit-any": "error",
            // Unused vars (≈ Ruff F/ARG rules)
            "@typescript-eslint/no-unused-vars": [
                "error",
                { argsIgnorePattern: "^_" },
            ],
            // No non-null assertion — use proper null checks
            "@typescript-eslint/no-non-null-assertion": "error",
            // React JSX scope not needed in React 17+
            "react/react-in-jsx-scope": "off",
            // setState in effects is a common valid pattern (loading indicators)
            "react-hooks/set-state-in-effect": "off",
            // Clean Code regra 7: tamanho de arquivos (max 500 linhas)
            "max-lines": [
                "error",
                { max: 500, skipComments: true, skipBlankLines: true },
            ],
            // Clean Code regra 7: complexidade ciclomatica (equivalente ao xenon do backend)
            // Grau B do xenon = complexidade <= 10
            "complexity": ["error", 10],
        },
    },
    // Override para arquivos de teste — relaxa as regras de tipo estrito
    // que conflitam com os matchers do Vitest/jest-axe/MSW
    {
        files: ["**/*.test.{ts,tsx}", "src/test/**/*.{ts,tsx}"],
        rules: {
            "@typescript-eslint/no-unsafe-assignment": "off",
            "@typescript-eslint/no-unsafe-call": "off",
            "@typescript-eslint/no-unsafe-member-access": "off",
            "@typescript-eslint/no-unsafe-argument": "off",
            "@typescript-eslint/no-unsafe-return": "off",
            "@typescript-eslint/no-explicit-any": "off",
            "@typescript-eslint/no-unsafe-enum-comparison": "off",
        },
    },
]);
