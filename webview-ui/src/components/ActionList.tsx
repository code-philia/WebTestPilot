import React, { type ChangeEvent } from "react";
import type { TestAction } from "../types";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";

interface ActionListProps {
  actions: TestAction[];
  onActionChange: (
    index: number,
    field: keyof TestAction,
    value: string
  ) => void;
  onRemoveAction: (index: number) => void;
  onAddAction: () => void;
}

export const ActionList: React.FC<ActionListProps> = ({
  actions,
  onActionChange,
  onRemoveAction,
  onAddAction,
}) => {
  return (
    <section className="editor-section actions-section">
      <div className="section-header">
        <h3>Actions</h3>
        <VSCodeButton onClick={onAddAction}>Add Action</VSCodeButton>
      </div>

      {actions.length === 0 ? (
        <div className="empty-state">
          No actions defined. Click "Add Action" to get started.
        </div>
      ) : (
        <div className="actions-list">
          {actions.map((action, index) => (
            <div key={`action-${index}`} className="action-card">
              <div className="action-row">
                <span className="action-number">{index + 1}.</span>
                <input
                  className="text-input"
                  value={action.action}
                  onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    onActionChange(index, "action", e.target.value)
                  }
                  placeholder="Action"
                />
                <button
                  className="icon-button"
                  onClick={() => onRemoveAction(index)}
                  aria-label={`Remove action ${index + 1}`}
                >
                  ×
                </button>
              </div>
              <div className="action-row">
                <span className="action-number">→</span>
                <input
                  className="text-input"
                  value={action.expectedResult}
                  onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    onActionChange(index, "expectedResult", e.target.value)
                  }
                  placeholder="Expected result"
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
