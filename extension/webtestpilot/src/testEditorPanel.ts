import * as vscode from 'vscode';
import { TestItem, TestAction } from './models';

export class TestEditorPanel {
    public static currentPanel: TestEditorPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _testItem: TestItem;
    private _onDidSave: (testItem: TestItem) => void;

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        testItem: TestItem,
        onDidSave: (testItem: TestItem) => void
    ) {
        this._panel = panel;
        this._testItem = { ...testItem };
        this._onDidSave = onDidSave;

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
        onDidSave: (testItem: TestItem) => void
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (TestEditorPanel.currentPanel) {
            TestEditorPanel.currentPanel._panel.reveal(column);
            TestEditorPanel.currentPanel._testItem = { ...testItem };
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

        TestEditorPanel.currentPanel = new TestEditorPanel(panel, extensionUri, testItem, onDidSave);
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _saveTest(data: any) {
        this._testItem = {
            ...this._testItem,
            name: data.name,
            url: data.url,
            actions: data.actions,
            updatedAt: new Date()
        };
        
        this._onDidSave(this._testItem);
        vscode.window.showInformationMessage('Test saved successfully!');
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
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

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Test: ${testItem.name}</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: var(--vscode-foreground);
        }
        input[type="text"], input[type="url"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            box-sizing: border-box;
        }
        textarea {
            min-height: 60px;
            resize: vertical;
        }
        .actions-section {
            margin-top: 30px;
        }
        .action-item {
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: var(--vscode-editor-background);
        }
        .action-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .action-number {
            font-weight: bold;
            color: var(--vscode-descriptionForeground);
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
        }
        .btn-primary {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .btn-primary:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        .btn-secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        .btn-secondary:hover {
            background-color: var(--vscode-button-secondaryHoverBackground);
        }
        .btn-danger {
            background-color: var(--vscode-errorBackground);
            color: var(--vscode-button-foreground);
        }
        .btn-danger:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--vscode-panel-border);
            position: sticky;
            top: 0;
            background-color: var(--vscode-editor-background);
            z-index: 10;
        }
        .title {
            font-size: 1.5em;
            font-weight: bold;
            color: var(--vscode-foreground);
        }
        .button-group {
            display: flex;
            gap: 8px;
        }
        .action-item.compact {
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 8px;
            background-color: var(--vscode-editor-background);
        }
        .action-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }
        .action-row:last-child {
            margin-bottom: 0;
        }
        .action-number {
            font-weight: bold;
            color: var(--vscode-descriptionForeground);
            min-width: 20px;
            text-align: right;
        }
        .action-text.compact, .expected-result.compact {
            flex: 1;
            padding: 4px 6px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            min-height: 24px;
        }
        .btn.compact {
            padding: 4px 8px;
            font-size: 12px;
            min-width: 24px;
            border-radius: 3px;
        }
        .btn-danger.compact {
            background-color: var(--vscode-errorBackground);
            color: var(--vscode-button-foreground);
            border: none;
        }
        .btn-danger.compact:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Edit Test: ${testItem.name}</div>
            <div class="button-group">
                <button class="btn btn-primary" onclick="saveTest()">Save Test</button>
                <button class="btn btn-secondary" onclick="runTest()">Run Test</button>
                <button class="btn btn-secondary" onclick="closePanel()">Close</button>
            </div>
        </div>

        <div class="form-group">
            <label for="testName">Test Name:</label>
            <input type="text" id="testName" value="${escapeHtml(testItem.name)}" />
        </div>

        <div class="form-group">
            <label for="testUrl">URL:</label>
            <input type="url" id="testUrl" value="${escapeHtml(testItem.url || '')}" placeholder="https://example.com" />
        </div>

        <div class="actions-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3>Actions</h3>
                <button class="btn btn-secondary" onclick="addAction()">Add Action</button>
            </div>
            
            <div id="actionsList">
                ${actions.map((action, index) => `
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
                `).join('')}
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        function addAction() {
            const actionsList = document.getElementById('actionsList');
            const actionCount = actionsList.children.length;
            
            const actionItem = document.createElement('div');
            actionItem.className = 'action-item compact';
            actionItem.dataset.index = actionCount;
            
            actionItem.innerHTML = \`
                <div class="action-row">
                    <span class="action-number">\${actionCount + 1}.</span>
                    <input type="text" class="action-text compact" placeholder="Action" />
                    <button class="btn btn-danger compact" onclick="removeAction(\${actionCount})">×</button>
                </div>
                <div class="action-row">
                    <span class="action-number">→</span>
                    <input type="text" class="expected-result compact" placeholder="Expected result" />
                </div>
            \`;
            
            actionsList.appendChild(actionItem);
            updateActionNumbers();
        }
        
        function removeAction(index) {
            const actionItem = document.querySelector(\`.action-item.compact[data-index="\${index}"]\`);
            if (actionItem) {
                actionItem.remove();
                updateActionNumbers();
            }
        }
        
        function updateActionNumbers() {
            const actionItems = document.querySelectorAll('.action-item.compact');
            actionItems.forEach((item, index) => {
                item.dataset.index = index;
                const numberSpans = item.querySelectorAll('.action-number');
                if (numberSpans[0]) {
                    numberSpans[0].textContent = \`\${index + 1}.\`;
                }
                const removeBtn = item.querySelector('.btn-danger.compact');
                if (removeBtn) {
                    removeBtn.setAttribute('onclick', \`removeAction(\${index})\`);
                }
            });
        }
        
        function getActionsData() {
            const actionItems = document.querySelectorAll('.action-item.compact');
            const actions = [];
            
            actionItems.forEach(item => {
                const actionText = item.querySelector('.action-text.compact').value.trim();
                const expectedResult = item.querySelector('.expected-result.compact').value.trim();
                
                if (actionText || expectedResult) {
                    actions.push({
                        action: actionText,
                        expectedResult: expectedResult
                    });
                }
            });
            
            return actions;
        }
        
        function saveTest() {
            const name = document.getElementById('testName').value.trim();
            const url = document.getElementById('testUrl').value.trim();
            const actions = getActionsData();
            
            if (!name) {
                vscode.postMessage({
                    command: 'showError',
                    text: 'Test name is required'
                });
                return;
            }
            
            vscode.postMessage({
                command: 'save',
                data: {
                    name,
                    url,
                    actions
                }
            });
        }
        
        function closePanel() {
            vscode.postMessage({
                command: 'close'
            });
        }
        
        function runTest() {
            const name = document.getElementById('testName').value.trim();
            const actions = getActionsData();
            
            vscode.postMessage({
                command: 'runTest',
                data: {
                    name,
                    actionCount: actions.length
                }
            });
        }
        
        // Auto-save on input changes
        document.getElementById('testName').addEventListener('input', function() {
            vscode.postMessage({
                command: 'updateTest',
                data: {
                    name: this.value.trim()
                }
            });
        });
        
        document.getElementById('testUrl').addEventListener('input', function() {
            vscode.postMessage({
                command: 'updateTest',
                data: {
                    url: this.value.trim()
                }
            });
        });
    </script>
</body>
</html>`;
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