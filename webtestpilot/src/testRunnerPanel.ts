import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { chromium } from 'playwright-core';
import { TestItem } from './models';
import { WorkspaceRootService } from './workspaceRootService.js';

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
    private _page: any;
    private _screenshotInterval: NodeJS.Timeout | undefined;
    private _pythonProcess: any = undefined;
    private _isTestRunning: boolean = false;

    private constructor(
        panel: vscode.WebviewPanel,
        testItem: TestItem,
        cdpEndpoint: string
    ) {
        this._panel = panel;
        this._testItem = testItem;

        // Set the webview's initial html content
        this._getHtmlForWebview().then(html => {
            this._panel.webview.html = html;
        });

        // Connect to CDP and start streaming
        this._connectToBrowser(cdpEndpoint);

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.type) {
                    case 'ready':
                        console.log('Webview ready for screenshots');
                        return;
                    case 'navigate':
                        if (this._page) {
                            this._page.goto(message.url).catch((err: Error) => {
                                vscode.window.showErrorMessage(`Navigation failed: ${err.message}`);
                            });
                        }
                        return;
                    case 'stopTest':
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
            vscode.window.showInformationMessage(`Connecting to browser at ${cdpEndpoint}...`);
            
            // Connect to CDP
            this._browser = await chromium.connectOverCDP(cdpEndpoint);
            
            // Get the first available page or create a new one
            const contexts = this._browser.contexts();
            const context = contexts.length > 0 ? contexts[0] : await this._browser.newContext();
            const pages = context.pages();
            this._page = pages.length > 0 ? pages[0] : await context.newPage();

            vscode.window.showInformationMessage(`✅ Connected to browser! Streaming live view...`);

            // Send initial info
            this._panel.webview.postMessage({
                type: 'connected',
                url: this._page.url()
            });

            // Listen to console messages from the browser
            this._page.on('console', (msg: any) => {
                this._panel.webview.postMessage({
                    type: 'console',
                    level: msg.type(),
                    text: msg.text()
                });
            });

            // Listen to page navigation
            this._page.on('framenavigated', (frame: any) => {
                if (frame === this._page.mainFrame()) {
                    this._panel.webview.postMessage({
                        type: 'navigation',
                        url: frame.url()
                    });
                }
            });

            // Start screenshot streaming (every 500ms for near real-time)
            this._startScreenshotStream();

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
     * Stops the currently running Python test process
     */
    private _stopTest() {
        if (this._pythonProcess && this._isTestRunning) {
            console.log('Stopping Python test process...');
            
            // Send SIGTERM to gracefully terminate the process
            this._pythonProcess.kill('SIGTERM');
            
            // If it doesn't stop within 2 seconds, force kill it
            setTimeout(() => {
                if (this._pythonProcess && !this._pythonProcess.killed) {
                    console.log('Force killing Python process...');
                    this._pythonProcess.kill('SIGKILL');
                }
            }, 2000);
            
            this._isTestRunning = false;
            
            // Update UI
            this._panel.webview.postMessage({
                type: 'testStopped'
            });
            
            vscode.window.showWarningMessage('Test execution stopped by user');
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
            if (!this._page) {return;}
            
            try {
                const imgBuffer = await this._page.screenshot({ 
                    type: 'png',  // Changed from jpeg to png for higher quality
                    fullPage: false,
                    scale: 'device'  // Use device pixel ratio for crisp images
                });
                const base64 = imgBuffer.toString('base64');
                
                this._panel.webview.postMessage({
                    type: 'screenshot',
                    data: base64
                });
            } catch (error) {
                console.error('Screenshot capture failed:', error);
            }
        };

        // Capture initial screenshot
        captureScreenshot();

        // Then capture every 500ms for near real-time updates
        this._screenshotInterval = setInterval(captureScreenshot, 50);
    }

    /**
     * Opens a test in a live browser viewer with CDP connection and runs the Python agent
     * @param testItem The test to run
     * @param workspaceRoot The workspace root path
     */
    public static async createOrShow(testItem: TestItem, workspaceRoot: string) {
        // Load test data from file
        const testFilePath = path.join(workspaceRoot, '.webtestpilot', testItem.id);
        
        try {
            const content = await fs.readFile(testFilePath, 'utf-8');
            const testData = JSON.parse(content);
            
            // Get the URL from the test data
            const url = testData.url || testItem.url;
            
            // Get CDP endpoint from configuration or use default
            const cdpEndpoint = vscode.workspace.getConfiguration('webtestpilot').get<string>('cdpEndpoint') || 'http://localhost:9222';

            // Validate test has actions
            if (!testData.actions || testData.actions.length === 0) {
                vscode.window.showWarningMessage(
                    `Test "${testItem.name}" has no actions defined. Please add test actions before running.`
                );
                return;
            }

            // Create output channel for test execution logs
            const outputChannel = vscode.window.createOutputChannel('WebTestPilot Test Runner');
            outputChannel.clear();
            outputChannel.show(true);
            
            outputChannel.appendLine('='.repeat(60));
            outputChannel.appendLine(`Running Test: ${testItem.name}`);
            outputChannel.appendLine('='.repeat(60));
            outputChannel.appendLine(`Test File: ${testFilePath}`);
            outputChannel.appendLine(`URL: ${url || 'Not specified'}`);
            outputChannel.appendLine(`CDP Endpoint: ${cdpEndpoint}`);
            outputChannel.appendLine(`Actions: ${testData.actions.length}`);
            outputChannel.appendLine('='.repeat(60));
            outputChannel.appendLine('');

            // If we already have a panel, dispose it and create a new one
            if (TestRunnerPanel.currentPanel) {
                TestRunnerPanel.currentPanel.dispose();
            }

            // Create a new panel for live browser view
            const panel = vscode.window.createWebviewPanel(
                'liveBrowser',
                `Live Browser: ${testItem.name}`,
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            TestRunnerPanel.currentPanel = new TestRunnerPanel(panel, testItem, cdpEndpoint);

            // Show progress notification with cancel button
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Running test: ${testItem.name}`,
                cancellable: true
            }, async (progress, token) => {
                // Handle cancellation from notification
                token.onCancellationRequested(() => {
                    console.log('Test cancelled from notification');
                    TestRunnerPanel.currentPanel?._stopTest();
                });
                progress.report({ message: 'Starting Python agent...' });
                
                // Run the Python CLI to execute the test
                workspaceRoot = WorkspaceRootService.getWorkspaceRoot();
                console.log('Using workspace root:', workspaceRoot);
                // const pythonPath = "/Users/abcbum/Desktop/Projects/Cophi/WebTestPilot/extension/webtestpilot/webtestpilot/.venv/bin/python";
                const pythonPath = path.join(workspaceRoot, 'webtestpilot', '.venv', 'bin', 'python');
                const cliScriptPath = path.join(workspaceRoot, 'webtestpilot', 'src', 'cli.py');
                const configPath = path.join(workspaceRoot, 'webtestpilot', 'src', 'config.yaml');
                const traceOutputPath = path.join(workspaceRoot, '.webtestpilot', 'traces', `${testItem.id}-trace.zip`);
                
                // Ensure traces directory exists
                const tracesDir = path.dirname(traceOutputPath);
                await fs.mkdir(tracesDir, { recursive: true });
                
                outputChannel.appendLine(`Workspace Root: ${workspaceRoot}`);
                outputChannel.appendLine(`Python: ${pythonPath}`);
                outputChannel.appendLine(`CLI Script: ${cliScriptPath}`);
                outputChannel.appendLine(`Config: ${configPath}`);
                outputChannel.appendLine(`Trace Output: ${traceOutputPath}`);
                outputChannel.appendLine('');
                
                // Verify CLI script exists
                try {
                    await fs.access(cliScriptPath);
                    outputChannel.appendLine('✓ CLI script found');
                } catch (error) {
                    outputChannel.appendLine(`✗ CLI script NOT FOUND: ${cliScriptPath}`);
                    vscode.window.showErrorMessage(
                        `Python CLI script not found at: ${cliScriptPath}\n\n` +
                        `Make sure you have opened the correct workspace folder.\n` +
                        `Expected workspace: .../WebTestPilot/extension/webtestpilot`
                    );
                    throw new Error(`CLI script not found: ${cliScriptPath}`);
                }
                
                outputChannel.appendLine('Executing Python agent...');
                outputChannel.appendLine('');

                try {
                    // Execute Python CLI
                    const { spawn } = require('child_process');
                    const pythonProcess = spawn(pythonPath, [
                        cliScriptPath,
                        testFilePath,
                        '--config', configPath,
                        '--cdp-endpoint', cdpEndpoint,
                        '--trace-output', traceOutputPath,
                        '--json-output'
                    ]);

                    // Store process reference for cancellation
                    if (TestRunnerPanel.currentPanel) {
                        TestRunnerPanel.currentPanel._pythonProcess = pythonProcess;
                        TestRunnerPanel.currentPanel._isTestRunning = true;
                        
                        // Update webview to show stop button
                        TestRunnerPanel.currentPanel._panel.webview.postMessage({
                            type: 'testStarted'
                        });
                    }

                    let stdoutData = '';
                    let stderrData = '';

                    pythonProcess.stdout.on('data', (data: Buffer) => {
                        const text = data.toString();
                        stdoutData += text;
                        outputChannel.append(text);
                    });

                    pythonProcess.stderr.on('data', (data: Buffer) => {
                        const text = data.toString();
                        stderrData += text;
                        outputChannel.append(`${text}`);
                    });

                    await new Promise<void>((resolve, reject) => {
                        pythonProcess.on('close', (code: number, signal: string) => {
                            // Clear running state
                            if (TestRunnerPanel.currentPanel) {
                                TestRunnerPanel.currentPanel._isTestRunning = false;
                                TestRunnerPanel.currentPanel._pythonProcess = undefined;
                                
                                // Update webview
                                TestRunnerPanel.currentPanel._panel.webview.postMessage({
                                    type: 'testFinished'
                                });
                            }
                            
                            outputChannel.appendLine('');
                            outputChannel.appendLine('='.repeat(60));
                            
                            // Check if process was terminated by signal (user stopped it)
                            if (signal === 'SIGTERM' || signal === 'SIGKILL') {
                                outputChannel.appendLine('⚠️  Test execution stopped by user');
                                outputChannel.appendLine('='.repeat(60));
                                resolve();
                                return;
                            }
                            
                            if (code === 0) {
                                outputChannel.appendLine('✅ Test execution completed successfully!');
                                
                                // Try to parse JSON result
                                try {
                                    const jsonMatch = stdoutData.match(/\{[\s\S]*\}/);
                                    if (jsonMatch) {
                                        const result = JSON.parse(jsonMatch[0]);
                                        outputChannel.appendLine('');
                                        outputChannel.appendLine('Test Results:');
                                        outputChannel.appendLine(`  Success: ${result.success}`);
                                        outputChannel.appendLine(`  Steps Executed: ${result.steps_executed || 0}`);
                                        if (result.errors && result.errors.length > 0) {
                                            outputChannel.appendLine(`  Errors: ${result.errors.join(', ')}`);
                                        }
                                    }
                                } catch (e) {
                                    // Ignore JSON parse errors
                                }
                                
                                outputChannel.appendLine('');
                                outputChannel.appendLine(`Trace saved to: ${traceOutputPath}`);
                                
                                vscode.window.showInformationMessage(
                                    `✅ Test "${testItem.name}" completed successfully!`,
                                    'View Trace',
                                    'View Output'
                                ).then(selection => {
                                    if (selection === 'View Trace') {
                                        vscode.commands.executeCommand('vscode.open', vscode.Uri.file(traceOutputPath));
                                    } else if (selection === 'View Output') {
                                        outputChannel.show();
                                    }
                                });
                                
                                resolve();
                            } else {
                                outputChannel.appendLine(`❌ Test execution failed with exit code: ${code}`);
                                if (stderrData) {
                                    outputChannel.appendLine('');
                                    outputChannel.appendLine('Error Output:');
                                    outputChannel.appendLine(stderrData);
                                }
                                
                                vscode.window.showErrorMessage(
                                    `❌ Test "${testItem.name}" failed. Check output for details.`,
                                    'View Output'
                                ).then(selection => {
                                    if (selection === 'View Output') {
                                        outputChannel.show();
                                    }
                                });
                                
                                reject(new Error(`Python process exited with code ${code}`));
                            }
                            
                            outputChannel.appendLine('='.repeat(60));
                        });

                        pythonProcess.on('error', (error: Error) => {
                            outputChannel.appendLine('');
                            outputChannel.appendLine(`❌ Failed to start Python process: ${error.message}`);
                            vscode.window.showErrorMessage(
                                `Failed to run test: ${error.message}`,
                                'View Output'
                            ).then(selection => {
                                if (selection === 'View Output') {
                                    outputChannel.show();
                                }
                            });
                            reject(error);
                        });
                    });

                } catch (error) {
                    outputChannel.appendLine('');
                    outputChannel.appendLine(`❌ Error: ${error}`);
                    throw error;
                }
            });

            console.log('Test execution completed:', {
                testName: testItem.name,
                url: url,
                cdpEndpoint: cdpEndpoint,
                actionsCount: testData.actions?.length || 0
            });
        } catch (error) {
            console.error('Error running test:', error);
            vscode.window.showErrorMessage(`Failed to run test: ${error}`);
        }
    }

    /**
     * Gets the HTML content for the webview
     */
    private async _getHtmlForWebview(): Promise<string> {
        const testName = this._testItem.name;
        
        // Read HTML template from file
        const fs = require('fs').promises;
        const htmlPath = require('path').join(__dirname, 'views', 'live-browser.html');
        let htmlContent = await fs.readFile(htmlPath, 'utf-8');
        
        // Replace the test name placeholder
        htmlContent = htmlContent.replace(/\{\{TEST_NAME\}\}/g, testName);
        
        return htmlContent;
    }



    /**
     * Disposes the panel and cleans up resources
     */
    public dispose() {
        TestRunnerPanel.currentPanel = undefined;

        // Stop any running test
        if (this._pythonProcess && this._isTestRunning) {
            console.log('Killing Python process on dispose');
            this._pythonProcess.kill('SIGTERM');
        }

        // Stop screenshot streaming
        if (this._screenshotInterval) {
            clearInterval(this._screenshotInterval);
        }

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
    }
}
