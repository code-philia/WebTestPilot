import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { TestItem } from './models';
import { WebTestPilotTreeDataProvider } from './treeDataProvider';

/**
 * TestEditorPanel provides a webview interface for editing test cases
 */
export class TestEditorPanel {
    public static currentPanel: TestEditorPanel | undefined;
    public static readonly viewType = 'testEditor';

    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _testItem: TestItem;
    private _treeDataProvider: WebTestPilotTreeDataProvider;

    private constructor(
        panel: vscode.WebviewPanel,
        testItem: TestItem,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        this._panel = panel;
        this._testItem = { ...testItem };
        this._treeDataProvider = treeDataProvider;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        // This happens when user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'save':
                        this._saveTest(message.data);
                        return;
                    case 'updateTest':
                        this._testItem = { ...this._testItem, ...message.data };
                        this._updatePanelTitle();
                        return;
                    case 'runTest':
                        // Validate test has actions before running
                        if (!this._testItem.actions || this._testItem.actions.length === 0) {
                            vscode.window.showWarningMessage('Cannot run test: No actions defined. Please add test actions before running.');
                            return;
                        }
                        // Execute the actual runTest command
                        vscode.commands.executeCommand('webtestpilot.runTest', this._testItem);
                        return;
                    case 'close':
                        this.dispose();
                        return;
                    case 'showError':
                        vscode.window.showErrorMessage(message.text || 'An error occurred');
                        return;
                }
            },
            undefined,
            this._disposables
        );
    }

    private async loadTestFromFile(testId: string): Promise<TestItem> {
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            throw new Error('No workspace folder found');
        }
        const testFilePath = path.join(workspaceRoot, '.webtestpilot', testId);
        const content = await fs.readFile(testFilePath, 'utf-8');
        const testData = JSON.parse(content);
        
        return {
            id: testId,
            name: testData.name || this._testItem.name,
            type: 'test',
            url: testData.url || '',
            actions: testData.actions || [],
            folderId: this._testItem.folderId,
            createdAt: new Date(testData.createdAt || Date.now()),
            updatedAt: new Date(testData.updatedAt || Date.now())
        };
    }

    public static async createOrShow(
        extensionUri: vscode.Uri,
        testItem: TestItem,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (TestEditorPanel.currentPanel) {
            TestEditorPanel.currentPanel._panel.reveal(column);
            TestEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
            
            // Only load fresh data if current test is different or has no actions
            if (TestEditorPanel.currentPanel._testItem.id !== testItem.id || 
                !TestEditorPanel.currentPanel._testItem.actions || 
                TestEditorPanel.currentPanel._testItem.actions.length === 0) {
                try {
                    const freshTestItem = await TestEditorPanel.currentPanel.loadTestFromFile(testItem.id);
                    TestEditorPanel.currentPanel._testItem = freshTestItem;
                } catch (error) {
                    console.error('Failed to load fresh test data:', error);
                    // Continue with current data if file load fails
                }
            }
            
            TestEditorPanel.currentPanel._updatePanelTitle();
            TestEditorPanel.currentPanel._update();
            return;
        }

        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel(
            TestEditorPanel.viewType,
            `Edit Test: ${testItem.name}`,
            column || vscode.ViewColumn.One,
            {
                // Enable javascript in the webview
                enableScripts: true,
                // And restrict the webview to only loading content from our extension's directory
                localResourceRoots: [extensionUri]
            }
        );

        const editorPanel = new TestEditorPanel(panel, testItem, treeDataProvider);
        
        // Load fresh data from file for new panel
        try {
            const freshTestItem = await editorPanel.loadTestFromFile(testItem.id);
            editorPanel._testItem = freshTestItem;
        } catch (error) {
            console.error('Failed to load test data:', error);
            // Continue with provided testItem if file load fails
        }
        
        editorPanel._updatePanelTitle();
        editorPanel._update();
        
        TestEditorPanel.currentPanel = editorPanel;
    }

    private _updatePanelTitle() {
        this._panel.title = `Edit Test: ${this._testItem.name}`;
    }

    private async _update() {
        // Only load fresh data if we don't have current data or if explicitly requested
        if (!this._testItem.actions || this._testItem.actions.length === 0) {
            try {
                const freshTestItem = await this.loadTestFromFile(this._testItem.id!);
                // Only overwrite if current data is empty
                if (!this._testItem.actions || this._testItem.actions.length === 0) {
                    this._testItem = { ...this._testItem, ...freshTestItem };
                }
            } catch (error) {
                console.error('Failed to load fresh data:', error);
                // Continue with current data if file load fails
            }
        }
        
        this._updatePanelTitle();
        const html = await this._getHtmlForWebview();
        this._panel.webview.html = html;
    }

    private async _saveTest(data: any) {
        // Validate required fields
        if (!data.name || data.name.trim() === '') {
            vscode.window.showErrorMessage('Test name is required');
            return;
        }

        // Preserve existing data and merge with new data
        this._testItem = {
            ...this._testItem,
            name: data.name.trim(),
            url: data.url ? data.url.trim() : '',
            actions: Array.isArray(data.actions) ? data.actions : (this._testItem.actions || []),
            updatedAt: new Date()
        };
        
        this._updatePanelTitle();
        
        try {
            await this._treeDataProvider.updateTest(this._testItem.id, this._testItem);
            vscode.window.showInformationMessage('Test saved successfully!');
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save test: ${errorMessage}`);
            console.error('Save error:', error);
        }
    }

    private async _getHtmlForWebview(): Promise<string> {
        const testItem = this._testItem;
        const actions = testItem.actions || [];
        
        // Read HTML template from file
        const htmlPath = path.join(__dirname, 'views', 'test-editor.html');
        let htmlTemplate = await fs.readFile(htmlPath, 'utf-8');
        
        // Helper function to escape HTML attributes
        const escapeHtml = (text: string): string => {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        };

        // Replace placeholders in template
        htmlTemplate = htmlTemplate
            .replace(/\{\{TEST_NAME\}\}/g, escapeHtml(testItem.name))
            .replace(/\{\{TEST_NAME_VALUE\}\}/g, escapeHtml(testItem.name))
            .replace(/\{\{TEST_URL_VALUE\}\}/g, escapeHtml(testItem.url || ''))
            .replace(/\{\{ACTIONS_LIST\}\}/g, actions.map((action, index) => `
                <div class="action-item compact" data-index="${index}">
                    <div class="action-row">
                        <span class="action-number">${index + 1}.</span>
                        <input type="text" class="action-text compact" placeholder="Action" value="${escapeHtml(action.action || '')}" />
                        <button class="btn btn-danger compact" onclick="removeAction(${index})">×</button>
                    </div>
                    <div class="action-row">
                        <span class="action-number">→</span>
                        <input type="text" class="expected-result compact" placeholder="Expected result" value="${escapeHtml(action.expectedResult || '')}" />
                    </div>
                </div>
            `).join(''));

        // Add JSON data script with fallback
        const jsonScript = `<script type="application/json" id="actionsJson">${JSON.stringify(actions)}</script>`;
        htmlTemplate = htmlTemplate.replace('</body>', `${jsonScript}</body>`);
        
        // Also add a debug script to verify actions are loaded
        const debugScript = `<script>console.log('Actions injected:', ${JSON.stringify(actions)});</script>`;
        htmlTemplate = htmlTemplate.replace('</body>', `${debugScript}</body>`);

        return htmlTemplate;
    }

    public dispose() {
        TestEditorPanel.currentPanel = undefined;

        // Clean up our resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}