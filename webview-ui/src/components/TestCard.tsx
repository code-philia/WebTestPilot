import { useLingui } from "@lingui/react/macro";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";
import React, { useEffect, useState } from "react";
import { formatDuration, formatTimestamp } from "../utilities/formatters";

export interface TestCardData {
  id: string;
  name: string;
  url: string;
  status: "pending" | "running" | "passed" | "failed" | "stopped";
  currentAction: string;
  tabIndex: number;
  currentStep: number;
  totalSteps: number;
  startTime: number;
  endTime?: number;
  screenshot?: string;
  screenshotTimestamp?: number;
  screenshotUrl?: string;
  targetId?: string;
  errors?: string[];
  logs?: Array<{
    type: "stdout" | "stderr";
    message: string;
    time: string;
  }>;
}

interface TestCardProps {
  test: TestCardData;
  onStop: (testId: string) => void;
  onViewLogs: (testId: string, testName: string) => void;
}

export const TestCard: React.FC<TestCardProps> = ({
  test,
  onStop,
  onViewLogs,
}) => {
  const { t } = useLingui();
  const [duration, setDuration] = useState(0);

  // Update duration timer
  useEffect(() => {
    if (test.status === "running") {
      const interval = setInterval(() => {
        setDuration(Date.now() - test.startTime);
      }, 1000);
      return () => clearInterval(interval);
    } else if (test.endTime) {
      setDuration(test.endTime - test.startTime);
    }
  }, [test.status, test.startTime, test.endTime]);

  const getStatusClass = () => {
    switch (test.status) {
      case "running":
        return "status-running";
      case "passed":
        return "status-passed";
      case "failed":
        return "status-failed";
      case "stopped":
        return "status-stopped";
      default:
        return "status-pending";
    }
  };

  return (
    <div className="test-card">
      <div className="test-header">
        <div className="test-name" title={test.name}>
          {test.name}
        </div>
        <div className={`test-status ${getStatusClass()}`}>{test.currentAction}</div>
        <div className={`test-status ${getStatusClass()}`}>{test.status}</div>
      </div>

      {test.targetId && (
        <div className="tab-info">
          {t`Browser Tab:`} {test.targetId.slice(0, 8)}
        </div>
      )}

      {test.url && <div className="url-info">{test.url}</div>}

      <div className="test-info">
        <span>
          {t`Steps:`} {test.currentStep}/{test.totalSteps}
        </span>
        <span>
          {t`Duration:`} {formatDuration(duration)}
        </span>
        <span>
          {t`Tab #`}
          {test.tabIndex}
        </span>
      </div>

      {test.screenshot && (
        <img
          src={`data:image/png;base64,${test.screenshot}`}
          alt={`${test.name} screenshot`}
          className="test-screenshot"
          title={
            test.screenshotUrl
              ? `${test.screenshotUrl} (${formatTimestamp(
                  test.screenshotTimestamp || 0
                )})`
              : undefined
          }
        />
      )}

      <div className="test-actions">
        {test.status === "running" && (
          <VSCodeButton appearance="secondary" onClick={() => onStop(test.id)}>
            {t`Stop`}
          </VSCodeButton>
        )}
        <VSCodeButton
          appearance="secondary"
          onClick={() => onViewLogs(test.id, test.name)}
        >
          {t`View Full Logs`}
        </VSCodeButton>
      </div>

      {test.errors && test.errors.length > 0 && (
        <div className="error-details">
          {test.errors.map((error, idx) => (
            <div key={idx}>{error}</div>
          ))}
        </div>
      )}

      {test.logs && test.logs.length > 0 && (
        <div className="log-container">
          {test.logs.map((log, idx) => (
            <div
              key={idx}
              className={`log-entry ${
                log.type === "stderr" ? "log-stderr" : ""
              }`}
            >
              <span className="log-time">{log.time}</span>
              <span className="log-type">[{log.type.toUpperCase()}]</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
