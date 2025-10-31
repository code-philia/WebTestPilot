import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { TestItem, FixtureItem } from './models';
import { WebTestPilotTreeDataProvider } from './treeDataProvider';

/**
 * FixtureEditorPanel provides a tabbed webview interface for editing test cases and fixtures
 */
export class FixtureEditorPanel {
    public static currentPanel: FixtureEditorPanel | undefined;
    public static readonly viewType = 'fixtureEditor';

    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private _treeDataProvider: WebTestPilotTreeDataProvider;
    private _currentTestItem: TestItem | undefined;
    private _currentFixtureItem: FixtureItem | undefined;
    private _allFixtures: FixtureItem[] = [];

    private constructor(
        panel: vscode.WebviewPanel,
        treeDataProvider: WebTestPilotTreeDataProvider
    ) {
        this._panel = panel;
        this._treeDataProvider = treeDataProvider;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'saveTest':
                        this._saveTest(message.data);
                        return;
                    case 'saveFixture':
                        this._saveFixture(message.data);
                        return;
                    case 'createFixture':
                        this._createFixture(message.data);
                        return;
                    case 'deleteFixture':
                        this._deleteFixture(message.data);
                        return;
                    case 'loadFixture':
                        this._loadFixture(message.data);
                        return;
                    case 'updateTest':
                        if (this._currentTestItem) {
                            this._currentTestItem = { ...this._currentTestItem, ...message.data };
                            this._updatePanelTitle();
                        }
                        return;
                    case 'updateFixture':
                        if (this._currentFixtureItem) {
                            this._currentFixtureItem = { ...this._currentFixtureItem, ...message.data };
                            this._updatePanelTitle();
                        }
                        return;
                    case 'runTest':
                        if (this._currentTestItem) {
                            if (!this._currentTestItem.actions || this._currentTestItem.actions.length === 0) {
                                vscode.window.showWarningMessage('Cannot run test: No actions defined. Please add test actions before running.');
                                return;
                            }
                            vscode.commands.executeCommand('webtestpilot.runTest', this._currentTestItem);
                        }
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

    public static async createOrShow(
        extensionUri: vscode.Uri,
        treeDataProvider: WebTestPilotTreeDataProvider,
        testItem?: TestItem
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (FixtureEditorPanel.currentPanel) {
            FixtureEditorPanel.currentPanel._panel.reveal(column);
            FixtureEditorPanel.currentPanel._treeDataProvider = treeDataProvider;
            
            if (testItem) {
                FixtureEditorPanel.currentPanel._currentTestItem = testItem;
                FixtureEditorPanel.currentPanel._updatePanelTitle();
                FixtureEditorPanel.currentPanel._update();
            }
            return;
        }

        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel(
            FixtureEditorPanel.viewType,
            'WebTestPilot Editor',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            }
        );

        const editorPanel = new FixtureEditorPanel(panel, treeDataProvider);
        
        if (testItem) {
            editorPanel._currentTestItem = testItem;
            editorPanel._updatePanelTitle();
        }
        
        editorPanel._update();
        FixtureEditorPanel.currentPanel = editorPanel;
    }

    private _updatePanelTitle() {
        if (this._currentTestItem) {
            this._panel.title = `Edit Test: ${this._currentTestItem.name}`;
        } else if (this._currentFixtureItem) {
            this._panel.title = `Edit Fixture: ${this._currentFixtureItem.name}`;
        } else {
            this._panel.title = 'WebTestPilot Editor';
        }
    }

    private async _update() {
        // Load all fixtures for dropdowns
        await this._loadAllFixtures();
        
        this._updatePanelTitle();
        const html = await this._getHtmlForWebview();
        this._panel.webview.html = html;
    }

    private async _loadAllFixtures() {
        try {
            const structure = await this._treeDataProvider.getStructure();
            this._allFixtures = structure.filter(item => item.type === 'fixture') as FixtureItem[];
        } catch (error) {
            console.error('Failed to load fixtures:', error);
            this._allFixtures = [];
        }
    }

