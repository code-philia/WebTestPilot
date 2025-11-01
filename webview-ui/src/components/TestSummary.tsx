import React from "react";
import { useLingui } from "@lingui/react/macro";

export interface SummaryData {
  total: number;
  running: number;
  passed: number;
  failed: number;
  stopped: number;
}

interface TestSummaryProps {
  summary: SummaryData;
}

export const TestSummary: React.FC<TestSummaryProps> = ({ summary }) => {
  const { t } = useLingui();
  return (
    <div className="summary">
      <div className="summary-item">
        <span className="summary-number">{summary.total}</span>
        <span className="summary-label">{t`Total Tests`}</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.running}</span>
        <span className="summary-label">{t`Running`}</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.passed}</span>
        <span className="summary-label">{t`Passed`}</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.failed}</span>
        <span className="summary-label">{t`Failed`}</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.stopped}</span>
        <span className="summary-label">{t`Stopped`}</span>
      </div>
    </div>
  );
};
