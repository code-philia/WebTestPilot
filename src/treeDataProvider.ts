import * as vscode from 'vscode';
import { TestItem, FolderItem, TreeItem as WebTestPilotDataItem, MenuItem, FixtureItem, EnvironmentItem, POSSIBLE_MENUS, POSSIBLE_MENU_IDS } from './models';
import { FileSystemService } from './services/fileSystemService';

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
        switch(this.item.type) {
        case 'menu' :
        case 'folder' :
            return  `${this.item.name}`;
        case 'test':
            const test = this.item as TestItem;
            const actionCount = test.actions ? test.actions.length : 0;
            return `${test.name}\n${test.url || 'No URL'}\n${actionCount} action(s)`;
        case 'fixture':
            const fixture = this.item as FixtureItem;
            const fixtureActionCount = fixture.actions ? fixture.actions.length : 0;
            return `${fixture.name}\n${fixtureActionCount} action(s)`;
        case 'environment':
            const environment = this.item as EnvironmentItem;
            const varCount = Object.keys(environment.environmentVariables || {}).length;
            return `${environment.name}\n${varCount} variable(s)`;
        }
    }

    private getDescription(): string {
        switch (this.item.type) {
        case 'menu':
        case 'folder':
            return '';
        case 'test':
            const test = this.item as TestItem;
            const actionCount = test.actions ? test.actions.length : 0;
            return `${actionCount} action(s) • ${test.url || 'No URL'}`;
        case 'fixture':
            const fixture = this.item as FixtureItem;
            const fixtureActionCount = fixture.actions ? fixture.actions.length : 0;
            return `${fixtureActionCount} action(s)`;
        case 'environment':
            const environment = this.item as EnvironmentItem;
            const varCount = Object.keys(environment.environmentVariables || {}).length;
            return `${varCount} variable(s)`;
        default:
            return '';
        }
    }

    private getIconPath(): vscode.ThemeIcon | vscode.Uri {
        switch (this.item.type) {
        case 'folder':
            return new vscode.ThemeIcon('folder');
        case 'test':
            return new vscode.ThemeIcon('beaker');
        case 'fixture':
            return new vscode.ThemeIcon('tools');
        case 'environment':
            return new vscode.ThemeIcon('settings-gear');
        case 'menu':
            const menuItem = this.item as MenuItem;
            return new vscode.ThemeIcon(menuItem.icon);
        default:
            return new vscode.ThemeIcon('file');
        }
    }
}

