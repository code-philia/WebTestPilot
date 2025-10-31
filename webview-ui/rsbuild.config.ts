import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";

export default defineConfig({
  plugins: [pluginReact()],
  // output: {
  //   filenameHash: false,
  // },
  html: {
    template: "./index.html",
  },
  source: {
    entry: {
      index: "./src/index.tsx",
    },
  },
});
