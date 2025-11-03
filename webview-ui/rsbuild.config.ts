import { defineConfig } from "@rsbuild/core";
import { pluginPreact } from "@rsbuild/plugin-preact";

export default defineConfig({
  plugins: [pluginPreact()],
  html: {
    template: "./index.html",
  },
  source: {
    entry: {
      index: "./src/index.tsx",
    },
    exclude: ["*.po"],
  },
  resolve: {
    extensions: [".js", ".ts", ".tsx", ".jsx"],
  },
  security: {
    nonce: "webtestpilot",
  },
  tools: {
    swc: {
      sourceMaps: true,
      jsc: {
        parser: {
          syntax: "typescript",
          tsx: true,
        },
        experimental: {
          plugins: [["@lingui/swc-plugin", {}]],
        },
      },
    },
    rspack: {
      output: {
        asyncChunks: false,
      },
    },
  },
});