    private async _saveTest(data: any) {
        if (!this._currentTestItem) {
            vscode.window.showErrorMessage('No test selected');
            return;
        }

        if (!data.name || data.name.trim() === '') {
            vscode.window.showErrorMessage('Test name is required');
            return;
        }

        this._currentTestItem = {
            ...this._currentTestItem,
            name: data.name.trim(),
            url: data.url ? data.url.trim() : '',
            actions: Array.isArray(data.actions) ? data.actions : (this._currentTestItem.actions || []),
            updatedAt: new Date()
        };
        
        this._updatePanelTitle();
        
        try {
            await this._treeDataProvider.updateTest(this._currentTestItem.id, this._currentTestItem);
            vscode.window.showInformationMessage('Test saved successfully!');
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save test: ${errorMessage}`);
        }
    }

    private async _saveFixture(data: any) {
        if (!this._currentFixtureItem) {
            vscode.window.showErrorMessage('No fixture selected');
            return;
        }

        if (!data.name || data.name.trim() === '') {
            vscode.window.showErrorMessage('Fixture name is required');
            return;
        }

        this._currentFixtureItem = {
            ...this._currentFixtureItem,
            name: data.name.trim(),
            actions: Array.isArray(data.actions) ? data.actions : (this._currentFixtureItem.actions || []),
            baseFixtureId: data.baseFixtureId || undefined,
            updatedAt: new Date()
        };
        
        this._updatePanelTitle();
        
        try {
            await this._treeDataProvider.updateFixture(this._currentFixtureItem.id, this._currentFixtureItem);
            await this._loadAllFixtures(); // Reload fixtures for dropdowns
            vscode.window.showInformationMessage('Fixture saved successfully!');
            this._update(); // Refresh the UI
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to save fixture: ${errorMessage}`);
        }
    }

    private async _createFixture(data: any) {
        if (!data.name || data.name.trim() === '') {
            vscode.window.showErrorMessage('Fixture name is required');
            return;
        }

        try {
            const fixture = await this._treeDataProvider.createFixture(data.name.trim(), data.baseFixtureId);
            this._currentFixtureItem = fixture;
            await this._loadAllFixtures();
            this._updatePanelTitle();
            this._update();
            vscode.window.showInformationMessage(`Fixture "${fixture.name}" created successfully!`);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Failed to create fixture: ${errorMessage}`);
        }
    }

    private async _deleteFixture(fixtureId: string) {
        const result = await vscode.window.showWarningMessage(
            'Are you sure you want to delete this fixture?',
            { modal: true },
            'Delete',
            'Cancel'
        );

        if (result === 'Delete') {
            try {
                await this._treeDataProvider.deleteFixture(fixtureId);
                if (this._currentFixtureItem?.id === fixtureId) {
                    this._currentFixtureItem = undefined;
                }
                await this._loadAllFixtures();
                this._updatePanelTitle();
                this._update();
                vscode.window.showInformationMessage('Fixture deleted successfully!');
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                vscode.window.showErrorMessage(`Failed to delete fixture: ${errorMessage}`);
            }
        }
    }

    private async _loadFixture(fixtureId: string) {
        try {
            const structure = await this._treeDataProvider.getStructure();
            const fixture = structure.find(item => item.id === fixtureId && item.type === 'fixture') as FixtureItem;
            
            if (fixture) {
                this._currentFixtureItem = fixture;
                this._updatePanelTitle();
                this._update();
            }
        } catch (error) {
            vscode.window.showErrorMessage('Failed to load fixture');
        }
    }

    private async _getHtmlForWebview(): Promise<string> {
        const testItem = this._currentTestItem;
        const fixtureItem = this._currentFixtureItem;
        const testActions = testItem?.actions || [];
        const fixtureActions = fixtureItem?.actions || [];
        
        // Read HTML template from file
        const htmlPath = path.join(__dirname, 'views', 'fixture-editor.html');
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

        // Generate fixture options for dropdowns
        const fixtureOptions = this._allFixtures.map(fixture => 
            `<option value="${fixture.id}" ${fixtureItem?.id === fixture.id ? 'selected' : ''}>${escapeHtml(fixture.name)}</option>`
        ).join('');

        const baseFixtureOptions = this._allFixtures
            .filter(fixture => fixture.id !== fixtureItem?.id)
            .map(fixture => 
                `<option value="${fixture.id}" ${fixtureItem?.baseFixtureId === fixture.id ? 'selected' : ''}>${escapeHtml(fixture.name)}</option>`
            ).join('');

        // Replace placeholders in template
        htmlTemplate = htmlTemplate
            .replace(/\{\{TEST_NAME\}\}/g, escapeHtml(testItem?.name || ''))
            .replace(/\{\{TEST_NAME_VALUE\}\}/g, escapeHtml(testItem?.name || ''))
            .replace(/\{\{TEST_URL_VALUE\}\}/g, escapeHtml(testItem?.url || ''))
            .replace(/\{\{FIXTURE_NAME\}\}/g, escapeHtml(fixtureItem?.name || ''))
            .replace(/\{\{FIXTURE_NAME_VALUE\}\}/g, escapeHtml(fixtureItem?.name || ''))
            .replace(/\{\{FIXTURE_OPTIONS\}\}/g, fixtureOptions)
            .replace(/\{\{BASE_FIXTURE_OPTIONS\}\}/g, baseFixtureOptions)
            .replace(/\{\{TEST_ACTIONS_LIST\}\}/g, testActions.map((action, index) => `
                <div class="action-item compact" data-index="${index}">
                    <div class="action-row">
                        <span class="action-number">${index + 1}.</span>
                        <input type="text" class="action-text compact" placeholder="Action" value="${escapeHtml(action.action || '')}" />
                        <button class="btn btn-danger compact" onclick="removeTestAction(${index})">×</button>
                    </div>
                    <div class="action-row">
                        <span class="action-number">→</span>
                        <input type="text" class="expected-result compact" placeholder="Expected result" value="${escapeHtml(action.expectedResult || '')}" />
                    </div>
                </div>
            `).join(''))
            .replace(/\{\{FIXTURE_ACTIONS_LIST\}\}/g, fixtureActions.map((action, index) => `
                <div class="action-item compact" data-index="${index}">
                    <div class="action-row">
                        <span class="action-number">${index + 1}.</span>
                        <input type="text" class="action-text compact" placeholder="Action" value="${escapeHtml(action.action || '')}" />
                        <button class="btn btn-danger compact" onclick="removeFixtureAction(${index})">×</button>
                    </div>
                    <div class="action-row">
                        <span class="action-number">→</span>
                        <input type="text" class="expected-result compact" placeholder="Expected result" value="${escapeHtml(action.expectedResult || '')}" />
                    </div>
                </div>
            `).join(''));

        // Add JSON data scripts
        const testJsonScript = `<script type="application/json" id="testActionsJson">${JSON.stringify(testActions)}</script>`;
        const fixtureJsonScript = `<script type="application/json" id="fixtureActionsJson">${JSON.stringify(fixtureActions)}</script>`;
        htmlTemplate = htmlTemplate.replace('</body>', `${testJsonScript}${fixtureJsonScript}</body>`);

        return htmlTemplate;
    }

    public dispose() {
        FixtureEditorPanel.currentPanel = undefined;
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}