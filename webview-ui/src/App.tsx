import React, { useEffect, useState } from "react";
import { I18nProvider } from "@lingui/react";
import { i18n } from "@lingui/core";
import { TestEditor } from "./pages/TestEditor";
import { FixtureEditor } from "./pages/FixtureEditor";
import { EnvironmentEditor } from "./pages/EnvironmentEditor";
import "./App.css";
import SingleRunner from "./pages/SingleRunner";
import ParallelRunner from "./pages/ParallelRunner";
import { initI18n } from "./i18n";
import { I18nContextProvider } from "./contexts/I18nContext";
import { LanguageSwitcher } from "./components/LanguageSwitcher";

// Global window interface for page routing
declare global {
  interface Window {
    __PAGE__?: string;
  }
}

/**
 * App Component
 * Routes to the appropriate page based on window.__PAGE__
 */
const App: React.FC = () => {
  const [isI18nLoaded, setIsI18nLoaded] = useState(false);
  const page = window.__PAGE__ || "testEditor";

  useEffect(() => {
    // Initialize i18n when app loads
    initI18n().then(() => {
      setIsI18nLoaded(true);
    });
  }, []);

  if (!isI18nLoaded) {
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        Loading...
      </div>
    );
  }

  let content;
  switch (page) {
    case "testEditor":
      content = <TestEditor />;
      break;
    case "fixtureEditor":
      content = <FixtureEditor />;
      break;
    case "environmentEditor":
      content = <EnvironmentEditor />;
      break;
    case "singleRunner":
      content = <SingleRunner />;
      break;
    case "parallelRunner":
      content = <ParallelRunner />;
      break;

    // Future pages will be added here:
    // case 'import': return <Import />;

    default:
      content = (
        <div style={{ padding: "20px", textAlign: "center" }}>
          <h2>Unknown Page</h2>
          <p>{`Page "${page}" not found`}</p>
        </div>
      );
  }

  return (
    <I18nProvider i18n={i18n}>
      <I18nContextProvider>
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "8px" }}>
          <LanguageSwitcher />
        </div>
        {content}
      </I18nContextProvider>
    </I18nProvider>
  );
};

export default App;
