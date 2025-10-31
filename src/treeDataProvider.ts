import * as vscode from 'vscode';
import { TestItem, FolderItem, FixtureItem, TreeItem as WebTestPilotDataItem } from './models';
import { FileSystemService } from './fileSystemService';

export class WebTestPilotTreeItem extends vscode.TreeItem {
    constructor(
        public readonly item: WebTestPilotDataItem,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly command?: vscode.Command
    ) {
        super(item.name, collapsibleState);
        
        this.tooltip = this.getTooltip();
        this.description = this.getDescription();
        this.contextValue = item.type;
        this.iconPath = this.getIconPath();
    }

    private getTooltip(): string {
        if (this.item.type === 'test') {
            const test = this.item as TestItem;
            const actionCount = test.actions ? test.actions.length : 0;
            return `${test.name}\n${test.url || 'No URL'}\n${actionCount} action(s)`;
        }
        if (this.item.type === 'fixture') {
            const fixture = this.item as FixtureItem;
            const actionCount = fixture.actions ? fixture.actions.length : 0;
            const baseInfo = fixture.baseFixtureId ? `\nBase: ${fixture.baseFixtureId}` : '';
            return `${fixture.name}\n${actionCount} action(s)${baseInfo}`;
        }
        return this.item.name;
    }

    private getDescription(): string {
        if (this.item.type === 'test') {
            const test = this.item as TestItem;
            const actionCount = test.actions ? test.actions.length : 0;
            return `${actionCount} action(s) • ${test.url || 'No URL'}`;
        }
        if (this.item.type === 'fixture') {
            const fixture = this.item as FixtureItem;
            const actionCount = fixture.actions ? fixture.actions.length : 0;
            const baseInfo = fixture.baseFixtureId ? ` • Base: ${fixture.baseFixtureId.replace(/\.json$/, '')}` : '';
            return `${actionCount} action(s)${baseInfo}`;
        }
        return '';
    }

    private getIconPath(): vscode.ThemeIcon | vscode.Uri {
        if (this.item.type === 'test') {
            return new vscode.ThemeIcon('debug-start');
        }
        if (this.item.type === 'fixture') {
            return new vscode.ThemeIcon('tools');
        }
        return new vscode.ThemeIcon('folder');
    }
}

