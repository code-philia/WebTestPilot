import React from "react";
import { TestEditor } from "./pages/TestEditor";
import "./App.css";
import SingleRunner from "./pages/SingleRunner";

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
  const page = window.__PAGE__ || "testEditor";

  switch (page) {
    case "testEditor":
      return <TestEditor />;
    case "singleRunner":
      return <SingleRunner />;

    // Future pages will be added here:
    // case 'import': return <Import />;
    // case 'parallelRunner': return <ParallelRunner />;

    default:
      return (
        <div style={{ padding: "20px", textAlign: "center" }}>
          <h2>Unknown Page</h2>
          <p>Page "{page}" not found</p>
        </div>
      );
  }
};

export default App;
