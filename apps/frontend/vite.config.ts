import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, lazyPlugins } from "vite-plus";

export default defineConfig({
  fmt: {
    ignorePatterns: ["src/client/**"],
  },
  lint: {
    jsPlugins: [{ name: "vite-plus", specifier: "vite-plus/oxlint-plugin" }],
    rules: { "vite-plus/prefer-vite-plus-imports": "error" },
    options: { typeAware: true, typeCheck: true },
    ignorePatterns: ["src/client/**"],
  },
  plugins: lazyPlugins(() => [tailwindcss(), reactRouter()]),
  resolve: {
    tsconfigPaths: true,
  },
});
