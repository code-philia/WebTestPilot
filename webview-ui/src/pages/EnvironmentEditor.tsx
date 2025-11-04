import React, {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
} from "react";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";
import { useVSCode } from "../hooks/useVSCode";
import type {
  EnvironmentEditorData,
  SaveEnvironmentPayload,
} from "../types";
import { useLingui } from "@lingui/react/macro";

const DEFAULT_DATA: EnvironmentEditorData = {
  id: undefined,
  folderId: undefined,
  name: "",
  environmentVariables: {},
};

function sanitizePayload(data: EnvironmentEditorData): SaveEnvironmentPayload {
  return {
    name: data.name.trim(),
    environmentVariables: data.environmentVariables,
  };
}

export const EnvironmentEditor: React.FC = () => {
  const { t } = useLingui();
  const { postMessage, onMessage, getState, setState } = useVSCode();
  const [environmentData, setEnvironmentData] = useState<EnvironmentEditorData>(
    () => getState() || DEFAULT_DATA
  );

  // Request initial data when component mounts
  useEffect(() => {
    postMessage("ready");
  }, [postMessage]);

  // Listen for messages from extension
  useEffect(() => {
    return onMessage((message: any) => {
      if (!message) return;

      if (message.command === "loadEnvironment" && message.environment) {
        const environment: EnvironmentEditorData = {
          id: message.environment.id,
          folderId: message.environment.folderId,
          name: message.environment.name || "",
          environmentVariables: message.environment.environmentVariables || {},
        };
        setEnvironmentData(environment);
        setState(environment);
      }
    });
  }, [onMessage, setState]);

  // Persist state changes
  useEffect(() => {
    setState(environmentData);
  }, [environmentData, setState]);

  // Update document title
  useEffect(() => {
    document.title = environmentData.name
      ? t`Edit Environment: ${environmentData.name}`
      : t`Edit Environment`;
  }, [environmentData.name]);

  // Event handlers
  const handleNameChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setEnvironmentData((prev) => ({ ...prev, name: value }));
      postMessage("updateEnvironment", { data: { name: value } });
    },
    [postMessage]
  );

  const handleAddVariable = useCallback(() => {
    setEnvironmentData((prev) => {
      // Generate a unique temporary key
      let tempKey = `NEW_VAR_${Date.now()}`;
      while (tempKey in prev.environmentVariables) {
        tempKey = `NEW_VAR_${Date.now()}_${Math.random()}`;
      }
      return {
        ...prev,
        environmentVariables: {
          ...prev.environmentVariables,
          [tempKey]: "",
        },
      };
    });
  }, []);

  const handleRemoveVariable = useCallback((key: string) => {
    setEnvironmentData((prev) => {
      const newVars = { ...prev.environmentVariables };
      delete newVars[key];
      return {
        ...prev,
        environmentVariables: newVars,
      };
    });
  }, []);

  const handleVariableKeyChange = useCallback(
    (oldKey: string, newKey: string) => {
      setEnvironmentData((prev) => {
        // If the key hasn't actually changed, don't update
        if (oldKey === newKey) {
          return prev;
        }
        
        const newVars: Record<string, string> = {};
        const value = prev.environmentVariables[oldKey];
        
        // Rebuild the object maintaining order
        for (const [k, v] of Object.entries(prev.environmentVariables)) {
          if (k === oldKey) {
            newVars[newKey] = value;
          } else {
            newVars[k] = v;
          }
        }
        
        return {
          ...prev,
          environmentVariables: newVars,
        };
      });
    },
    []
  );

  const handleVariableValueChange = useCallback((key: string, value: string) => {
    setEnvironmentData((prev) => ({
      ...prev,
      environmentVariables: {
        ...prev.environmentVariables,
        [key]: value,
      },
    }));
  }, []);

  const handleClose = useCallback(() => {
    postMessage("close");
  }, [postMessage]);

  const handleSave = useCallback(() => {
    const payload = sanitizePayload(environmentData);

    if (!payload.name) {
      postMessage("showError", { text: t`Environment name is required` });
      return;
    }

    postMessage("save", { data: payload });
  }, [environmentData, postMessage]);

  const variables = Object.entries(environmentData.environmentVariables);

  return (
    <main className="environment-editor">
      <header className="editor-header">
        <div className="editor-title">
          {environmentData.name
            ? t`Edit Environment: ${environmentData.name}`
            : t`Edit Environment`}
        </div>
        <div className="header-actions">
          <VSCodeButton appearance="primary" onClick={handleSave}>
            {t`Save Environment`}
          </VSCodeButton>
          <VSCodeButton appearance="secondary" onClick={handleClose}>
            {t`Close`}
          </VSCodeButton>
        </div>
      </header>

      <section className="editor-section">
        <label className="field-label" htmlFor="environment-name">
          {t`Environment Name`}
        </label>
        <input
          id="environment-name"
          className="text-input"
          value={environmentData.name}
          onChange={handleNameChange}
          placeholder={t`My Environment`}
        />
      </section>

      <section className="editor-section">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "8px",
          }}
        >
          <label className="field-label">{t`Environment Variables`}</label>
          <VSCodeButton appearance="secondary" onClick={handleAddVariable}>
            {t`Add Variable`}
          </VSCodeButton>
        </div>

        <table className="variables-table">
          <thead>
            <tr>
              <th>{t`Variable`}</th>
              <th>{t`Value`}</th>
              <th style={{ width: "60px" }}></th>
            </tr>
          </thead>
          <tbody>
            {variables.length === 0 ? (
              <tr>
                <td colSpan={3} style={{ textAlign: "center", padding: "20px" }}>
                  {t`No variables defined. Click "Add Variable" to create one.`}
                </td>
              </tr>
            ) : (
              variables.map(([key, value], index) => {
                // Use index as the stable key for React, and track the actual variable key separately
                const stableKey = `var-${index}`;
                return (
                  <tr key={stableKey}>
                    <td>
                      <input
                        type="text"
                        className="text-input"
                        value={key}
                        onChange={(e) =>
                          handleVariableKeyChange(key, e.target.value)
                        }
                        placeholder={t`VARIABLE_NAME`}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="text-input"
                        value={value}
                        onChange={(e) =>
                          handleVariableValueChange(key, e.target.value)
                        }
                        placeholder={t`value`}
                      />
                    </td>
                    <td>
                      <VSCodeButton
                        appearance="icon"
                        onClick={() => handleRemoveVariable(key)}
                        aria-label={t`Remove variable`}
                      >
                        <span className="codicon codicon-trash"></span>
                      </VSCodeButton>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </section>
    </main>
  );
};
