import assert from "assert";
import { spawn } from "child_process";
import * as fs from "fs/promises";
import * as path from "path";
import { chromium, Page } from "playwright-core";
import * as vscode from "vscode";
import { TestItem } from "../models";
import { EnvironmentService } from "../services/environmentService";
import { WorkspaceRootService } from "../services/workspaceRootService.js";
import { WebTestPilotTreeDataProvider } from "../treeDataProvider";
import { parseLogEvents } from "../utils/logParser";
import { loadWebviewHtml } from "../utils/webviewLoader";

/**
 * TestRunnerPanel handles running tests by connecting to a remote browser via CDP
 * and streaming live screenshots to show test execution in real-time
 */
export class TestRunnerPanel {
    public static currentPanel: TestRunnerPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _testItem: TestItem;
    private _browser: any;
    private _page: Page | undefined;
    private _screenshotInterval: NodeJS.Timeout | undefined;
    private _pythonProcess: any = undefined;
    private _isTestRunning: boolean = false;
    private _progress:
    | vscode.Progress<{
        message?: string;
        increment?: number;
      }>
    | undefined = undefined;

    private constructor(
        panel: vscode.WebviewPanel,
        testItem: TestItem,
        cdpEndpoint: string,
    ) {
        this._panel = panel;
        this._testItem = testItem;
        this._panel.webview.html = this._getHtmlForWebview();

        // Connect to CDP and start streaming
        this._connectToBrowser(cdpEndpoint);

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview (support both `type` and `command` fields)
        this._panel.webview.onDidReceiveMessage(
            (message) => {
                const msgType = message?.type || message?.command;
                switch (msgType) {
                case "ready":
                    console.log("Webview ready for screenshots");
                    return;
                case "navigate":
                    if (this._page) {
                        this._page.goto(message.url).catch((err: Error) => {
                            vscode.window.showErrorMessage(
                                `Navigation failed: ${err.message}`
                            );
                        });
                    }
                    return;
                case "stopTest":
                    this._stopTest();
                    return;
                }
            },
            undefined,
            this._disposables
        );
    }

    /**
   * Connects to the remote browser via CDP and starts screenshot streaming
   */
    private async _connectToBrowser(cdpEndpoint: string) {
        try {
            // Connect to CDP
            this._browser = await chromium.connectOverCDP(cdpEndpoint);

            // Get the first available page or create a new one
            const contexts = this._browser.contexts();
            const context =
        contexts.length > 0 ? contexts[0] : await this._browser.newContext();
            const pages = context.pages();
            this._page = pages.length > 0 ? pages[0] : await context.newPage();

            assert(this._page, "Failed to get or create a page in the browser");

            vscode.window.showInformationMessage(
                `Connected to browser! Streaming live view...`
            );

            // Send initial info
            this._panel.webview.postMessage({
                type: "connected",
                url: this._page.url(),
            });

            // Listen to console messages from the browser
            this._page.on("console", (msg: any) => {
                this._panel.webview.postMessage({
                    type: "console",
                    level: msg.type(),
                    text: msg.text(),
                });
            });

            // Listen to page navigation
            this._page.on("framenavigated", (frame: any) => {
                assert(this._page, "Page should be defined");

                if (frame === this._page.mainFrame()) {
                    this._panel.webview.postMessage({
                        type: "navigation",
                        url: frame.url(),
                    });
                }
            });

            // Start screenshot streaming (every 500ms for near real-time)
            this._startScreenshotStream();
        } catch (error) {
            console.error("Failed to connect to browser:", error);
            vscode.window.showErrorMessage(
                `Failed to connect to CDP at ${cdpEndpoint}. Make sure Chrome is running with --remote-debugging-port=9222`
            );
            this._panel.webview.postMessage({
                type: "error",
                message: `Connection failed: ${error}`,
            });
        }
    }

    /**
   * Stops the currently running Python test process
   */
    private _stopTest() {
        if (this._pythonProcess && this._isTestRunning) {
            console.log("Stopping Python test process...");

            // Send SIGTERM to gracefully terminate the process
            this._pythonProcess.kill("SIGTERM");

            // If it doesn't stop within 2 seconds, force kill it
            setTimeout(() => {
                if (this._pythonProcess && !this._pythonProcess.killed) {
                    console.log("Force killing Python process...");
                    this._pythonProcess.kill("SIGKILL");
                }
            }, 2000);

            this._isTestRunning = false;

            // Update UI
            this._panel.webview.postMessage({
                type: "testStopped",
            });

            vscode.window.showWarningMessage("Test execution stopped by user");
        }
    }