export class WebTestPilotTreeDataProvider implements vscode.TreeDataProvider<WebTestPilotTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<WebTestPilotTreeItem | undefined | null | void> = new vscode.EventEmitter<WebTestPilotTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<WebTestPilotTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private items: WebTestPilotDataItem[] = [];
    private fileSystemService: FileSystemService;

    constructor(private context: vscode.ExtensionContext) {
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            throw new Error('No workspace folder found');
        }
        
        this.fileSystemService = new FileSystemService(workspaceRoot);
        this.initialize();
    }

    private async initialize(): Promise<void> {
        try {
            await this.fileSystemService.initialize();
            await this.loadFromFileSystem();
            
            // Start watching for file changes
            this.fileSystemService.startWatching(() => {
                this.loadFromFileSystem();
            });
        } catch (error) {
            console.error('Failed to initialize TreeDataProvider:', error);
            vscode.window.showErrorMessage(`Failed to initialize WebTestPilot: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    private async loadFromFileSystem(): Promise<void> {
        try {
            this.items = await this.fileSystemService.readStructure();
            this._onDidChangeTreeData.fire();
        } catch (error) {
            console.error('Error loading from file system:', error);
        }
    }

    refresh(): void {
        this.loadFromFileSystem();
    }

    getTreeItem(element: WebTestPilotTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: WebTestPilotTreeItem): Thenable<WebTestPilotTreeItem[]> {
        if (!element) {
            // Root level - show folders, root-level tests, and fixtures
            const rootFolders = this.items.filter(item => 
                item.type === 'folder' && !item.parentId
            ) as FolderItem[];
            const rootTests = this.items.filter(item => 
                item.type === 'test' && !item.folderId
            ) as TestItem[];
            const fixtures = this.items.filter(item => 
                item.type === 'fixture'
            ) as FixtureItem[];
            
            return Promise.resolve([
                ...rootFolders.map(folder => new WebTestPilotTreeItem(folder, vscode.TreeItemCollapsibleState.Collapsed)),
                ...rootTests.map(test => new WebTestPilotTreeItem(test, vscode.TreeItemCollapsibleState.None, {
                    command: 'webtestpilot.openTest',
                    title: 'Open Test',
                    arguments: [test]
                })),
                ...fixtures.map(fixture => new WebTestPilotTreeItem(fixture, vscode.TreeItemCollapsibleState.None, {
                    command: 'webtestpilot.openFixtureEditor',
                    title: 'Open Fixture',
                    arguments: [fixture]
                }))
            ]);
        }

        if (element.item.type === 'folder') {
            const folder = element.item as FolderItem;
            const childFolders = this.items.filter(item => 
                item.type === 'folder' && item.parentId === folder.id
            ) as FolderItem[];
            const childTests = this.items.filter(item => 
                item.type === 'test' && item.folderId === folder.id
            ) as TestItem[];
            
            return Promise.resolve([
                ...childFolders.map(childFolder => new WebTestPilotTreeItem(childFolder, vscode.TreeItemCollapsibleState.Collapsed)),
                ...childTests.map(test => new WebTestPilotTreeItem(test, vscode.TreeItemCollapsibleState.None, {
                    command: 'webtestpilot.openTest',
                    title: 'Open Test',
                    arguments: [test]
                }))
            ]);
        }

        return Promise.resolve([]);
    }

    async createTest(name: string, folderId?: string): Promise<TestItem> {
        const folderPath = folderId;
        const testItem = await this.fileSystemService.createTest(name, folderPath);
        await this.loadFromFileSystem();
        return testItem;
    }

    async createFolder(name: string, parentId?: string): Promise<FolderItem> {
        const parentPath = parentId;
        const folderItem = await this.fileSystemService.createFolder(name, parentPath);
        await this.loadFromFileSystem();
        return folderItem;
    }

    async deleteItem(item: WebTestPilotDataItem): Promise<void> {
        if (item.type === 'test') {
            await this.fileSystemService.deleteTest(item.id);
        } else if (item.type === 'fixture') {
            await this.fileSystemService.deleteFixture(item.id);
        } else {
            await this.fileSystemService.deleteFolder(item.id);
        }
        await this.loadFromFileSystem();
    }

    async updateTest(testPath: string, testItem: TestItem): Promise<void> {
        try {
            await this.fileSystemService.updateTest(testPath, testItem);
            await this.loadFromFileSystem();
        } catch (error) {
            console.error('TreeDataProvider.updateTest failed:', error);
            throw error;
        }
    }

    async createFixture(name: string, baseFixtureId?: string): Promise<FixtureItem> {
        const fixtureItem = await this.fileSystemService.createFixture(name, baseFixtureId);
        await this.loadFromFileSystem();
        return fixtureItem;
    }

    async updateFixture(fixtureId: string, fixtureItem: FixtureItem): Promise<void> {
        try {
            await this.fileSystemService.updateFixture(fixtureId, fixtureItem);
            await this.loadFromFileSystem();
        } catch (error) {
            console.error('TreeDataProvider.updateFixture failed:', error);
            throw error;
        }
    }

    async deleteFixture(fixtureId: string): Promise<void> {
        await this.fileSystemService.deleteFixture(fixtureId);
        await this.loadFromFileSystem();
    }

    getStructure(): WebTestPilotDataItem[] {
        return this.items;
    }

    getChildrenTests(folderId?: string): TestItem[] {
        if (!folderId) {
            // Root level tests
            return this.items.filter(item => 
                item.type === 'test' && !item.folderId
            ) as TestItem[];
        }

        // Tests in specific folder
        const directTests = this.items.filter(item => 
            item.type === 'test' && item.folderId === folderId
        ) as TestItem[];

        // Get tests from subfolders recursively
        const subfolders = this.items.filter(item => 
            item.type === 'folder' && item.parentId === folderId
        ) as FolderItem[];

        const subfolderTests: TestItem[] = [];
        subfolders.forEach(subfolder => {
            subfolderTests.push(...this.getChildrenTests(subfolder.id));
        });

        return [...directTests, ...subfolderTests];
    }

    dispose(): void {
        this.fileSystemService.dispose();
    }
}