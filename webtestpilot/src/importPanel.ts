import * as vscode from 'vscode';
import { TestItem } from './models';
import { WebTestPilotTreeDataProvider } from './treeDataProvider';
import { TestEditorPanel } from './testEditorPanel';

export interface ImportData {
    appName: string;
    url: string;
    requirements: string;
}

export class ImportPanel {
    public static currentPanel: ImportPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        private context: vscode.ExtensionContext,
        private treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        this._panel = panel;

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
        context: vscode.ExtensionContext,
        treeDataProvider: WebTestPilotTreeDataProvider
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

        ImportPanel.currentPanel = new ImportPanel(panel, extensionUri, context, treeDataProvider);
    }

    private _update() {
        this._getHtmlForWebview().then(html => {
            this._panel.webview.html = html;
        });
    }

    private async _handleImport(data: ImportData) {
        if (!data.appName || !data.url) {
            vscode.window.showErrorMessage('App name and URL are required');
            return;
        }

        try {
            console.log('Import data received:', data);
            // Create a new test based on the imported data
            const testName = `${data.appName} - Imported Test`;
            
            // Create the test with basic information and get the created test
            const newTest = await this.treeDataProvider.createTest(testName, undefined);
            
            // Update the test with the imported data
            const updatedTest: TestItem = {
                ...newTest,
                url: data.url,
                actions: data.requirements ? [{
                    action: `Verify requirements: ${data.requirements}`,
                    expectedResult: "Requirements should be met"
                }] : []
            };
            
            await this.treeDataProvider.updateTest(newTest.id, updatedTest);
            
            // Open the test editor for further customization
            TestEditorPanel.createOrShow(
                this.context.extensionUri,
                updatedTest,
                this.treeDataProvider
            );

            vscode.window.showInformationMessage(`Successfully imported "${data.appName}"!`);
            this.dispose();
        } catch (error) {
            console.error('Error during import:', error);
            vscode.window.showErrorMessage(`Failed to import "${data.appName}": ${error}`);
        }
    }

    private async _getHtmlForWebview(): Promise<string> {
        // Read HTML template from file
        const fs = require('fs').promises;
        const htmlPath = require('path').join(__dirname, 'views', 'import.html');
        return await fs.readFile(htmlPath, 'utf-8');
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