    /**
   * Starts periodic screenshot capture and streaming to webview
   */
    private _startScreenshotStream() {
        if (this._screenshotInterval) {
            clearInterval(this._screenshotInterval);
        }

        const captureScreenshot = async () => {
            if (!this._page) {
                return;
            }

            try {
                const imgBuffer = await this._page.screenshot({
                    type: "png",
                    fullPage: true,
                    scale: "device",
                });
                const base64 = imgBuffer.toString("base64");

                this._panel.webview.postMessage({
                    type: "screenshot",
                    data: base64,
                });
            } catch (error) {
                console.error("Screenshot capture failed:", error);
            }
        };

        // Capture initial screenshot
        captureScreenshot();

        // Then capture every 200ms for near real-time updates
        this._screenshotInterval = setInterval(captureScreenshot, 200);
    }

    /**
   * Opens a test in a live browser viewer with CDP connection and runs the Python agent
   * @param testItem The test to run
   * @param workspaceRoot The workspace root path
   */
    public static async createOrShow(
        testItem: TestItem,
    ) {
        try {
            const url = testItem.url;
            const cdpEndpoint =
        vscode.workspace
            .getConfiguration("webtestpilot")
            .get<string>("cdpEndpoint") || "http://localhost:9222";

            // Validate test has actions
            console.log(testItem);
            if (!testItem.actions || testItem.actions.length === 0) {
                vscode.window.showWarningMessage(
                    `Test "${testItem.name}" has no actions defined. Please add test actions before running.`
                );
                return;
            }

            // Create output channel for test execution logs
            const outputChannel = vscode.window.createOutputChannel(
                "WebTestPilot Test Runner"
            );
            outputChannel.clear();
            outputChannel.show(true);

            // If we already have a panel, dispose it and create a new one
            if (TestRunnerPanel.currentPanel) {
                TestRunnerPanel.currentPanel.dispose();
            }

            // Create a new panel for live browser view
            const panel = vscode.window.createWebviewPanel(
                "Single Runner",
                `Single Runner: ${testItem.name}`,
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true,
                }
            );

            TestRunnerPanel.currentPanel = new TestRunnerPanel(
                panel,
                testItem,
                cdpEndpoint,
            );

            // Show progress notification with cancel button
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: `Running test: ${testItem.name}`,
                    cancellable: true,
                },
                async (progress, token) => {
                    // Store progress reference for step updates
                    if (TestRunnerPanel.currentPanel) {
                        TestRunnerPanel.currentPanel._progress = progress;
                    }

                    // Handle cancellation from notification
                    token.onCancellationRequested(() => {
                        console.log("Test cancelled from notification");
                        TestRunnerPanel.currentPanel?._stopTest();
                    });
                    progress.report({ message: "Starting Python agent..." });

                    // Run the Python CLI to execute the test
                    const workspaceRoot = WorkspaceRootService.getWorkspaceRoot();
                    console.log("Using workspace root:", workspaceRoot);
                    const pythonPath = path.join(
                        workspaceRoot,
                        "webtestpilot",
                        ".venv",
                        "bin",
                        "python"
                    );
                    const cliScriptPath = path.join(
                        workspaceRoot,
                        "webtestpilot",
                        "src",
                        "cli.py"
                    );
                    const configPath = path.join(
                        workspaceRoot,
                        "webtestpilot",
                        "src",
                        "config.yaml"
                    );
                    const traceOutputPath = path.join(
                        workspaceRoot,
                        ".webtestpilot",
                        "traces",
                        `${testItem.id}-trace.zip`
                    );

                    // Ensure traces directory exists
                    const tracesDir = path.dirname(traceOutputPath);
                    await fs.mkdir(tracesDir, { recursive: true });

                    outputChannel.appendLine(`Workspace Root: ${workspaceRoot}`);
                    outputChannel.appendLine(`Python: ${pythonPath}`);
                    outputChannel.appendLine(`CLI Script: ${cliScriptPath}`);
                    outputChannel.appendLine(`Config: ${configPath}`);
                    outputChannel.appendLine(`Trace Output: ${traceOutputPath}`);
                    outputChannel.appendLine("");

                    // Verify CLI script exists
                    try {
                        await fs.access(cliScriptPath);
                        outputChannel.appendLine("✓ CLI script found");
                    } catch (error) {
                        outputChannel.appendLine(
                            `✗ CLI script NOT FOUND: ${cliScriptPath}`
                        );
                        vscode.window.showErrorMessage(
                            `Python CLI script not found at: ${cliScriptPath}\n\n` +
                `Make sure you have opened the correct workspace folder.\n` +
                `Expected workspace: .../WebTestPilot/extension/webtestpilot`
                        );
                        throw new Error(`CLI script not found: ${cliScriptPath}`);
                    }

                    outputChannel.appendLine("Executing Python agent...");
                    outputChannel.appendLine("");

                    // Execute Python CLI
                    try {
                        const args = [
                            testItem.fullPath,
                            "--config",
                            configPath,
                            "--cdp-endpoint",
                            cdpEndpoint,
                            "--json-output",
                        ];
                        
                        const fixtureDataProvider = (global as any).webTestPilotFixtureTreeDataProvider as WebTestPilotTreeDataProvider;
                        if (testItem.fixtureId) {
                            const fixture = fixtureDataProvider?.getFixtureWithId(testItem.fixtureId);
                            args.push("--fixture-file-path", fixture!.fullPath);
                        }
                    
                        const environmentService = (global as any).environmentService as EnvironmentService;
                        const selectedEnv = environmentService.getSelectedEnvironment();
                        if (selectedEnv) {
                            args.push("--environment-file-path", selectedEnv.fullPath);
                        }

                        const pythonProcess = spawn(
                            pythonPath,
                            [
                                cliScriptPath,
                                ...args,
                            ],
                            {
                                env: {
                                    ...process.env,
                                    BAML_LOG: "info",
                                },
                            }
                        );

                        // Store process reference for cancellation
                        if (TestRunnerPanel.currentPanel) {
                            TestRunnerPanel.currentPanel._pythonProcess = pythonProcess;
                            TestRunnerPanel.currentPanel._isTestRunning = true;

                            // Update webview to show stop button
                            TestRunnerPanel.currentPanel._panel.webview.postMessage({
                                type: "testStarted",
                            });
                        }

                        let stdoutData = "";
                        let stderrData = "";

                        pythonProcess.stdout.on("data", (data: Buffer) => {
                            const text = data.toString();
                            stdoutData += text;
                            outputChannel.append(text);

                            // Parse step information from logs
                            TestRunnerPanel.currentPanel?._parseStepUpdates(text);
                        });

                        pythonProcess.stderr.on("data", (data: Buffer) => {
                            const text = data.toString();
                            stderrData += text;
                            outputChannel.append(`${text}`);
                        });

                        await new Promise<void>((resolve, reject) => {
                            pythonProcess.on("close", (code: number, signal: string) => {
                                // Clear running state
                                if (TestRunnerPanel.currentPanel) {
                                    TestRunnerPanel.currentPanel._isTestRunning = false;
                                    TestRunnerPanel.currentPanel._pythonProcess = undefined;

                                    // Update webview
                                    TestRunnerPanel.currentPanel._panel.webview.postMessage({
                                        type: "testFinished",
                                    });
                                }

                                outputChannel.appendLine("");
                                outputChannel.appendLine("=".repeat(60));

                                // Check if process was terminated by signal (user stopped it)
                                if (signal === "SIGTERM" || signal === "SIGKILL") {
                                    outputChannel.appendLine(
                                        "⚠️  Test execution stopped by user"
                                    );
                                    outputChannel.appendLine("=".repeat(60));
                                    resolve();
                                    return;
                                }

                                if (code === 0) {
                                    outputChannel.appendLine(
                                        "✅ Test execution completed successfully!"
                                    );

                                    // Try to parse JSON result
                                    try {
                                        const jsonMatch = stdoutData.match(/\{[\s\S]*\}/);
                                        if (jsonMatch) {
                                            const result = JSON.parse(jsonMatch[0]);
                                            outputChannel.appendLine("");
                                            outputChannel.appendLine("Test Results:");
                                            outputChannel.appendLine(`  Success: ${result.success}`);
                                            outputChannel.appendLine(
                                                `  Steps Executed: ${result.steps_executed || 0}`
                                            );
                                            if (result.errors && result.errors.length > 0) {
                                                outputChannel.appendLine(
                                                    `  Errors: ${result.errors.join(", ")}`
                                                );
                                            }
                                        }
                                    } catch (e) {
                                        // Ignore JSON parse errors
                                    }

                                    vscode.window
                                        .showInformationMessage(
                                            `✅ Test "${testItem.name}" PASSED - All steps completed successfully!`,
                                            "View Trace",
                                            "View Output"
                                        )
                                        .then((selection) => {
                                            if (selection === "View Trace") {
                                                vscode.commands.executeCommand(
                                                    "vscode.open",
                                                    vscode.Uri.file(traceOutputPath)
                                                );
                                            } else if (selection === "View Output") {
                                                outputChannel.show();
                                            }
                                        });

                                    resolve();
                                } else {
                                    outputChannel.appendLine(
                                        `❌ Test execution failed with exit code: ${code}`
                                    );
                                    vscode.window
                                        .showErrorMessage(
                                            `❌ Test "${testItem.name}" FAILED - Check output for details.`,
                                            "View Output"
                                        )
                                        .then((selection) => {
                                            if (selection === "View Output") {
                                                outputChannel.show();
                                            }
                                        });

                                    reject(new Error(`Python process exited with code ${code}`));
                                }

                                outputChannel.appendLine("=".repeat(60));
                            });

                            pythonProcess.on("error", (error: Error) => {
                                outputChannel.appendLine("");
                                outputChannel.appendLine(
                                    `❌ Failed to start Python process: ${error.message}`
                                );
                                vscode.window
                                    .showErrorMessage(
                                        `Failed to run test: ${error.message}`,
                                        "View Output"
                                    )
                                    .then((selection) => {
                                        if (selection === "View Output") {
                                            outputChannel.show();
                                        }
                                    });
                                reject(error);
                            });
                        });
                    } catch (error) {
                        outputChannel.appendLine("");
                        outputChannel.appendLine(`❌ Error: ${error}`);
                        throw error;
                    }
                }
            );

            console.log("Test execution completed:", {
                testName: testItem.name,
                url: url,
                cdpEndpoint: cdpEndpoint,
                actionsCount: testItem.actions?.length || 0,
            });
        } catch (error) {
            console.error("Error running test:", error);
            vscode.window.showErrorMessage(`Failed to run test: ${error}`);
        }
    }

    /**
   * Gets the HTML content for the webview
   */
    private _getHtmlForWebview(): string {
        return loadWebviewHtml(
            this._panel.webview,
            "singleRunner"
        );
    }

    /**
   * Parse step updates from Python process output
   */
    private _parseStepUpdates(text: string) {
        assert(this._progress, "Progress object should be defined");

        const events = parseLogEvents(text);
        for (const ev of events) {
            if (ev.type === "step") {
                const stepNumber = ev.step;
                if (ev.status === "started") {
                    this._progress.report({
                        message: `Step ${stepNumber}: ${ev.action || ""}`,
                    });
                } else if (ev.status === "passed") {
                    vscode.window.showInformationMessage(`Step ${stepNumber} passed`);
                } else if (ev.status === "failed") {
                    vscode.window.showErrorMessage(
                        `❌ Step ${stepNumber} failed: ${ev.error || "error"}`
                    );
                }
            } else if (ev.type === "verification") {
                const stepNumber = ev.step;

                if (ev.status === "verifying") {
                    this._progress.report({
                        message: `Step ${stepNumber}: Verifying - ${ev.expectation || ""}`,
                    });
                } else if (ev.status === "verifyPassed") {
                    this._progress.report({
                        message: `Step ${stepNumber}: ✓ Completed`,
                    });
                    vscode.window.showInformationMessage(
                        `✅ Step ${stepNumber} verification passed`
                    );
                } else if (ev.status === "verifyFailed") {
                    this._progress.report({
                        message: `Step ${stepNumber}: ❌ Failed - ${
                            ev.error || "verification failed"
                        }`,
                    });
                    vscode.window.showErrorMessage(
                        `❌ Step ${stepNumber} verification failed: ${
                            ev.error || "verification failed"
                        }`
                    );
                }
            } else if (ev.type === "bug") {
                vscode.window.showErrorMessage(`Bug reported: ${ev.message}`);
            }
        }
    }

    /**
   * Disposes the panel and cleans up resources
   */
    public dispose() {
        TestRunnerPanel.currentPanel = undefined;

        // Clear progress reference
        this._progress = undefined;

        // Stop any running test
        if (this._pythonProcess && this._isTestRunning) {
            console.log("Killing Python process on dispose");
            this._pythonProcess.kill("SIGTERM");
        }

        // Stop screenshot streaming
        if (this._screenshotInterval) {
            clearInterval(this._screenshotInterval);
        }

        // Close browser connection
        if (this._browser) {
            this._browser.close().catch((err: Error) => {
                console.error("Error closing browser:", err);
            });
        }

        // Clean up panel
        this._panel.dispose();

        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
