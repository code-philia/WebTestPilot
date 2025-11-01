import { i18n } from "@lingui/core";

export const locales = {
  en: "English",
  zh: "中文",
};

export type SupportedLocale = keyof typeof locales;

function detectLocaleFromVscodeLang(lang?: string): SupportedLocale | undefined {
  if (!lang || typeof lang !== "string") return undefined;
  const lower = lang.toLowerCase();
  if (lower.startsWith("zh")) return "zh";
  if (lower.startsWith("en")) return "en";
  return undefined;
}

/**
 * Load messages for a given locale
 */
export async function loadMessages(locale: SupportedLocale) {
  const { messages } = await import(`./locales/${locale}/messages.ts`);
  i18n.load(locale, messages);
  i18n.activate(locale);
}

/**
 * Initialize i18n with the default or stored locale
 */
export function initI18n(defaultLocale: SupportedLocale = "en") {
  // Try to get stored locale from localStorage first
  const storedLocale = localStorage.getItem("locale") as SupportedLocale | null;

  // If user hasn't stored a preference, try to detect VS Code language injected into the page
  if (storedLocale) {
    return loadMessages(storedLocale);
  }

  const vscodeLang = (window as any).__VSCODE_LANGUAGE__ as string | undefined;
  const detected = detectLocaleFromVscodeLang(vscodeLang);
  const initial = detected || defaultLocale;
  return loadMessages(initial);
}

/**
 * Change the active locale
 */
export async function changeLocale(locale: SupportedLocale) {
  await loadMessages(locale);
  localStorage.setItem("locale", locale);
}

/**
 * Get the current active locale
 */
export function getCurrentLocale(): SupportedLocale {
  return (i18n.locale as SupportedLocale) || "en";
}
