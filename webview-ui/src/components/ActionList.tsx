import React, { type ChangeEvent, useState } from "react";
import type { TestAction } from "../types";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";
import { useLingui } from "@lingui/react/macro";

interface ActionListProps {
  actions: TestAction[];
  onActionChange?: (
    index: number,
    field: keyof TestAction,
    value: string
  ) => void;
  onRemoveAction?: (index: number) => void;
  onAddAction?: () => void;
  readonly?: boolean;
}

export const ActionList: React.FC<ActionListProps> = ({
  actions,
  onActionChange = () => {},
  onRemoveAction = () => {},
  onAddAction = () => {},
  readonly = false,
}) => {
  const { t } = useLingui();
  const [showActions, setShowActions] = useState(true);

  return (
    <section
      className={`editor-section actions-section ${readonly ? "readonly" : ""}`}
    >
      <div className="section-header">
        <h3>{readonly ? t`From fixture` : t`Actions`}</h3>
        {readonly ? (
          // Eye and close eye icons for toggling visibility
          <VSCodeButton onClick={() => setShowActions(!showActions)}>
            {showActions ? t`Hide` : t`Show`}
          </VSCodeButton>
        ) : (
          <VSCodeButton onClick={onAddAction}>{t`Add Action`}</VSCodeButton>
        )}
      </div>

      {showActions &&
        (actions.length === 0 ? (
          <div className="empty-state">
            {readonly
              ? t`No actions defined in fixtures.`
              : t`No actions defined. Click "Add Action" to get started.`}
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
                    onChange={
                      readonly
                        ? undefined
                        : (e: ChangeEvent<HTMLInputElement>) =>
                            onActionChange(index, "action", e.target.value)
                    }
                    placeholder={t`Action`}
                    readOnly={readonly}
                    aria-readonly={readonly}
                  />
                  {!readonly && (
                    <button
                      className="icon-button"
                      onClick={() => onRemoveAction(index)}
                      aria-label={`Remove action ${index + 1}`}
                    >
                      ×
                    </button>
                  )}
                </div>
                <div className="action-row">
                  <span className="action-number">→</span>
                  <input
                    className="text-input"
                    value={action.expectedResult}
                    onChange={
                      readonly
                        ? undefined
                        : (e: ChangeEvent<HTMLInputElement>) =>
                            onActionChange(
                              index,
                              "expectedResult",
                              e.target.value
                            )
                    }
                    placeholder={t`Expected result`}
                    readOnly={readonly}
                    aria-readonly={readonly}
                  />
                </div>
              </div>
            ))}
          </div>
        ))}
    </section>
  );
};
