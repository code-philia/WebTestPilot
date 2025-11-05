import * as vscode from "vscode";
import { TestItem, FixtureItem } from "../models";
import { WebTestPilotTreeDataProvider } from "../treeDataProvider";
import { loadWebviewHtml } from "../utils/webviewLoader";
import { TestRunnerPanel } from "./testRunnerPanel";

/**
 * TestEditorPanel provides a webview interface for editing test cases
 */
export class TestEditorPanel {
    public static currentPanel: TestEditorPanel | undefined;
    public static readonly viewType = "testEditor";

    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _testItem: TestItem;
    private _treeDataProvider: WebTestPilotTreeDataProvider;
    private _fixtureTreeDataProvider: WebTestPilotTreeDataProvider;

    private constructor(
        panel: vscode.WebviewPanel,
        testItem: TestItem,
        treeDataProvider: WebTestPilotTreeDataProvider,
        fixtureTreeDataProvider: WebTestPilotTreeDataProvider
    ) {
        this._panel = panel;
        this._testItem = testItem;
        this._treeDataProvider = treeDataProvider;
        this._fixtureTreeDataProvider = fixtureTreeDataProvider;

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
                    this._sendTestData();
                    return;
                case "save":
                    await this._saveTest(message.data);
                    return;
                case "saveAndRun":
                    if (await this._saveTest(message.data)) {
                        await this._runTest();
                    }
                    return;
                case "updateTest":
                    this._testItem = { ...this._testItem, ...message.data };
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
        testItem: TestItem,
        treeDataProvider: WebTestPilotTreeDataProvider,
        fixtureTreeDataProvider: WebTestPilotTreeDataProvider
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it and update the test
        if (TestEditorPanel.currentPanel) {
            TestEditorPanel.currentPanel._panel.reveal(column);
            TestEditorPanel.currentPanel._testItem = testItem;
            TestEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
            TestEditorPanel.currentPanel._fixtureTreeDataProvider = fixtureTreeDataProvider;
            TestEditorPanel.currentPanel._updatePanelTitle();
            TestEditorPanel.currentPanel._sendTestData();
            return;
        }

        // Create a new panel
        const panel = vscode.window.createWebviewPanel(
            TestEditorPanel.viewType,
            `Edit Test: ${testItem.name}`,
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

        TestEditorPanel.currentPanel = new TestEditorPanel(
            panel,
            testItem,
            treeDataProvider,
            fixtureTreeDataProvider
        );
    }

    private _updatePanelTitle() {
        this._panel.title = `Edit Test: ${this._testItem.name}`;
    }

    private _sendTestData() {
        // Get all fixtures for dropdown
        const fixtures = this._fixtureTreeDataProvider.getStructure().filter(item => item.type === 'fixture') as FixtureItem[];
        
        this._panel.webview.postMessage({
            command: "loadTest",
            test: {
                id: this._testItem.id,
                name: this._testItem.name || "",
                url: this._testItem.url || "",
                folderId: this._testItem.parentId,
                fixtureId: this._testItem.fixtureId,
                actions: this._testItem.actions || [],
            },
            fixtures: fixtures.map(fixture => ({
                id: fixture.id,
                name: fixture.name,
                parentId: fixture.parentId,
                actions: fixture.actions || []
            })),
        });
    }

    private async _saveTest(data: any): Promise<boolean> {
    // Validate required fields
        if (!data.name || data.name.trim() === "") {
            vscode.window.showErrorMessage("Test name is required");
            return false;
        }

        // Preserve existing data and merge with new data
        this._testItem = {
            ...this._testItem,
            name: data.name.trim(),
            url: data.url ? data.url.trim() : "",
            fixtureId: data.fixtureId,
            actions: Array.isArray(data.actions)
                ? data.actions
                : this._testItem.actions || [],
            updatedAt: new Date(),
        };

        this._updatePanelTitle();

        try {
            await this._treeDataProvider.updateTest(
                this._testItem.fullPath,
                this._testItem
            );
            vscode.window.showInformationMessage("Test saved successfully!");
            return true;
        } catch (error) {
            const errorMessage =
        error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save test: ${errorMessage}`);
            console.error("Save error:", error);
            return false;
        }
    }

    private _getHtmlForWebview(): string {
        return loadWebviewHtml(this._panel.webview, "testEditor");
    }

    private async _runTest() {
        if (!this._testItem.actions || this._testItem.actions.length === 0) {
            vscode.window.showWarningMessage("Cannot run test: No actions defined.");
            return;
        }
        await TestRunnerPanel.createOrShow(this._testItem);
    }

    public dispose() {
        TestEditorPanel.currentPanel = undefined;
        this._panel.dispose();

        while (this._disposables.length) {
            this._disposables.pop()?.dispose();
        }
    }
}
