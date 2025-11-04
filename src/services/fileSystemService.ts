import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { TestItem, FolderItem, TreeItem as WebTestPilotDataItem, MenuItem, EnvironmentItem, FixtureItem, FIXTURE_MENU_ID, ENV_MENU_ID, TEST_MENU_ID, POSSIBLE_MENUS } from '../models';


export class FileSystemService {
    private webTestPilotDir: string;
    private fixturesDir: string;
    private envDir: string;
    private testsDir: string;
    private fileWatcher: vscode.FileSystemWatcher | undefined;
    private readonly loadType: POSSIBLE_MENUS;

    constructor(private workspaceRoot: string, loadType: POSSIBLE_MENUS) {
        this.loadType = loadType;
        this.webTestPilotDir = path.join(workspaceRoot, '.webtestpilot');
        this.testsDir = path.join(this.webTestPilotDir, '.tests');
        this.fixturesDir = path.join(this.webTestPilotDir, '.fixtures');
        this.envDir = path.join(this.webTestPilotDir, '.environments');
    }

    async initialize(): Promise<void> {
        const dirs = [
            this.webTestPilotDir,
            this.testsDir,
            this.fixturesDir,
            this.envDir
        ];

        for (const dir of dirs) {
            try {
                await fs.access(dir);
            }
            catch {
                await fs.mkdir(dir, { recursive: true });
            }
        }
    }

    async readStructure(): Promise<WebTestPilotDataItem[]> {
        const items: WebTestPilotDataItem[] = [];
        
        try {
            switch (this.loadType) {
            case TEST_MENU_ID:
                await this.loadDataRecursive(this.testsDir, items, this.testsDir, TEST_MENU_ID);
                break;
            case FIXTURE_MENU_ID:
                await this.loadDataRecursive(this.fixturesDir, items, this.fixturesDir, FIXTURE_MENU_ID);
                break;
            case ENV_MENU_ID:
                await this.loadDataRecursive(this.envDir, items, this.envDir, ENV_MENU_ID);
                break;
            }

            console.log('FileSystemService.readStructure loaded items:', items);
        } catch (error) {
            console.error('Error reading .webtestpilot directory:', error);
        }

        return items;
    }

    private async loadDataRecursive(rootPath: string, items: WebTestPilotDataItem[], currentPath: string = '', loadType: POSSIBLE_MENUS): Promise<void> {
        try {
            const entries = await fs.readdir(currentPath, { withFileTypes: true });
            for (const entry of entries) {
                const entryFullPath = path.join(currentPath, entry.name);

                if (entry.isDirectory()) {
                    const folderItem: FolderItem = {
                        id: entryFullPath,
                        name: entry.name,
                        type: 'folder',
                        parentId: rootPath === currentPath ? loadType : currentPath,
                        createdAt: new Date(),
                        updatedAt: new Date()
                    };
                    items.push(folderItem);
                    await this.loadDataRecursive(rootPath, items, entryFullPath, loadType);
                } else if (entry.isFile() && entry.name.endsWith('.json')) {
                    try {
                        const content = await fs.readFile(entryFullPath, 'utf-8');
                        const data = JSON.parse(content);
                        let item: Partial<WebTestPilotDataItem> = {
                            id: entryFullPath,
                            name: this.extractTestName(entry.name, data),
                            parentId: rootPath === currentPath ? loadType : currentPath,
                            createdAt: new Date(data.createdAt || Date.now()),
                            updatedAt: new Date(data.updatedAt || Date.now())
                        };
                        switch (loadType) {
                        case TEST_MENU_ID:
                            item = {
                                ...item,
                                type: 'test',
                                url: data.url || '',
                                fixtureId: data.fixtureId,
                                actions: data.actions || [],
                            } as TestItem;
                            break;
                        case FIXTURE_MENU_ID:
                            item = {
                                ...item,
                                type: 'fixture',
                                actions: data.actions || [],
                            } as FixtureItem;
                            break;
                        case ENV_MENU_ID:
                            item = {
                                ...item,
                                type: 'environment',
                                environmentVariables: data.environmentVariables || {},
                            } as EnvironmentItem;
                            break;
                        }
                        items.push(item as WebTestPilotDataItem);
                    } catch (error) {
                        console.error(`Error reading test file ${entryFullPath}:`, error);
                    }
                }
            }
        } catch (error) {
            console.error(`Error reading directory ${rootPath}:`, error);
        }
    }

    private extractTestName(fileName: string, testData: any): string {
        // Remove .json extension
        const baseName = fileName.replace(/\.json$/, '');
        
        // Use name from test data if available, otherwise use filename
        return testData.name || baseName;
    }

    async createTest(name: string, folderPath?: string): Promise<TestItem> {
        const testFileName = this.generateTestFileName(name);
        const testId = folderPath 
            ? path.join(folderPath, testFileName)
            : testFileName;

        const testItem: TestItem = {
            id: testId,
            name,
            type: 'test',
            url: 'http://localhost:8080/',
            actions: [],
            parentId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date()
        };

        const filePath = path.join(this.testsDir, testId);
        await this.writeTestFile(filePath, testItem);
        return testItem;
    }

