import * as vscode from "vscode";
import { EnvironmentItem } from "../models";
import { WebTestPilotTreeDataProvider } from "../treeDataProvider";
import { loadWebviewHtml } from "../utils/webviewLoader";

/**
 * EnvironmentEditorPanel provides a webview interface for editing environment variables
 */
export class EnvironmentEditorPanel {
    public static currentPanel: EnvironmentEditorPanel | undefined;
    public static readonly viewType = "environmentEditor";

    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _environmentItem: EnvironmentItem;
    private _treeDataProvider: WebTestPilotTreeDataProvider;

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        environmentItem: EnvironmentItem,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        this._panel = panel;
        this._environmentItem = environmentItem;
        this._treeDataProvider = treeDataProvider;

        // Set the webview's HTML content
        this._panel.webview.html = this._getHtmlForWebview();

        // Listen for panel disposal
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                case "ready":
                    // Webview is ready, send initial data
                    this._sendEnvironmentData();
                    return;
                case "save":
                    await this._saveEnvironment(message.data);
                    return;
                case "updateEnvironment":
                    this._environmentItem = { ...this._environmentItem, ...message.data };
                    this._updatePanelTitle();
                    return;
                case "close":
                    this.dispose();
                    return;
                case "showError":
                    vscode.window.showErrorMessage(message.text || "An error occurred");
                    return;
                }
            },
            undefined,
            this._disposables
        );
    }

    public static createOrShow(
        extensionUri: vscode.Uri,
        environmentItem: EnvironmentItem,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it and update the environment
        if (EnvironmentEditorPanel.currentPanel) {
            EnvironmentEditorPanel.currentPanel._panel.reveal(column);
            EnvironmentEditorPanel.currentPanel._environmentItem = environmentItem;
            EnvironmentEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
            EnvironmentEditorPanel.currentPanel._updatePanelTitle();
            EnvironmentEditorPanel.currentPanel._sendEnvironmentData();
            return;
        }

        // Create a new panel
        const panel = vscode.window.createWebviewPanel(
            EnvironmentEditorPanel.viewType,
            `Edit Environment: ${environmentItem.name}`,
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, "webview-ui", "dist"),
                    extensionUri,
                ],
                retainContextWhenHidden: true,
            }
        );

        EnvironmentEditorPanel.currentPanel = new EnvironmentEditorPanel(
            panel,
            extensionUri,
            environmentItem,
            treeDataProvider
        );
    }

    private _updatePanelTitle() {
        this._panel.title = `Edit Environment: ${this._environmentItem.name}`;
    }

    private _sendEnvironmentData() {
        this._panel.webview.postMessage({
            command: "loadEnvironment",
            environment: {
                id: this._environmentItem.id,
                name: this._environmentItem.name || "",
                folderId: this._environmentItem.parentId,
                environmentVariables: this._environmentItem.environmentVariables || {},
            },
        });
    }

    private async _saveEnvironment(data: any): Promise<boolean> {
    // Validate required fields
        if (!data.name || data.name.trim() === "") {
            vscode.window.showErrorMessage("Environment name is required");
            return false;
        }

        // Preserve existing data and merge with new data
        this._environmentItem = {
            ...this._environmentItem,
            name: data.name.trim(),
            environmentVariables: data.environmentVariables || {},
            updatedAt: new Date(),
        };

        this._updatePanelTitle();

        try {
            await this._treeDataProvider.updateEnvironment(
                this._environmentItem.fullPath,
                this._environmentItem
            );
            vscode.window.showInformationMessage("Environment saved successfully!");
            return true;
        } catch (error) {
            const errorMessage =
        error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save environment: ${errorMessage}`);
            console.error("Save error:", error);
            return false;
        }
    }

    private _getHtmlForWebview(): string {
        return loadWebviewHtml(this._panel.webview, "environmentEditor");
    }

    public dispose() {
        EnvironmentEditorPanel.currentPanel = undefined;
        this._panel.dispose();

        while (this._disposables.length) {
            this._disposables.pop()?.dispose();
        }
    }
}