export class WebTestPilotTreeDataProvider implements vscode.TreeDataProvider<WebTestPilotTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<WebTestPilotTreeItem | undefined | null | void> = new vscode.EventEmitter<WebTestPilotTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<WebTestPilotTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private items: WebTestPilotDataItem[] = [];
    private fileSystemService: FileSystemService;
    private loadType: POSSIBLE_MENUS;

    constructor(private context: vscode.ExtensionContext, loadType: POSSIBLE_MENUS) {
        this.loadType = loadType;
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            throw new Error('No workspace folder found');
        }

        this.fileSystemService = new FileSystemService(workspaceRoot, this.loadType);
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
        // Root level - show 3 items; test cases, fixtures, environments
        console.log(this.items);
        if (!element) {
            const rootFolders = this.items.filter(item => 
                POSSIBLE_MENU_IDS.includes(item.parentId!) && item.type === 'folder'
            ) as FolderItem[];
            const rootItems = this.items.filter(item =>
                POSSIBLE_MENU_IDS.includes(item.parentId!) && item.type === this.loadType
            );

            return Promise.resolve([
                ...rootFolders.map(
                    folder => new WebTestPilotTreeItem(folder, vscode.TreeItemCollapsibleState.Collapsed)
                ),
                ...rootItems.map(item => {
                    const command = this.loadType === 'test' ? 'webtestpilot.openTest' : 
                        this.loadType === 'fixture' ? 'webtestpilot.openFixture' :
                            this.loadType === 'environment' ? 'webtestpilot.openEnvironment' : undefined;
                    return new WebTestPilotTreeItem(item, vscode.TreeItemCollapsibleState.None, command ? {
                        command,
                        title: `Open ${this.loadType}`,
                        arguments: [item]
                    } : undefined);
                })
            ]);
        }
        
        if (!element || element.item.type === 'folder' || element.item.type === 'menu') {
            const parent = element.item as FolderItem | MenuItem;
            const childFolders = this.items.filter(item => 
                item.type === 'folder' && item.parentId === parent.id
            ) as FolderItem[];
            const childItems = this.items.filter(item => 
                item.type === this.loadType && item.parentId === parent.id
            );
            console.log(parent.id, childFolders, childItems);
            
            return Promise.resolve([
                ...childFolders.map(childFolder => new WebTestPilotTreeItem(childFolder, vscode.TreeItemCollapsibleState.Collapsed)),
                ...childItems.map(item => {
                    const command = this.loadType === 'test' ? 'webtestpilot.openTest' : 
                        this.loadType === 'fixture' ? 'webtestpilot.openFixture' :
                            this.loadType === 'environment' ? 'webtestpilot.openEnvironment' : undefined;
                    return new WebTestPilotTreeItem(item, vscode.TreeItemCollapsibleState.None, command ? {
                        command,
                        title: `Open ${this.loadType}`,
                        arguments: [item]
                    } : undefined);
                })
            ]);
        }

        return Promise.resolve([]);
    }

    async createFolder(name: string, parentId?: string): Promise<FolderItem> {
        const parentPath = parentId;
        const folderItem = await this.fileSystemService.createFolder(name, parentPath);
        await this.loadFromFileSystem();
        return folderItem;
    }

    async deleteItem(item: WebTestPilotDataItem): Promise<void> {
        if (item.type === 'test' || item.type === 'fixture' || item.type === 'environment') {
            await this.fileSystemService.deleteTest(item.id);
        } else {
            await this.fileSystemService.deleteFolder(item.id);
        }
        await this.loadFromFileSystem();
    }

    async createTest(name: string, folderId?: string): Promise<TestItem> {
        const folderPath = folderId;
        const testItem = await this.fileSystemService.createTest(name, folderPath);
        await this.loadFromFileSystem();
        return testItem;
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

    async updateFixture(fixturePath: string, fixtureItem: FixtureItem): Promise<void> {
        try {
            await this.fileSystemService.updateFixture(fixturePath, fixtureItem);
            await this.loadFromFileSystem();
        } catch (error) {
            console.error('TreeDataProvider.updateFixture failed:', error);
            throw error;
        }
    }

    async createFixture(name: string, folderId?: string): Promise<FixtureItem> {
        const folderPath = folderId;
        const fixtureItem = await this.fileSystemService.createFixture(name, folderPath);
        await this.loadFromFileSystem();
        return fixtureItem;
    }

    async createEnvironment(name: string, folderId?: string): Promise<EnvironmentItem> {
        const folderPath = folderId;
        const environmentItem = await this.fileSystemService.createEnvironment(name, folderPath);
        await this.loadFromFileSystem();
        return environmentItem;
    }

    async updateEnvironment(environmentPath: string, environmentItem: EnvironmentItem): Promise<void> {
        try {
            await this.fileSystemService.updateEnvironment(environmentPath, environmentItem);
            await this.loadFromFileSystem();
        } catch (error) {
            console.error('TreeDataProvider.updateEnvironment failed:', error);
            throw error;
        }
    }

    getStructure(): WebTestPilotDataItem[] {
        return this.items;
    }

    getChildrenTests(parentId: string): TestItem[] {
        // Tests in specific folder
        const directTests = this.items.filter(item =>
            item.type === 'test' && item.parentId === parentId
        ) as TestItem[];

        // Get tests from subfolders recursively
        const subfolders = this.items.filter(item =>
            item.type === 'folder' && item.parentId === parentId
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