    async createFolder(name: string, parentPath?: string): Promise<FolderItem> {
        // Sanitize folder name
        const sanitizedName = name.replace(/[<>:"/\\|?*]/g, '_').trim();
        
        const folderId = parentPath 
            ? path.join(parentPath, sanitizedName)
            : sanitizedName;

        const folderItem: FolderItem = {
            id: folderId,
            name: sanitizedName,
            type: 'folder',
            parentId: parentPath ? parentPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date()
        };

        const folderPath = path.join(this.webTestPilotDir, folderId);
        await fs.mkdir(folderPath, { recursive: true });
        return folderItem;
    }

    async deleteTest(testPath: string): Promise<void> {
        const filePath = path.join(this.testsDir, testPath);
        await fs.unlink(filePath);
    }

    async deleteFolder(folderPath: string): Promise<void> {
        const fullPath = path.join(this.webTestPilotDir, folderPath);
        await fs.rm(fullPath, { recursive: true, force: true });
    }

    async updateTest(testPath: string, testItem: TestItem): Promise<void> {
        await this.writeTestFile(testPath, testItem);
    }

    async updateFixture(fixturePath: string, fixtureItem: FixtureItem): Promise<void> {
        await this.writeFixtureFile(fixturePath, fixtureItem);
    }

    async createFixture(name: string, folderPath?: string): Promise<FixtureItem> {
        const fixtureFileName = this.generateTestFileName(name);
        const fixtureId = folderPath 
            ? path.join(folderPath, fixtureFileName)
            : fixtureFileName;

        const fixtureItem: FixtureItem = {
            id: fixtureId,
            name,
            type: 'fixture',
            actions: [],
            parentId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date()
        };

        const filePath = path.join(this.fixturesDir, fixtureId);
        await this.writeFixtureFile(filePath, fixtureItem);
        return fixtureItem;
    }

    private async writeTestFile(filePath: string, testItem: TestItem): Promise<void> {
        const testContent = {
            name: testItem.name,
            url: testItem.url,
            fixtureId: testItem.fixtureId,
            actions: testItem.actions || [],
            createdAt: testItem.createdAt.toISOString(),
            updatedAt: testItem.updatedAt.toISOString()
        };

        try {
            // Write to a temporary file first, then rename to avoid corruption
            const tempFilePath = filePath + '.tmp';
            await fs.writeFile(tempFilePath, JSON.stringify(testContent, null, 2), 'utf-8');
            await fs.rename(tempFilePath, filePath);
        } catch (error) {
            console.error('Failed to write test file:', error);
            throw error;
        }
    }

    private async writeFixtureFile(filePath: string, fixtureItem: FixtureItem): Promise<void> {
        const fixtureContent = {
            name: fixtureItem.name,
            actions: fixtureItem.actions || [],
            createdAt: fixtureItem.createdAt.toISOString(),
            updatedAt: fixtureItem.updatedAt.toISOString()
        };

        try {
            // Write to a temporary file first, then rename to avoid corruption
            const tempFilePath = filePath + '.tmp';
            await fs.writeFile(tempFilePath, JSON.stringify(fixtureContent, null, 2), 'utf-8');
            await fs.rename(tempFilePath, filePath);
        } catch (error) {
            console.error('Failed to write fixture file:', error);
            throw error;
        }
    }

    async createEnvironment(name: string, folderPath?: string): Promise<EnvironmentItem> {
        const environmentFileName = this.generateTestFileName(name);
        const environmentId = folderPath 
            ? path.join(folderPath, environmentFileName)
            : environmentFileName;

        const environmentItem: EnvironmentItem = {
            id: environmentId,
            name,
            type: 'environment',
            environmentVariables: {},
            parentId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date()
        };

        const filePath = path.join(this.envDir, environmentId);
        await this.writeEnvironmentFile(filePath, environmentItem);
        return environmentItem;
    }

    async updateEnvironment(environmentPath: string, environmentItem: EnvironmentItem): Promise<void> {
        await this.writeEnvironmentFile(environmentPath, environmentItem);
    }

    private async writeEnvironmentFile(filePath: string, environmentItem: EnvironmentItem): Promise<void> {
        const environmentContent = {
            name: environmentItem.name,
            environmentVariables: environmentItem.environmentVariables || {},
            createdAt: environmentItem.createdAt.toISOString(),
            updatedAt: environmentItem.updatedAt.toISOString()
        };

        try {
            // Write to a temporary file first, then rename to avoid corruption
            const tempFilePath = filePath + '.tmp';
            await fs.writeFile(tempFilePath, JSON.stringify(environmentContent, null, 2), 'utf-8');
            await fs.rename(tempFilePath, filePath);
        } catch (error) {
            console.error('Failed to write environment file:', error);
            throw error;
        }
    }

    private generateTestFileName(name: string): string {
        // Sanitize name for filename
        const sanitizedName = name.replace(/[^a-zA-Z0-9-_]/g, '_').trim();
        const timestamp = Date.now();
        return `${sanitizedName}_${timestamp}.json`;
    }

    startWatching(callback: () => void): void {
        if (this.fileWatcher) {
            this.fileWatcher.dispose();
        }

        // Watch both the main directory and fixtures directory
        this.fileWatcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(this.webTestPilotDir, '**/*'),
            false,
            false,
            false
        );

        this.fileWatcher.onDidCreate(() => callback());
        this.fileWatcher.onDidDelete(() => callback());
        this.fileWatcher.onDidChange(() => callback());
    }

    dispose(): void {
        if (this.fileWatcher) {
            this.fileWatcher.dispose();
        }
    }
}