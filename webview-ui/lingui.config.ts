import { LinguiConfig } from "@lingui/conf";

const config: Partial<LinguiConfig> = {
  locales: ["en", "zh"],
  sourceLocale: "en",
  catalogs: [
    {
      path: "<rootDir>/src/locales/{locale}/messages",
      include: ["src"],
      exclude: ["**/node_modules/**"],
    },
  ],
  format: "po",
};

export default config;
