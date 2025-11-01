/**
 * Optional: Enhanced i18n context provider
 * 
 * This provides a React context for easier access to locale state and methods.
 * You can use this if you need to react to locale changes in your components.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { SupportedLocale, getCurrentLocale, changeLocale, locales } from "../i18n";

interface I18nContextValue {
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => Promise<void>;
  locales: typeof locales;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

interface I18nContextProviderProps {
  children: ReactNode;
}

/**
 * I18nContextProvider
 * Provides locale state and methods to all child components
 * 
 * Usage:
 * Wrap your app or specific sections with this provider:
 * 
 * <I18nContextProvider>
 *   <YourComponents />
 * </I18nContextProvider>
 * 
 * Then use the hook in any child component:
 * 
 * const { locale, setLocale, locales } = useI18nContext();
 */
export const I18nContextProvider: React.FC<I18nContextProviderProps> = ({ children }) => {
  const [locale, setLocaleState] = useState<SupportedLocale>(getCurrentLocale());

  const handleSetLocale = async (newLocale: SupportedLocale) => {
    await changeLocale(newLocale);
    setLocaleState(newLocale);
  };

  useEffect(() => {
    // Listen for locale changes from i18n
    const handleLocaleChange = () => {
      setLocaleState(getCurrentLocale());
    };

    // You could set up an event listener here if needed
    // For now, the state is managed through setLocale

    return () => {
      // Cleanup if needed
    };
  }, []);

  const value: I18nContextValue = {
    locale,
    setLocale: handleSetLocale,
    locales,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

/**
 * useI18nContext hook
 * Access the i18n context from any component
 * 
 * @returns {I18nContextValue} The i18n context value
 * @throws {Error} If used outside of I18nContextProvider
 * 
 * @example
 * const { locale, setLocale, locales } = useI18nContext();
 * 
 * Get current locale
 * console.log(locale); // "en" or "zh"
 * 
 * Change locale
 * await setLocale("zh");
 * 
 * Get available locales
 * Object.entries(locales).map(([code, name]) => ...)
 */
export const useI18nContext = (): I18nContextValue => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18nContext must be used within I18nContextProvider");
  }
  return context;
};

/**
 * Alternative: Simple custom hook without context
 * Use this if you don't want to add another provider
 */
export const useLocale = () => {
  const [locale, setLocaleState] = useState<SupportedLocale>(getCurrentLocale());

  const setLocale = async (newLocale: SupportedLocale) => {
    await changeLocale(newLocale);
    setLocaleState(newLocale);
  };

  return { locale, setLocale, locales };
};
