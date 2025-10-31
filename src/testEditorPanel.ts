import * as vscode from "vscode";
import * as fs from "fs";
import { TestItem } from "./models";
import { WebTestPilotTreeDataProvider } from "./treeDataProvider";

/**
 * TestEditorPanel provides a webview interface for editing test cases
 */
export class TestEditorPanel {
  public static currentPanel: TestEditorPanel | undefined;
  public static readonly viewType = "testEditor";

  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];
  private _testItem: TestItem;
  private _treeDataProvider: WebTestPilotTreeDataProvider;

  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    testItem: TestItem,
    treeDataProvider: WebTestPilotTreeDataProvider
  ) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._testItem = testItem;
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
            this._sendTestData();
            return;
          case "save":
            await this._saveTest(message.data);
            return;
          case "saveAndRun":
            if (await this._saveTest(message.data)) {
              this._runTest();
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
    treeDataProvider: WebTestPilotTreeDataProvider
  ) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it and update the test
    if (TestEditorPanel.currentPanel) {
      TestEditorPanel.currentPanel._panel.reveal(column);
      TestEditorPanel.currentPanel._testItem = testItem;
      TestEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
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
      extensionUri,
      testItem,
      treeDataProvider
    );
  }

  private _updatePanelTitle() {
    this._panel.title = `Edit Test: ${this._testItem.name}`;
  }

  private _sendTestData() {
    this._panel.webview.postMessage({
      command: "loadTest",
      test: {
        id: this._testItem.id,
        name: this._testItem.name || "",
        url: this._testItem.url || "",
        folderId: this._testItem.folderId,
        actions: this._testItem.actions || [],
      },
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
      actions: Array.isArray(data.actions)
        ? data.actions
        : this._testItem.actions || [],
      updatedAt: new Date(),
    };

    this._updatePanelTitle();

    try {
      await this._treeDataProvider.updateTest(
        this._testItem.id,
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
    const webview = this._panel.webview;
    const distUri = vscode.Uri.joinPath(
      this._extensionUri,
      "webview-ui",
      "dist"
    );
    const indexHtmlUri = vscode.Uri.joinPath(distUri, "index.html");

    // Load the built index.html
    let html = fs.readFileSync(indexHtmlUri.fsPath, "utf-8");

    // Generate a nonce for CSP and script tags
    const nonce = this._getNonce();

    // Build the CSP meta tag using the webview's cspSource and the nonce
    const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${webview.cspSource} https: data:; style-src ${webview.cspSource} 'unsafe-inline'; font-src ${webview.cspSource}; script-src 'nonce-${nonce}'; connect-src ${webview.cspSource} https:;">`;

    // Insert the CSP meta tag before the closing head tag
    html = html.replace("</head>", `${cspMeta}</head>`);

    // Inject page identifier script with nonce
    const pageScript = `<script nonce="${nonce}">window.__PAGE__ = 'testEditor';</script>`;

    // Insert the page script before the closing body tag
    html = html.replace("</body>", `${pageScript}</body>`);

    // Add nonce attribute to all script tags so bundled scripts are allowed by the CSP
    html = html.replace(/<script(\s)/g, `<script nonce="${nonce}"$1`);

    html = this._rewriteResourceUrls(html, distUri, webview, nonce);
    return html;
  }

  private _rewriteResourceUrls(
    html: string,
    distUri: vscode.Uri,
    webview: vscode.Webview,
    nonce: string
  ): string {
    const scriptPattern = /<script([^>]*)src="([^"]+)"([^>]*)><\/script>/gi;
    html = html.replace(scriptPattern, (match, preAttrs, src, postAttrs) => {
      if (this._isExternalResource(src)) {
        return match;
      }

      const resolvedSrc = this._resolveWebviewUri(webview, distUri, src);
      let rebuilt = `<script${preAttrs || ""} src="${resolvedSrc}"${
        postAttrs || ""
      }></script>`;
      if (/nonce\s*=/.test(rebuilt)) {
        rebuilt = rebuilt.replace(/nonce\s*=\s*"[^"]*"/i, `nonce="${nonce}"`);
      } else {
        rebuilt = rebuilt.replace("<script", `<script nonce="${nonce}"`);
      }
      return rebuilt;
    });

    const linkPattern = /<link([^>]*)href="([^"]+)"([^>]*)>/gi;
    html = html.replace(linkPattern, (match, preAttrs, href, postAttrs) => {
      if (this._isExternalResource(href)) {
        return match;
      }

      const resolvedHref = this._resolveWebviewUri(webview, distUri, href);
      return `<link${preAttrs || ""}href="${resolvedHref}"${postAttrs || ""}>`;
    });

    return html;
  }

  private _isExternalResource(resourcePath: string): boolean {
    return (
      /^(https?:)?\/\//i.test(resourcePath) ||
      resourcePath.startsWith("vscode-resource:") ||
      resourcePath.startsWith("vscode-webview-resource:") ||
      resourcePath.startsWith("data:")
    );
  }

  private _resolveWebviewUri(
    webview: vscode.Webview,
    baseUri: vscode.Uri,
    resourcePath: string
  ): string {
    const cleanedPath = resourcePath.trim();
    const [pathWithoutHash, hashFragment] = cleanedPath.split("#", 2);
    const [pathPart, queryString] = pathWithoutHash.split("?", 2);

    const normalizedSegments = pathPart
      .replace(/^\//, "")
      .split("/")
      .filter((segment) => segment.length > 0);

    const resourceUri = vscode.Uri.joinPath(baseUri, ...normalizedSegments);
    let webviewUri = webview.asWebviewUri(resourceUri).toString();

    if (queryString) {
      webviewUri += `?${queryString}`;
    }

    if (hashFragment) {
      webviewUri += `#${hashFragment}`;
    }

    return webviewUri;
  }

  private _runTest() {
    if (!this._testItem.actions || this._testItem.actions.length === 0) {
      vscode.window.showWarningMessage("Cannot run test: No actions defined.");
      return;
    }
    vscode.commands.executeCommand("webtestpilot.runTest", this._testItem);
  }

  // Add nonce helper
  private _getNonce(): string {
    const possible =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let text = "";
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }

  public dispose() {
    TestEditorPanel.currentPanel = undefined;
    this._panel.dispose();

    while (this._disposables.length) {
      this._disposables.pop()?.dispose();
    }
  }
}
