import React, {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
} from "react";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";
import { useVSCode } from "../hooks/useVSCode";
import { ActionList } from "../components/ActionList";
import type { TestAction, TestEditorData, SavePayload } from "../types";
import { useLingui } from "@lingui/react/macro";

const DEFAULT_DATA: TestEditorData = {
  id: undefined,
  folderId: undefined,
  name: "",
  url: "",
  actions: [],
};

function sanitizePayload(data: TestEditorData): SavePayload {
  return {
    name: data.name.trim(),
    url: data.url.trim(),
    actions: data.actions.map((action) => ({
      action: action.action.trim(),
      expectedResult: action.expectedResult.trim(),
    })),
  };
}

export const TestEditor: React.FC = () => {
  const { t } = useLingui();
  const { postMessage, onMessage, getState, setState } = useVSCode();
  const [testData, setTestData] = useState<TestEditorData>(
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

      if (message.command === "loadTest" && message.test) {
        const test: TestEditorData = {
          id: message.test.id,
          folderId: message.test.folderId,
          name: message.test.name || "",
          url: message.test.url || "",
          actions: message.test.actions || [],
        };
        setTestData(test);
        setState(test);
      }
    });
  }, [onMessage, setState]);

  // Persist state changes
  useEffect(() => {
    setState(testData);
  }, [testData, setState]);

  // Update document title
  useEffect(() => {
    document.title = testData.name
      ? t`Edit Test: ${testData.name}`
      : t`Edit Test`;
  }, [testData.name]);

  // Event handlers
  const handleNameChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setTestData((prev) => ({ ...prev, name: value }));
      postMessage("updateTest", { data: { name: value } });
    },
    [postMessage]
  );

  const handleUrlChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setTestData((prev) => ({ ...prev, url: value }));
      postMessage("updateTest", { data: { url: value } });
    },
    [postMessage]
  );

  const handleAddAction = useCallback(() => {
    setTestData((prev) => ({
      ...prev,
      actions: [...prev.actions, { action: "", expectedResult: "" }],
    }));
  }, []);

  const handleRemoveAction = useCallback((index: number) => {
    setTestData((prev) => ({
      ...prev,
      actions: prev.actions.filter((_, idx) => idx !== index),
    }));
  }, []);

  const handleActionChange = useCallback(
    (index: number, field: keyof TestAction, value: string) => {
      setTestData((prev) => ({
        ...prev,
        actions: prev.actions.map((action, idx) =>
          idx === index ? { ...action, [field]: value } : action
        ),
      }));
    },
    []
  );

  const handleClose = useCallback(() => {
    postMessage("close");
  }, [postMessage]);

  const persistSanitizedState = useCallback((payload: SavePayload) => {
    setTestData((prev) => ({
      ...prev,
      name: payload.name,
      url: payload.url,
      actions: payload.actions,
    }));
  }, []);

  const handleSave = useCallback(() => {
    const payload = sanitizePayload(testData);

    if (!payload.name) {
      postMessage("showError", { text: t`Test name is required` });
      return;
    }

    persistSanitizedState(payload);
    postMessage("save", { data: payload });
  }, [persistSanitizedState, testData, postMessage]);

  const handleRunTest = useCallback(() => {
    const payload = sanitizePayload(testData);

    if (payload.actions.length === 0) {
      postMessage("showError", {
        text: t`Cannot run test: No actions defined. Please add test actions before running.`,
      });
      return;
    }

    const hasEmptyActions = payload.actions.some(
      (action) => !action.action || action.action.length === 0
    );

    if (hasEmptyActions) {
      postMessage("showError", {
        text: t`Cannot run test: Some actions are empty. Please fill in all action descriptions.`,
      });
      return;
    }

    persistSanitizedState(payload);
    postMessage("saveAndRun", { data: payload });
  }, [persistSanitizedState, testData, postMessage]);

  return (
    <main className="test-editor">
      <header className="editor-header">
        <div className="editor-title">
          {testData.name ? t`Edit Test: ${testData.name}` : t`Edit Test`}
        </div>
        <div className="header-actions">
          <VSCodeButton appearance="primary" onClick={handleSave}>
            {t`Save Test`}
          </VSCodeButton>
          <VSCodeButton appearance="secondary" onClick={handleRunTest}>
            {t`Run Test`}
          </VSCodeButton>
          <VSCodeButton appearance="secondary" onClick={handleClose}>
            {t`Close`}
          </VSCodeButton>
        </div>
      </header>

      <section className="editor-section">
        <label className="field-label" htmlFor="test-name">
          {t`Test Name`}
        </label>
        <input
          id="test-name"
          className="text-input"
          value={testData.name}
          onChange={handleNameChange}
          placeholder={t`My Test`}
        />
      </section>

      <section className="editor-section">
        <label className="field-label" htmlFor="test-url">
          {t`URL`}
        </label>
        <input
          id="test-url"
          className="text-input"
          value={testData.url}
          onChange={handleUrlChange}
          placeholder={t`https://example.com`}
        />
      </section>

      <ActionList
        actions={testData.actions}
        onActionChange={handleActionChange}
        onRemoveAction={handleRemoveAction}
        onAddAction={handleAddAction}
      />
    </main>
  );
};
