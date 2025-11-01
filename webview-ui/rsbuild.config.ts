import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";

export default defineConfig({
  plugins: [pluginReact()],
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
  performance: {
    preload: {
      type: "async-chunks",
    },
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
