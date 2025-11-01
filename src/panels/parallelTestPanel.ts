import { spawn } from 'child_process';
import * as fs from 'fs/promises';
import * as path from 'path';
import { Browser, BrowserContext, chromium, Page } from 'playwright-core';
import * as vscode from 'vscode';
import { FolderItem, TestItem } from '../models';
import { loadWebviewHtml } from '../utils/webviewLoader';
import { WorkspaceRootService } from '../services/workspaceRootService';



interface TestExecution {
    testItem: TestItem;
    page: Page;
    targetId: string;
    pythonProcess: ReturnType<typeof spawn> | null;
    isRunning: boolean;
    startTime: number;
    endTime?: number;
    currentStep: number;
    totalSteps: number;
    stepsWithVerifications: Set<number>; // Steps that have verification checks
    verifiedSteps: Set<number>; // Steps that passed verification
    completedSteps: Set<number>; // All steps that completed (with or without verification)
    result?: {
        success: boolean;
        stepsExecuted: number;
        errors: string[];
    };
}

interface TestData {
    name?: string;
    url?: string;
    actions?: any[];
}

/**
 * ParallelTestRunner handles running multiple test cases simultaneously
 * with each test in its own browser tab and Python process
 */
export class ParallelTestPanel {
    public static currentPanel: ParallelTestPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _folder: FolderItem;
    private _browser: Browser | undefined;
    private _context: BrowserContext | undefined;
    private _executions: Map<string, TestExecution> = new Map();
    private _screenshotIntervals: Map<string, NodeJS.Timeout> = new Map();
    private _outputChannel: vscode.OutputChannel;
    private _testLogs: Map<string, { stdout: string[], stderr: string[] }> = new Map();
    private _testOutputChannels: Map<string, vscode.OutputChannel> = new Map();

