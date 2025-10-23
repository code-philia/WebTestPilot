import * as vscode from 'vscode';
import { TestItem } from './models';
import { WebTestPilotTreeDataProvider } from './treeDataProvider';

export class TestEditorPanel {
    public static currentPanel: TestEditorPanel | undefined;
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
        // This happens when the user closes the panel or when the panel is closed programmatically
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
                        return;
                    case 'runTest':
                        // Execute the actual runTest command
                        vscode.commands.executeCommand('webtestpilot.runTest', this._testItem);
                        return;
                    case 'close':
                        this.dispose();
                        return;
                }
            },
            undefined,
            this._disposables
        );
    }

    public static createOrShow(
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
            TestEditorPanel.currentPanel._testItem = { ...testItem };
            TestEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
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

        TestEditorPanel.currentPanel = new TestEditorPanel(panel, testItem, treeDataProvider);
    }

    private _update() {
        this._getHtmlForWebview().then(html => {
            this._panel.webview.html = html;
        });
    }

    private async _saveTest(data: any) {
        this._testItem = {
            ...this._testItem,
            name: data.name,
            url: data.url,
            actions: data.actions,
            updatedAt: new Date()
        };
        
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
        
        // Helper function to escape HTML attributes
        const escapeHtml = (text: string): string => {
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        };

        // Generate actions list HTML
        const actionsListHtml = actions.map((action, index) => `
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
        `).join('');

        // Read HTML template from file
        const fs = require('fs').promises;
        const htmlPath = require('path').join(__dirname, 'views', 'test-editor.html');
        let htmlContent = await fs.readFile(htmlPath, 'utf-8');
        
        // Replace placeholders
        htmlContent = htmlContent.replace(/\{\{TEST_NAME\}\}/g, escapeHtml(testItem.name));
        htmlContent = htmlContent.replace(/\{\{TEST_NAME_VALUE\}\}/g, escapeHtml(testItem.name));
        htmlContent = htmlContent.replace(/\{\{TEST_URL_VALUE\}\}/g, escapeHtml(testItem.url || ''));
        htmlContent = htmlContent.replace(/\{\{ACTIONS_LIST\}\}/g, actionsListHtml);
        
        return htmlContent;
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

    private static readonly viewType = 'testEditor';
}