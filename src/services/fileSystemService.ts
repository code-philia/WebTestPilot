import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { TestItem, FolderItem, TreeItem as WebTestPilotDataItem, MenuItem, EnvironmentItem, FixtureItem, FIXTURE_MENU_ID, ENV_MENU_ID, TEST_MENU_ID, POSSIBLE_MENUS } from '../models';
import { generateId } from '../utils/common';


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
        this.testsDir = path.join(this.webTestPilotDir, '.test');
        this.fixturesDir = path.join(this.webTestPilotDir, '.fixture');
        this.envDir = path.join(this.webTestPilotDir, '.environment');
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
                    // Dynamic ids for folder always.
                    const folderItem: FolderItem = {
                        id: entryFullPath,
                        name: entry.name,
                        type: 'folder',
                        parentId: rootPath === currentPath ? loadType : currentPath,
                        createdAt: new Date(),
                        updatedAt: new Date(),
                        fullPath: entryFullPath
                    };
                    items.push(folderItem);
                    await this.loadDataRecursive(rootPath, items, entryFullPath, loadType);
                } else if (entry.isFile() && entry.name.endsWith('.json')) {
                    try {
                        const content = await fs.readFile(entryFullPath, 'utf-8');
                        const data = JSON.parse(content);
                        let item: Partial<WebTestPilotDataItem> = {
                            id: data.id ? data.id : generateId(loadType),
                            name: this.extractTestName(entry.name, data),
                            parentId: rootPath === currentPath ? loadType : currentPath,
                            createdAt: new Date(data.createdAt || Date.now()),
                            updatedAt: new Date(data.updatedAt || Date.now()),
                            fullPath: entryFullPath
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

                        // Write this file so that the id persists if it's not in the first place.
                        if (!data.id) {
                            if (loadType === FIXTURE_MENU_ID) {
                                await this.writeFixtureFile(entryFullPath, item as FixtureItem);
                            } else if (loadType === ENV_MENU_ID) {
                                await this.writeEnvironmentFile(entryFullPath, item as EnvironmentItem);
                            } else if (loadType === TEST_MENU_ID) {
                                await this.writeTestFile(entryFullPath, item as TestItem);
                            }
                        }
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
        const testFullPath = folderPath 
            ? path.join(folderPath, testFileName)
            : path.join(this.testsDir, testFileName);

        const testItem: TestItem = {
            id: generateId('test'),
            name,
            type: 'test',
            url: 'http://localhost:8080/',
            actions: [],
            parentId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date(),
            fullPath: testFullPath
        };

        await this.writeTestFile(testFullPath, testItem);
        return testItem;
    }

    async createFolder(name: string, parentPath?: string, type?: POSSIBLE_MENUS): Promise<FolderItem> {
        const sanitizedName = name.replace(/[<>:"/\\|?*]/g, '_').trim();
        const fullPath = parentPath 
            ? path.join(parentPath, sanitizedName)
            : path.join(this.webTestPilotDir, `.${type}`, sanitizedName);

        const folderItem: FolderItem = {
            id: fullPath,
            name: sanitizedName,
            type: 'folder',
            parentId: parentPath ? parentPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date(),
            fullPath: fullPath,
        };

        await fs.mkdir(fullPath, { recursive: true });
        return folderItem;
    }

    async deleteItem(path: string): Promise<void> {
        await fs.unlink(path);
    }

    async deleteFolder(folderPath: string): Promise<void> {
        await fs.rm(folderPath, { recursive: true, force: true });
    }

    async updateTest(testPath: string, testItem: TestItem): Promise<void> {
        await this.writeTestFile(testPath, testItem);
    }

    async updateFixture(fixturePath: string, fixtureItem: FixtureItem): Promise<void> {
        await this.writeFixtureFile(fixturePath, fixtureItem);
    }

    async createFixture(name: string, folderPath?: string): Promise<FixtureItem> {
        const fixtureFileName = this.generateTestFileName(name);
        const fixtureFullPath = folderPath 
            ? path.join(folderPath, fixtureFileName)
            : path.join(this.fixturesDir, fixtureFileName);

        const fixtureItem: FixtureItem = {
            id: generateId('fixture'),
            name,
            type: 'fixture',
            actions: [],
            parentId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date(),
            fullPath: fixtureFullPath
        };

        await this.writeFixtureFile(fixtureFullPath, fixtureItem);
        return fixtureItem;
    }

    private async writeTestFile(filePath: string, testItem: TestItem): Promise<void> {
        const testContent = {
            id: testItem.id,
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
            id: fixtureItem.id,
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
        const environmentFullPath = folderPath 
            ? path.join(folderPath, environmentFileName)
            : path.join(this.envDir, environmentFileName);

        const environmentItem: EnvironmentItem = {
            id: generateId('environment'),
            name,
            type: 'environment',
            environmentVariables: {},
            parentId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date(),
            fullPath: environmentFullPath
        };

        await this.writeEnvironmentFile(environmentFullPath, environmentItem);
        return environmentItem;
    }

    async updateEnvironment(environmentPath: string, environmentItem: EnvironmentItem): Promise<void> {
        await this.writeEnvironmentFile(environmentPath, environmentItem);
    }

    private async writeEnvironmentFile(filePath: string, environmentItem: EnvironmentItem): Promise<void> {
        const environmentContent = {
            id: environmentItem.id,
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