import React from "react";

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
  return (
    <div className="summary">
      <div className="summary-item">
        <span className="summary-number">{summary.total}</span>
        <span className="summary-label">Total Tests</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.running}</span>
        <span className="summary-label">Running</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.passed}</span>
        <span className="summary-label">Passed</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.failed}</span>
        <span className="summary-label">Failed</span>
      </div>
      <div className="summary-item">
        <span className="summary-number">{summary.stopped}</span>
        <span className="summary-label">Stopped</span>
      </div>
    </div>
  );
};
