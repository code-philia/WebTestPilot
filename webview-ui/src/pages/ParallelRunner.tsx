import React, { useCallback, useEffect, useState } from "react";
import { VSCodeButton } from "@vscode/webview-ui-toolkit/react";
import { useVSCode } from "../hooks/useVSCode";
import { TestCard, TestCardData } from "../components/TestCard";
import { TestSummary, SummaryData } from "../components/TestSummary";
import { getCurrentTimeString, parseStepNumber } from "../utilities/formatters";
import { useLingui } from "@lingui/react/macro";

export const ParallelRunner: React.FC = () => {
  const { t } = useLingui();
  const { postMessage, onMessage } = useVSCode();
  const [folderName, setFolderName] = useState<string>("");
  const [connectionStatus, setConnectionStatus] = useState<string>(
    t`Connecting to browser...`
  );
  const [tests, setTests] = useState<Map<string, TestCardData>>(new Map());
  const [summary, setSummary] = useState<SummaryData>({
    total: 0,
    running: 0,
    passed: 0,
    failed: 0,
    stopped: 0,
  });

  // Notify extension that webview is ready
  useEffect(() => {
    postMessage("ready");
  }, [postMessage]);

  // Calculate summary whenever tests change
  useEffect(() => {
    const testArray = Array.from(tests.values());
    setSummary({
      total: testArray.length,
      running: testArray.filter((t) => t.status === "running").length,
      passed: testArray.filter((t) => t.status === "passed").length,
      failed: testArray.filter((t) => t.status === "failed").length,
      stopped: testArray.filter((t) => t.status === "stopped").length,
    });
  }, [tests]);

  // Listen for messages from extension
  useEffect(() => {
    return onMessage((message: any) => {
      if (!message || !message.type) return;

      switch (message.type) {
        case "connected":
          setConnectionStatus(t`Connected to browser ✓`);
          if (message.folderName) {
            setFolderName(message.folderName);
          }
          break;

        case "error":
          setConnectionStatus(`Error: ${message.message}`);
          break;

        case "testStarted":
          handleTestStarted(message);
          break;

        case "testFinished":
          handleTestFinished(message);
          break;

        case "screenshot":
          handleScreenshot(message);
          break;

        case "stepUpdate":
          handleStepUpdate(message);
          break;

        case "logMessage":
          handleLogMessage(message);
          break;

        case "tabsCleared":
          setTests(new Map());
          break;
      }
    });
  }, [onMessage, tests]);

  const handleTestStarted = useCallback((message: any) => {
    const testData: TestCardData = {
      id: message.testId,
      name: message.testName,
      url: message.url || "",
      status: "running",
      tabIndex: message.tabIndex || 0,
      currentStep: 0,
      currentAction: "",
      totalSteps: message.totalSteps || 0,
      startTime: Date.now(),
      targetId: message.targetId,
      logs: [],
      errors: [],
    };

    setTests((prev) => {
      const newMap = new Map(prev);
      newMap.set(message.testId, testData);
      return newMap;
    });
  }, []);

  const handleTestFinished = useCallback((message: any) => {
    setTests((prev) => {
      const newMap = new Map(prev);
      const test = newMap.get(message.testId);

      if (test) {
        test.status = message.result?.status;
        test.endTime = Date.now();
        if (message.result?.errors) {
          test.errors = message.result.errors;
        }
        newMap.set(message.testId, test);
      }
      return newMap;
    });
  }, []);

  const handleScreenshot = useCallback((message: any) => {
    setTests((prev) => {
      const newMap = new Map(prev);
      const test = newMap.get(message.testId);
      if (test) {
        test.screenshot = message.data;
        test.screenshotTimestamp = message.timestamp;
        test.screenshotUrl = message.url;
        newMap.set(message.testId, test);
      }
      return newMap;
    });
  }, []);

  const handleStepUpdate = useCallback((message: any) => {
    setTests((prev) => {
      const newMap = new Map(prev);
      const test = newMap.get(message.testId);
      console.log(test);
      if (test) {
        test.currentStep = message.stepNumber;
        test.currentAction = `${message.status} step ${message.stepNumber}`;

        // Add step update to logs
        console.log("Adding step log:", message, test.currentAction);
        test.logs = [
          ...(test.logs || []),
          {
            type:
              message.status === "failed"
                ? ("stderr" as const)
                : ("stdout" as const),
            message:
              message.message ||
              `Step ${message.stepNumber}: ${message.status}`,
            time: getCurrentTimeString(),
          },
        ];

        // Add errors if step failed
        if (message.status === "failed" && message.error) {
          test.errors = [...(test.errors || []), message.error];
        }

        newMap.set(message.testId, test);
      }
      return newMap;
    });
  }, []);

  const handleLogMessage = useCallback((message: any) => {
    setTests((prev) => {
      const newMap = new Map(prev);
      const test = newMap.get(message.testId);
      if (test) {
        const logEntry = {
          type: message.logType as "stdout" | "stderr",
          message: message.message,
          time: getCurrentTimeString(),
        };
        test.logs = [...(test.logs || []), logEntry];

        // Update step counter based on log message
        const stepNum = parseStepNumber(message.message);
        if (stepNum !== null && stepNum > test.currentStep) {
          test.currentStep = stepNum;
        }

        newMap.set(message.testId, test);
      }
      return newMap;
    });
  }, []);

  const handleStopTest = useCallback(
    (testId: string) => {
      postMessage("stopTest", { testId });
      setTests((prev) => {
        const newMap = new Map(prev);
        const test = newMap.get(testId);
        if (test) {
          test.status = "stopped";
          test.endTime = Date.now();
          newMap.set(testId, test);
        }
        return newMap;
      });
    },
    [postMessage]
  );

  const handleViewLogs = useCallback(
    (testId: string, testName: string) => {
      postMessage("viewLogs", { testId, testName });
    },
    [postMessage]
  );

  const handleStopAllTests = useCallback(() => {
    postMessage("stopAll");
    setTests((prev) => {
      const newMap = new Map(prev);
      newMap.forEach((test) => {
        if (test.status === "running") {
          test.status = "stopped";
          test.endTime = Date.now();
        }
      });
      return newMap;
    });
  }, [postMessage]);

  const handleClearTabs = useCallback(() => {
    postMessage("clearTabs");
  }, [postMessage]);

  const testArray = Array.from(tests.values());
  const hasRunningTests = testArray.some((t) => t.status === "running");
  const hasFinishedTests = testArray.some(
    (t) =>
      t.status === "passed" || t.status === "failed" || t.status === "stopped"
  );

  return (
    <div className="parallel-runner-root">
      <div className="header">
        <h1>
          {t`Parallel Tests:`} {folderName || t`Loading...`}
        </h1>
        <div>{connectionStatus}</div>
      </div>

      {testArray.length > 0 && <TestSummary summary={summary} />}

      <div className="controls">
        <VSCodeButton
          appearance="secondary"
          onClick={handleStopAllTests}
          disabled={!hasRunningTests}
        >
          {t`Stop All Tests`}
        </VSCodeButton>
        <VSCodeButton appearance="secondary" onClick={handleClearTabs}>
          {t`Clear All Tabs`}
        </VSCodeButton>
      </div>

      <div className="test-grid">
        {testArray.map((test) => (
          <TestCard
            key={test.id}
            test={test}
            onStop={handleStopTest}
            onViewLogs={handleViewLogs}
          />
        ))}
      </div>
    </div>
  );
};

export default ParallelRunner;
