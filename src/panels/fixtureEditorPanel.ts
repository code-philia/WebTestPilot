import * as vscode from "vscode";
import { FixtureItem } from "../models";
import { WebTestPilotTreeDataProvider } from "../treeDataProvider";
import { loadWebviewHtml } from "../utils/webviewLoader";

/**
 * FixtureEditorPanel provides a webview interface for editing fixture cases
 */
export class FixtureEditorPanel {
    public static currentPanel: FixtureEditorPanel | undefined;
    public static readonly viewType = "fixtureEditor";

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _fixtureItem: FixtureItem;
    private _treeDataProvider: WebTestPilotTreeDataProvider;

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        fixtureItem: FixtureItem,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._fixtureItem = fixtureItem;
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
                    this._sendFixtureData();
                    return;
                case "save":
                    await this._saveFixture(message.data);
                    return;
                case "updateFixture":
                    this._fixtureItem = { ...this._fixtureItem, ...message.data };
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
        fixtureItem: FixtureItem,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it and update the fixture
        if (FixtureEditorPanel.currentPanel) {
            FixtureEditorPanel.currentPanel._panel.reveal(column);
            FixtureEditorPanel.currentPanel._fixtureItem = fixtureItem;
            FixtureEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
            FixtureEditorPanel.currentPanel._updatePanelTitle();
            FixtureEditorPanel.currentPanel._sendFixtureData();
            return;
        }

        // Create a new panel
        const panel = vscode.window.createWebviewPanel(
            FixtureEditorPanel.viewType,
            `Edit Fixture: ${fixtureItem.name}`,
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

        FixtureEditorPanel.currentPanel = new FixtureEditorPanel(
            panel,
            extensionUri,
            fixtureItem,
            treeDataProvider
        );
    }

    private _updatePanelTitle() {
        this._panel.title = `Edit Fixture: ${this._fixtureItem.name}`;
    }

    private _sendFixtureData() {
        this._panel.webview.postMessage({
            command: "loadFixture",
            fixture: {
                id: this._fixtureItem.id,
                name: this._fixtureItem.name || "",
                folderId: this._fixtureItem.parentId,
                actions: this._fixtureItem.actions || [],
            },
        });
    }

    private async _saveFixture(data: any): Promise<boolean> {
    // Validate required fields
        if (!data.name || data.name.trim() === "") {
            vscode.window.showErrorMessage("Fixture name is required");
            return false;
        }

        // Preserve existing data and merge with new data
        this._fixtureItem = {
            ...this._fixtureItem,
            name: data.name.trim(),
            actions: Array.isArray(data.actions)
                ? data.actions
                : this._fixtureItem.actions || [],
            updatedAt: new Date(),
        };

        this._updatePanelTitle();

        try {
            await this._treeDataProvider.updateFixture(
                this._fixtureItem.fullPath,
                this._fixtureItem
            );
            vscode.window.showInformationMessage("Fixture saved successfully!");
            return true;
        } catch (error) {
            const errorMessage =
        error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save fixture: ${errorMessage}`);
            console.error("Save error:", error);
            return false;
        }
    }

    private _getHtmlForWebview(): string {
        return loadWebviewHtml(this._panel.webview, "fixtureEditor");
    }

    public dispose() {
        FixtureEditorPanel.currentPanel = undefined;
        this._panel.dispose();

        while (this._disposables.length) {
            this._disposables.pop()?.dispose();
        }
    }
}