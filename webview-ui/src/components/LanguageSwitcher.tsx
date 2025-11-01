import React, { useState } from "react";
import { changeLocale, getCurrentLocale, locales, SupportedLocale } from "../i18n";

interface LanguageSwitcherProps {
  className?: string;
}

/**
 * LanguageSwitcher Component
 * Provides a dropdown to switch between supported languages
 */
export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = "" }) => {
  const [isChanging, setIsChanging] = useState(false);

  const handleLocaleChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = event.target.value as SupportedLocale;
    setIsChanging(true);
    try {
      await changeLocale(newLocale);
    } catch (error) {
      console.error("Failed to change locale:", error);
    } finally {
      setIsChanging(false);
    }
  };

  return (
    <div className={`language-switcher ${className}`}>
      <select
        value={getCurrentLocale()}
        onChange={handleLocaleChange}
        disabled={isChanging}
        className="language-select"
        style={{
          padding: "4px 8px",
          borderRadius: "4px",
          border: "1px solid var(--vscode-input-border)",
          backgroundColor: "var(--vscode-input-background)",
          color: "var(--vscode-input-foreground)",
          cursor: isChanging ? "wait" : "pointer",
        }}
      >
        {Object.entries(locales).map(([code, name]) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
};