    private constructor(
        panel: vscode.WebviewPanel,
        folder: FolderItem,
        cdpEndpoint: string,
        extensionUri: vscode.Uri
    ) {
        this._panel = panel;
        this._folder = folder;
        this._outputChannel = vscode.window.createOutputChannel('WebTestPilot Parallel Runner');

        // Set the webview's initial html content using React UI
        this._panel.webview.html = this._getHtmlForWebview(extensionUri);

        // Connect to browser and setup parallel execution
        this._connectToBrowser(cdpEndpoint);

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'ready':
                        console.log('Parallel runner webview ready');
                        return;
                    case 'stopTest':
                        this._stopTest(message.testId);
                        return;
                    case 'stopAll':
                        this._stopAllTests();
                        return;
                    case 'viewLogs':
                        this._showTestLogs(message.testId, message.testName);
                        return;
                    case 'clearTabs':
                        this._confirmClearAllTabs();
                        return;
                }
            },
            undefined,
            this._disposables
        );
    }

    /**
     * Load and parse a JSON test file
     */
    private async _loadAndParseTestFile(testId: string, workspaceRoot: string): Promise<TestData> {
        const testFilePath = path.join(workspaceRoot, '.webtestpilot', testId);
        const content = await fs.readFile(testFilePath, 'utf-8');
        const testData = JSON.parse(content);
        
        if (!testData.actions || testData.actions.length === 0) {
            throw new Error('No actions defined in test');
        }
        
        return testData;
    }

    /**
     * Connects to the remote browser via CDP and creates context for parallel execution
     */
    private async _connectToBrowser(cdpEndpoint: string) {
        try {
            // Connect to CDP
            this._browser = await chromium.connectOverCDP(cdpEndpoint);
            
            // Wait a moment for browser to be fully ready
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Create a single context for all tests
            const contexts = this._browser.contexts();
            this._context = contexts.length > 0 ? contexts[0] : await this._browser.newContext();
            
            // Wait for context to be fully initialized
            await new Promise(resolve => setTimeout(resolve, 500));

            vscode.window.showInformationMessage(`✅ Connected! Ready for parallel test execution`);

            // Send initial connection status
            this._panel.webview.postMessage({
                type: 'connected',
                folderName: this._folder.name
            });

        } catch (error) {
            console.error('Failed to connect to browser:', error);
            vscode.window.showErrorMessage(
                `Failed to connect to CDP at ${cdpEndpoint}. Make sure Chrome is running with --remote-debugging-port=9222`
            );
            this._panel.webview.postMessage({
                type: 'error',
                message: `Connection failed: ${error}`
            });
        }
    }

    /**
     * Starts execution of all tests in the folder
     */
    private async _startParallelTests(tests: TestItem[], workspaceRoot: string) {
        this._outputChannel.clear();
        this._outputChannel.show(true);
        
        this._outputChannel.appendLine('='.repeat(60));
        this._outputChannel.appendLine(`Starting Parallel Test Execution: ${this._folder.name}`);
        this._outputChannel.appendLine(`Tests to run: ${tests.length}`);
        this._outputChannel.appendLine('='.repeat(60));

        // Get workspace root using same method as single test runner
        workspaceRoot = WorkspaceRootService.getWorkspaceRoot();
        console.log('Parallel runner using workspace root:', workspaceRoot);
        
        // Get configuration
        const cdpEndpoint = vscode.workspace.getConfiguration('webtestpilot').get<string>('cdpEndpoint') || 'http://localhost:9222';
        const pythonPath = path.join(workspaceRoot, 'webtestpilot', '.venv', 'bin', 'python');
        const cliScriptPath = path.join(workspaceRoot, 'webtestpilot', 'src', 'cli.py');
        const configPath = path.join(workspaceRoot, 'webtestpilot', 'src', 'config.yaml');

        // Verify CLI script exists
        try {
            await fs.access(cliScriptPath);
        } catch (error) {
            vscode.window.showErrorMessage(`Python CLI script not found: ${cliScriptPath}`);
            return;
        }

        // Start tests sequentially with 2-second delays between each
        this._outputChannel.appendLine('\nStarting tests...');

        // Delete all tabs for clean
        this._clearAllTabs();
        
        for (let index = 0; index < tests.length; index++) {
            const test = tests[index];
            
            // Wait 1 seconds between each test start (except for the first one)
            if (index > 0) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            this._outputChannel.appendLine(`Starting test ${index + 1}/${tests.length}: ${test.name}`);
            await this._startSingleTest(test, WorkspaceRootService.getOpenedFolderWorkspaceRoot(), pythonPath, cliScriptPath, configPath, cdpEndpoint);
        }
        
        this._outputChannel.appendLine('\nAll test processes started sequentially');
    }

    /**
     * Starts a single test execution
     */
    private async _startSingleTest(
        test: TestItem,
        workspaceRoot: string,
        pythonPath: string,
        cliScriptPath: string,
        configPath: string,
        cdpEndpoint: string
    ) {
        try {
            // Ensure browser context is initialized
            if (!this._browser) {
                throw new Error('Browser not connected');
            }
            if (!this._context) {
                throw new Error('Browser context not initialized');
            }

            let testData: TestData;
            const testFilePath = path.join(workspaceRoot, '.webtestpilot', test.id);
            try {
                testData = await this._loadAndParseTestFile(test.id, workspaceRoot);
            } catch (error) {
                this._outputChannel.appendLine(`⚠️  Skipping "${test.name}" - ${error instanceof Error ? error.message : String(error)}`);
                return;
            }

            // Create a new page for this test
            const page = await this._context.newPage();
            const cdp = await page.context().newCDPSession(page);
            const { targetInfo } = await cdp.send('Target.getTargetInfo');
            const TARGET_ID = targetInfo.targetId;
            
            this._outputChannel.appendLine(`[${test.name}] Tab index: ${TARGET_ID}`);

            // Create individual log storage for this test
            this._testLogs.set(test.id, { stdout: [], stderr: [] });
            const testOutputChannel = vscode.window.createOutputChannel(`Test: ${test.name}`);
            this._testOutputChannels.set(test.id, testOutputChannel);
            testOutputChannel.show(true);

            // Create execution record
            const execution: TestExecution = {
                testItem: test,
                page,
                targetId: TARGET_ID,
                pythonProcess: null,
                isRunning: true,
                startTime: Date.now(),
                currentStep: 0,
                totalSteps: testData.actions ? testData.actions.length : 0,
                stepsWithVerifications: new Set<number>(),
                verifiedSteps: new Set<number>(),
                completedSteps: new Set<number>()
            };
            this._executions.set(test.id, execution);

            // Start screenshot streaming for this test
            this._outputChannel.appendLine(`[${test.name}] Starting screenshot streaming for tab`);
            this._startScreenshotStream(test.id, page);

            // Update UI
            this._panel.webview.postMessage({
                type: 'testStarted',
                testId: test.id,
                testName: test.name,
                url: testData.url,
                tabIndex: TARGET_ID,
                totalSteps: testData.actions ? testData.actions.length : 0
            });

            // Start Python process
            const pythonProcess = spawn(pythonPath, [
                cliScriptPath,
                testFilePath,
                '--config', configPath,
                '--cdp-endpoint', cdpEndpoint,
                '--target-id', TARGET_ID,
                '--json-output'
            ], {
                env: {
                    ...process.env,
                    BAML_LOG: 'info'
                }
            });

            execution.pythonProcess = pythonProcess;

            const testLogs = this._testLogs.get(test.id)!;

            let stdoutData = '';
            let stderrData = '';

            pythonProcess.stdout.on('data', (data: Buffer) => {
                const text = data.toString();
                stdoutData += text;
                testLogs.stdout.push(text);
                testOutputChannel.append(text);
                this._outputChannel.append(`[${test.name}] ${text}`);
                
                // Parse step information from logs
                this._parseStepUpdates(test.id, text);
                
                // Stream stdout logs to UI
                this._panel.webview.postMessage({
                    type: 'logMessage',
                    testId: test.id,
                    logType: 'stdout',
                    message: text.trim(),
                    timestamp: Date.now()
                });
            });

            pythonProcess.stderr.on('data', (data: Buffer) => {
                const text = data.toString();
                stderrData += text;
                testLogs.stderr.push(text);
                testOutputChannel.append(`${text}`);
                this._outputChannel.append(`[${test.name}] ${text}`);
                
                // Stream stderr logs to UI
                this._panel.webview.postMessage({
                    type: 'logMessage',
                    testId: test.id,
                    logType: 'stderr',
                    message: text.trim(),
                    timestamp: Date.now()
                });
            });

            pythonProcess.on('close', (code: number, signal: string) => {
                execution.isRunning = false;
                execution.endTime = Date.now();
                
                // Stop screenshot streaming
                const interval = this._screenshotIntervals.get(test.id);
                if (interval) {
                    clearInterval(interval);
                    this._screenshotIntervals.delete(test.id);
                    this._outputChannel.appendLine(`[${test.name}] Screenshot streaming stopped`);
                    
                    // Notify UI that streaming has stopped
                    this._panel.webview.postMessage({
                        type: 'streamingStopped',
                        testId: test.id
                    });
                }

                // Parse result
                let result = { success: false, stepsExecuted: 0, errors: [] as string[] };
                
                if (signal === 'SIGTERM' || signal === 'SIGKILL') {
                    this._outputChannel.appendLine(`[${test.name}] ⚠️  Test stopped by user`);
                } else if (code === 0) {
                    const jsonMatch = stdoutData.match(/\{[\s\S]*\}/);
                    if (jsonMatch) {
                        result = JSON.parse(jsonMatch[0]);
                    }
                    this._outputChannel.appendLine(`[${test.name}] ✅ Test completed successfully`);
                } else {
                    result.success = false;
                    
                    // Extract BugReport messages from stdout
                    const bugMessages = this._parseBugReports(stdoutData);
                    if (bugMessages.length > 0) {
                        result.errors = bugMessages;
                        this._outputChannel.appendLine(`[${test.name}] ❌ Test failed with BugReport: ${bugMessages.join('; ')}`);
                    } else {
                        result.errors = [stderrData || `Process exited with code ${code}`];
                        this._outputChannel.appendLine(`[${test.name}] ❌ Test failed with code ${code}`);
                    }
                }

                // Only update result if not already set by verification handlers
                if (!execution.result) {
                    execution.result = result;
                }

                // Store final logs and close individual output channel
                const testLogs = this._testLogs.get(test.id);
                const outputChannel = this._testOutputChannels.get(test.id);
                if (testLogs && outputChannel) {
                    outputChannel.appendLine('');
                    outputChannel.appendLine('='.repeat(60));
                    outputChannel.appendLine('FINAL TEST SUMMARY');
                    outputChannel.appendLine('='.repeat(60));
                    outputChannel.appendLine(`Total stdout lines: ${testLogs.stdout.length}`);
                    outputChannel.appendLine(`Total stderr lines: ${testLogs.stderr.length}`);
                    if (execution.result && execution.result.errors && execution.result.errors.length > 0) {
                        outputChannel.appendLine('Errors encountered:');
                        execution.result.errors.forEach((error, index) => {
                            outputChannel.appendLine(`  ${index + 1}. ${error}`);
                        });
                    }
                    outputChannel.appendLine('='.repeat(60));
                }

                // Only send testFinished if not already sent by verification handlers
                // (verification handlers set execution.result)
                if (!execution.result || execution.result !== result) {
                    // Update UI
                    this._panel.webview.postMessage({
                        type: 'testFinished',
                        testId: test.id,
                        result: execution.result || result,
                        duration: execution.endTime - execution.startTime
                    });
                }
            });

            pythonProcess.on('error', (error: Error) => {
                execution.isRunning = false;
                execution.endTime = Date.now();
                execution.result = {
                    success: false,
                    stepsExecuted: 0,
                    errors: [error.message]
                };

                this._outputChannel.appendLine(`[${test.name}] ❌ Process error: ${error.message}`);
                
                // Keep the page open for inspection - no automatic closing
                
                this._panel.webview.postMessage({
                    type: 'testFinished',
                    testId: test.id,
                    result: execution.result,
                    duration: execution.endTime - execution.startTime
                });
            });

        } catch (error) {
            this._outputChannel.appendLine(`[${test.name}] ❌ Failed to start: ${error}`);
            
            // No cleanup needed for page usage map
            
            this._panel.webview.postMessage({
                type: 'testFinished',
                testId: test.id,
                result: {
                    success: false,
                    stepsExecuted: 0,
                    errors: [String(error)]
                },
                duration: 0
            });
        }
    }

    /**
     * Parse BugReport messages from stderr output
     */
    private _parseBugReports(stderrData: string): string[] {
        const bugReportMatches = stderrData.match(/Bug reported: ([\s\S]*?)(?=\n|$)/g);
        if (bugReportMatches && bugReportMatches.length > 0) {
            return bugReportMatches.map(match => 
                match.replace(/^Bug reported:\s*/, '').trim()
            );
        }
        return [];
    }

    /**
     * Parse step updates from Python process output for a specific test
     */
    private _parseStepUpdates(testId: string, text: string) {
        const execution = this._executions.get(testId);
        if (!execution) {
            return;
        }

        // Parse step execution: "STEP_N: action description"
        const stepMatch = text.match(/STEP_(\d+):\s*(.+)/);
        if (stepMatch) {
            const stepNumber = parseInt(stepMatch[1]);
            const action = stepMatch[2].trim();
            execution.currentStep = stepNumber;
            
            // Send step update to UI
            this._panel.webview.postMessage({
                type: 'stepUpdate',
                testId: testId,
                stepNumber: stepNumber,
                action: action,
                status: 'executing',
                message: `Step ${stepNumber}: ${action}`
            });
        }
        
        // Parse step passed: "STEP_N_PASSED"
        const stepPassedMatch = text.match(/STEP_(\d+)_PASSED/);
        if (stepPassedMatch) {
            const stepNumber = parseInt(stepPassedMatch[1]);
            
            // Track completed step (regardless of verification)
            execution.completedSteps.add(stepNumber);
            
            // Send step passed update to UI
            this._panel.webview.postMessage({
                type: 'stepUpdate',
                testId: testId,
                stepNumber: stepNumber,
                status: 'passed',
                message: `✅ Step ${stepNumber} passed`
            });
        }
        
        // Parse step failed: "STEP_N_FAILED: error message"
        const stepFailedMatch = text.match(/STEP_(\d+)_FAILED:\s*(.+)/);
        if (stepFailedMatch) {
            const stepNumber = parseInt(stepFailedMatch[1]);
            const error = stepFailedMatch[2].trim();
            
            // Send step failed update to UI
            this._panel.webview.postMessage({
                type: 'stepUpdate',
                testId: testId,
                stepNumber: stepNumber,
                status: 'failed',
                message: `❌ Step ${stepNumber} failed: ${error}`,
                error: error
            });
        }
        
        // Parse step verification: "VERIFYING_STEP_N: expectation description"
        const verifyMatch = text.match(/VERIFYING_STEP_(\d+):\s*(.+)/);
        if (verifyMatch) {
            const stepNumber = parseInt(verifyMatch[1]);
            const expectation = verifyMatch[2].trim();
            
            // Send verification update to UI
            this._panel.webview.postMessage({
                type: 'stepUpdate',
                testId: testId,
                stepNumber: stepNumber,
                status: 'verifying',
                message: `Step ${stepNumber}: Verifying - ${expectation}`
            });
        }
        
        // Parse verification passed: "VERIFYING_STEP_N_PASSED"
        const verifyPassedMatch = text.match(/VERIFYING_STEP_(\d+)_PASSED/);
        if (verifyPassedMatch) {
            const stepNumber = parseInt(verifyPassedMatch[1]);
            
            // Mark that this step has verification
            execution.stepsWithVerifications.add(stepNumber);
            
            // Track verified steps
            execution.verifiedSteps.add(stepNumber);
            
            // Send verification passed update to UI
            this._panel.webview.postMessage({
                type: 'stepUpdate',
                testId: testId,
                stepNumber: stepNumber,
                status: 'completed',
                message: `✅ Step ${stepNumber} verification passed`
            });
            
            // Check if all steps with verifications have been verified (meaning all verifications passed)
            if (execution.stepsWithVerifications.size > 0 && 
                execution.verifiedSteps.size === execution.stepsWithVerifications.size) {
                this._outputChannel.appendLine(`[${testId}] ✅ All ${execution.stepsWithVerifications.size} verifications passed - marking test as PASSED`);
                
                // Mark test as passed in UI immediately
                this._panel.webview.postMessage({
                    type: 'testFinished',
                    testId: testId,
                    result: {
                        success: true,
                        stepsExecuted: execution.totalSteps,
                        errors: []
                    },
                    duration: Date.now() - execution.startTime
                });
                
                execution.result = {
                    success: true,
                    stepsExecuted: execution.totalSteps,
                    errors: []
                };
            }
        }
        
        // Parse verification failed: "VERIFYING_STEP_N_FAILED: error message"
        const verifyFailedMatch = text.match(/VERIFYING_STEP_(\d+)_FAILED:\s*(.+)/);
        if (verifyFailedMatch) {
            const stepNumber = parseInt(verifyFailedMatch[1]);
            const error = verifyFailedMatch[2].trim();
            
            // Mark that this step has verification
            execution.stepsWithVerifications.add(stepNumber);
            
            // Send verification failed update to UI
            this._panel.webview.postMessage({
                type: 'stepUpdate',
                testId: testId,
                stepNumber: stepNumber,
                status: 'failed',
                message: `❌ Step ${stepNumber} verification failed: ${error}`,
                error: error
            });
            
            // Mark test as failed immediately in UI
            this._outputChannel.appendLine(`[${testId}] ❌ Test FAILED - verification failed at step ${stepNumber}: ${error}`);
            
            this._panel.webview.postMessage({
                type: 'testFinished',
                testId: testId,
                result: {
                    success: false,
                    stepsExecuted: stepNumber,
                    errors: [error]
                },
                duration: Date.now() - execution.startTime
            });
            
            execution.result = {
                success: false,
                stepsExecuted: stepNumber,
                errors: [error]
            };
        }
    }

    /**
      * Starts screenshot streaming for a specific test
      */
    private _startScreenshotStream(testId: string, page: Page) {
        const captureScreenshot = async () => {
            try {
                // Verify page is still valid and connected
                if (!page || page.isClosed()) {
                    this._outputChannel.appendLine(`[${testId}] Browser tab closed, stopping screenshot streaming`);
                    const interval = this._screenshotIntervals.get(testId);
                    if (interval) {
                        clearInterval(interval);
                        this._screenshotIntervals.delete(testId);
                    }
                    return;
                }

                const imgBuffer = await page.screenshot({
                    type: 'png',
                    fullPage: false,
                    scale: 'device',
                    timeout: 10000
                });
                const base64 = imgBuffer.toString('base64');
                
                // Send screenshot with tab verification info
                this._panel.webview.postMessage({
                    type: 'screenshot',
                    testId: testId,
                    data: base64,
                    timestamp: Date.now(),
                    url: page.url()
                });
            } catch (error) {
                console.error(`Screenshot capture failed for ${testId}:`, error);
                this._outputChannel.appendLine(`[${testId}] Screenshot error: ${error instanceof Error ? error.message : String(error)}`);
                
                // Terminate the interval on exception
                const interval = this._screenshotIntervals.get(testId);
                if (interval) {
                    clearInterval(interval);
                    this._screenshotIntervals.delete(testId);
                    this._outputChannel.appendLine(`[${testId}] Screenshot streaming stopped due to error`);
                }
            }
        };

        // Capture initial screenshot to verify tab connection
        this._outputChannel.appendLine(`[${testId}] Taking initial screenshot to verify tab connection`);
        captureScreenshot();

        // 5 FPS
        const interval = setInterval(captureScreenshot, 200);
        this._screenshotIntervals.set(testId, interval);
        
        this._outputChannel.appendLine(`[${testId}] Screenshot streaming started for browser tab`);
    }

    /**
     * Shows the individual test output channel
     */
    private _showTestLogs(testId: string, testName: string) {
        const outputChannel = this._testOutputChannels.get(testId);
        if (outputChannel) {
            outputChannel.show();
        } else {
            vscode.window.showWarningMessage(`No logs available for test: ${testName}`);
        }
    }

    /**
     * Stops a specific test
     */
    private _stopTest(testId: string) {
        const execution = this._executions.get(testId);
        if (execution && execution.isRunning && execution.pythonProcess) {
            this._outputChannel.appendLine(`[${execution.testItem.name}] Stopping test...`);
            
            // Stop screenshot streaming for this test
            const interval = this._screenshotIntervals.get(testId);
            if (interval) {
                clearInterval(interval);
                this._screenshotIntervals.delete(testId);
                this._outputChannel.appendLine(`[${execution.testItem.name}] Screenshot streaming stopped`);
                
                // Notify UI that streaming has stopped
                this._panel.webview.postMessage({
                    type: 'streamingStopped',
                    testId: testId
                });
            }
            
            execution.pythonProcess.kill('SIGTERM');
            
            setTimeout(() => {
                if (execution.pythonProcess && !execution.pythonProcess.killed) {
                    execution.pythonProcess.kill('SIGKILL');
                }
                
                // Keep the page open for inspection - no automatic closing
            }, 2000);
        }
    }

    /**
     * Stops all running tests
     */
    private _stopAllTests() {
        this._outputChannel.appendLine('Stopping all tests...');
        
        this._executions.forEach((execution, testId) => {
            if (execution.isRunning) {
                this._stopTest(testId);
            }
        });
    }

    /**
     * Shows confirmation dialog before clearing all tabs
     */
    private _confirmClearAllTabs() {
        vscode.window.showWarningMessage(
            'Are you sure you want to close all browser tabs? This will clear all test results.',
            'Yes',
            'No'
        ).then(selection => {
            if (selection === 'Yes') {
                this._clearAllTabs();
            }
        });
    }

    /**
     * Clears all browser tabs
     */
    private _clearAllTabs() {
        this._outputChannel.appendLine('Clearing all browser tabs...');
        
        if (this._context) {
            this._context.pages().forEach(async (page: Page) => {
                if (!page.isClosed()) {
                    await page.close();
                }
            });
            this._outputChannel.appendLine('All browser tabs closed');
        }
        
        // Clear all executions
        this._executions.clear();
        
        // Clear screenshot intervals
        this._screenshotIntervals.forEach((interval) => {
            clearInterval(interval);
        });
        this._screenshotIntervals.clear();
        
        // Update UI to reflect cleared state
        this._panel.webview.postMessage({
            type: 'tabsCleared'
        });
    }

    /**
     * Opens parallel test runner for a folder
     */
    public static async createOrShow(folder: FolderItem, workspaceRoot: string) {
        // Get all tests in folder
        const treeDataProvider = (global as any).webTestPilotTreeDataProvider;
        if (!treeDataProvider) {
            vscode.window.showErrorMessage('Tree data provider not available');
            return;
        }

        const testsInFolder = treeDataProvider.getChildrenTests(folder.id);
        
        if (testsInFolder.length === 0) {
            vscode.window.showInformationMessage(`No test cases found in folder "${folder.name}"`);
            return;
        }

        // If we already have a panel, dispose it and create a new one
        if (ParallelTestPanel.currentPanel) {
            ParallelTestPanel.currentPanel.dispose();
        }

        // Get extension URI from the first workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        // Get the extension context to access extensionUri
        const extensionUri = (global as any).extensionUri as vscode.Uri;
        if (!extensionUri) {
            vscode.window.showErrorMessage('Extension URI not available');
            return;
        }

        // Create a new panel for parallel execution
        const panel = vscode.window.createWebviewPanel(
            'parallelTestRunner',
            `Parallel Tests: ${folder.name}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview-ui', 'dist'),
                    extensionUri,
                ],
            }
        );

        const cdpEndpoint = vscode.workspace.getConfiguration('webtestpilot').get<string>('cdpEndpoint') || 'http://localhost:9222';
        ParallelTestPanel.currentPanel = new ParallelTestPanel(panel, folder, cdpEndpoint, extensionUri);

        // Start tests after a short delay to allow UI to initialize
        setTimeout(() => {
            ParallelTestPanel.currentPanel?._startParallelTests(testsInFolder, workspaceRoot);
        }, 2000);
    }

    /**
     * Gets the HTML content for the webview using React UI
     */
    private _getHtmlForWebview(extensionUri: vscode.Uri): string {
        return loadWebviewHtml(extensionUri, this._panel.webview, 'parallelRunner');
    }

    /**
     * Disposes the panel and cleans up resources
     */
    public dispose() {
        ParallelTestPanel.currentPanel = undefined;

        // Stop all tests
        this._stopAllTests();

        // Stop all screenshot streaming
        this._screenshotIntervals.forEach((interval) => {
            clearInterval(interval);
        });
        this._screenshotIntervals.clear();

        // Close individual test output channels
        this._testOutputChannels.forEach((outputChannel) => {
            outputChannel.appendLine('\nTest execution ended - channel closing.');
            outputChannel.dispose();
        });
        this._testOutputChannels.clear();

        // No page cleanup needed - pages are closed individually

        // Close browser connection
        if (this._browser) {
            this._browser.close().catch((err: Error) => {
                console.error('Error closing browser:', err);
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

        // Close output channel
        this._outputChannel.dispose();
    }
}