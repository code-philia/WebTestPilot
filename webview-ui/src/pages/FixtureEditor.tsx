import React, {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
} from "react";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";
import { useVSCode } from "../hooks/useVSCode";
import { ActionList } from "../components/ActionList";
import type { TestAction, FixtureEditorData, SaveFixturePayload } from "../types";
import { useLingui } from "@lingui/react/macro";

const DEFAULT_DATA: FixtureEditorData = {
  id: undefined,
  folderId: undefined,
  name: "",
  actions: [],
};

function sanitizePayload(data: FixtureEditorData): SaveFixturePayload {
  return {
    name: data.name.trim(),
    actions: data.actions.map((action: TestAction) => ({
      action: action.action.trim(),
      expectedResult: action.expectedResult.trim(),
    })),
  };
}

export const FixtureEditor: React.FC = () => {
  const { t } = useLingui();
  const { postMessage, onMessage, getState, setState } = useVSCode();
  const [fixtureData, setFixtureData] = useState<FixtureEditorData>(
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

      if (message.command === "loadFixture" && message.fixture) {
        const fixture: FixtureEditorData = {
          id: message.fixture.id,
          folderId: message.fixture.folderId,
          name: message.fixture.name || "",
          actions: message.fixture.actions || [],
        };
        setFixtureData(fixture);
        setState(fixture);
      }
    });
  }, [onMessage, setState]);

  // Persist state changes
  useEffect(() => {
    setState(fixtureData);
  }, [fixtureData, setState]);

  // Update document title
  useEffect(() => {
    document.title = fixtureData.name
      ? t`Edit Fixture: ${fixtureData.name}`
      : t`Edit Fixture`;
  }, [fixtureData.name]);

  // Event handlers
  const handleNameChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setFixtureData((prev: FixtureEditorData) => ({ ...prev, name: value }));
      postMessage("updateFixture", { data: { name: value } });
    },
    [postMessage]
  );

  const handleAddAction = useCallback(() => {
    setFixtureData((prev: FixtureEditorData) => ({
      ...prev,
      actions: [...prev.actions, { action: "", expectedResult: "" }],
    }));
  }, []);

  const handleRemoveAction = useCallback((index: number) => {
    setFixtureData((prev: FixtureEditorData) => ({
      ...prev,
      actions: prev.actions.filter((_: TestAction, idx: number) => idx !== index),
    }));
  }, []);

  const handleActionChange = useCallback(
    (index: number, field: keyof TestAction, value: string) => {
      setFixtureData((prev: FixtureEditorData) => ({
        ...prev,
        actions: prev.actions.map((action: TestAction, idx: number) =>
          idx === index ? { ...action, [field]: value } : action
        ),
      }));
    },
    []
  );

  const handleClose = useCallback(() => {
    postMessage("close");
  }, [postMessage]);

  const persistSanitizedState = useCallback((payload: SaveFixturePayload) => {
    setFixtureData((prev: FixtureEditorData) => ({
      ...prev,
      name: payload.name,
      actions: payload.actions,
    }));
  }, []);

  const handleSave = useCallback(() => {
    const payload = sanitizePayload(fixtureData);

    if (!payload.name) {
      postMessage("showError", { text: t`Fixture name is required` });
      return;
    }

    persistSanitizedState(payload);
    postMessage("save", { data: payload });
  }, [persistSanitizedState, fixtureData, postMessage]);

  return (
    <main className="test-editor">
      <header className="editor-header">
        <div className="editor-title">
          {fixtureData.name ? t`Edit Fixture: ${fixtureData.name}` : t`Edit Fixture`}
        </div>
        <div className="header-actions">
          <VSCodeButton appearance="primary" onClick={handleSave}>
            {t`Save Fixture`}
          </VSCodeButton>
          <VSCodeButton appearance="secondary" onClick={handleClose}>
            {t`Close`}
          </VSCodeButton>
        </div>
      </header>

      <section className="editor-section">
        <label className="field-label" htmlFor="fixture-name">
          {t`Fixture Name`}
        </label>
        <input
          id="fixture-name"
          className="text-input"
          value={fixtureData.name}
          onChange={handleNameChange}
          placeholder={t`My Fixture`}
        />
      </section>

      <ActionList
        actions={fixtureData.actions}
        onActionChange={handleActionChange}
        onRemoveAction={handleRemoveAction}
        onAddAction={handleAddAction}
      />
    </main>
  );
};