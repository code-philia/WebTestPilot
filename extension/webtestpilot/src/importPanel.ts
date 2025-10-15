import * as vscode from 'vscode';

export interface ImportData {
    appName: string;
    url: string;
    requirements: string;
}

export class ImportPanel {
    public static currentPanel: ImportPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _onDidImport: (data: ImportData) => void;

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        onDidImport: (data: ImportData) => void
    ) {
        this._panel = panel;
        this._onDidImport = onDidImport;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'import':
                        this._handleImport(message.data);
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
        onDidImport: (data: ImportData) => void
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (ImportPanel.currentPanel) {
            ImportPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel(
            ImportPanel.viewType,
            'Import Web App',
            column || vscode.ViewColumn.One,
            {
                // Enable javascript in the webview
                enableScripts: true,
                // And restrict the webview to only loading content from our extension's directory
                localResourceRoots: [extensionUri]
            }
        );

        ImportPanel.currentPanel = new ImportPanel(panel, extensionUri, onDidImport);
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
    }

    private _handleImport(data: ImportData) {
        if (!data.appName || !data.url) {
            vscode.window.showErrorMessage('App name and URL are required');
            return;
        }

        this._onDidImport(data);
        vscode.window.showInformationMessage(`Successfully imported "${data.appName}"!`);
        this.dispose();
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Import Web App</title>
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
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        .title {
            font-size: 1.5em;
            font-weight: bold;
            color: var(--vscode-foreground);
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: var(--vscode-foreground);
        }
        input[type="text"], input[type="url"], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            box-sizing: border-box;
            border-radius: 4px;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            font-weight: 500;
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
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 30px;
        }
        .description {
            color: var(--vscode-descriptionForeground);
            font-size: 0.9em;
            margin-bottom: 20px;
            line-height: 1.4;
        }
        .required {
            color: var(--vscode-errorForeground);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Import Web App</div>
        </div>

        <div class="description">
            Import a web application to create automated tests. Provide the app details and requirements below.
        </div>

        <div class="form-group">
            <label for="appName">App Name <span class="required">*</span></label>
            <input type="text" id="appName" placeholder="My Web App" required />
        </div>

        <div class="form-group">
            <label for="appUrl">App URL <span class="required">*</span></label>
            <input type="url" id="appUrl" placeholder="https://example.com" required />
        </div>

        <div class="form-group">
            <label for="requirements">Requirements</label>
            <textarea id="requirements" placeholder="Describe what you want to test on this webpage..."></textarea>
        </div>

        <div class="button-group">
            <button class="btn btn-secondary" onclick="closePanel()">Cancel</button>
            <button class="btn btn-primary" onclick="importApp()">Import</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        function importApp() {
            const appName = document.getElementById('appName').value.trim();
            const appUrl = document.getElementById('appUrl').value.trim();
            const requirements = document.getElementById('requirements').value.trim();
            
            if (!appName) {
                vscode.postMessage({
                    command: 'showError',
                    text: 'App name is required'
                });
                return;
            }
            
            if (!appUrl) {
                vscode.postMessage({
                    command: 'showError',
                    text: 'App URL is required'
                });
                return;
            }
            
            // Basic URL validation
            try {
                new URL(appUrl);
            } catch (e) {
                vscode.postMessage({
                    command: 'showError',
                    text: 'Please enter a valid URL'
                });
                return;
            }
            
            vscode.postMessage({
                command: 'import',
                data: {
                    appName,
                    appUrl,
                    requirements
                }
            });
        }
        
        function closePanel() {
            vscode.postMessage({
                command: 'close'
            });
        }
        
        // Allow Enter key to submit when in input fields
        document.getElementById('appName').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('appUrl').focus();
            }
        });
        
        document.getElementById('appUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('requirements').focus();
            }
        });
        
        document.getElementById('requirements').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                importApp();
            }
        });
    </script>
</body>
</html>`;
    }

    public dispose() {
        ImportPanel.currentPanel = undefined;

        // Clean up our resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private static readonly viewType = 'importPanel';
}