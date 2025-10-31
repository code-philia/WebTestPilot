import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { TestItem, FolderItem, TreeItem as WebTestPilotDataItem } from './models';

export class FileSystemService {
    private webTestPilotDir: string;
    private fixturesDir: string;
    private fileWatcher: vscode.FileSystemWatcher | undefined;

    constructor(private workspaceRoot: string) {
        this.webTestPilotDir = path.join(workspaceRoot, '.webtestpilot');
        this.fixturesDir = path.join(this.webTestPilotDir, '.fixtures');
    }

    async initialize(): Promise<void> {
        try {
            await fs.access(this.webTestPilotDir);
        } catch {
            await fs.mkdir(this.webTestPilotDir, { recursive: true });
        }
        
        try {
            await fs.access(this.fixturesDir);
        } catch {
            await fs.mkdir(this.fixturesDir, { recursive: true });
        }
    }

    async readStructure(): Promise<WebTestPilotDataItem[]> {
        const items: WebTestPilotDataItem[] = [];
        
        try {
            await this.readDirectoryRecursive(this.webTestPilotDir, items);
        } catch (error) {
            console.error('Error reading .webtestpilot directory:', error);
        }

        return items;
    }

    private async readDirectoryRecursive(dirPath: string, items: WebTestPilotDataItem[], relativePath: string = ''): Promise<void> {
        try {
            const entries = await fs.readdir(dirPath, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                const relativeEntryPath = relativePath ? path.join(relativePath, entry.name) : entry.name;

                if (entry.isDirectory()) {
                    // Skip .fixtures directory as it's handled separately
                    if (entry.name === '.fixtures') {
                        continue;
                    }
                    
                    // Create folder item
                    const folderItem: FolderItem = {
                        id: relativeEntryPath,
                        name: entry.name,
                        type: 'folder',
                        parentId: relativePath ? relativePath : undefined,
                        createdAt: new Date(),
                        updatedAt: new Date()
                    };
                    items.push(folderItem);

                    // Recursively read subdirectory
                    await this.readDirectoryRecursive(fullPath, items, relativeEntryPath);
                } else if (entry.isFile() && entry.name.endsWith('.json')) {
                    // Read test file
                    try {
                        const content = await fs.readFile(fullPath, 'utf-8');
                        const testData = JSON.parse(content);
                        
                        const testItem: TestItem = {
                            id: relativeEntryPath,
                            name: this.extractTestName(entry.name, testData),
                            type: 'test',
                            url: testData.url || '',
                            actions: testData.actions || [],
                            folderId: relativePath ? relativePath : undefined,
                            createdAt: new Date(testData.createdAt || Date.now()),
                            updatedAt: new Date(testData.updatedAt || Date.now())
                        };
                        items.push(testItem);
                    } catch (error) {
                        console.error(`Error reading test file ${fullPath}:`, error);
                    }
                }
            }
        } catch (error) {
            console.error(`Error reading directory ${dirPath}:`, error);
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
            folderId: folderPath ? folderPath : undefined,
            createdAt: new Date(),
            updatedAt: new Date()
        };

        const filePath = path.join(this.webTestPilotDir, testId);
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
        const filePath = path.join(this.webTestPilotDir, testPath);
        await fs.unlink(filePath);
    }

    async deleteFolder(folderPath: string): Promise<void> {
        const fullPath = path.join(this.webTestPilotDir, folderPath);
        await fs.rm(fullPath, { recursive: true, force: true });
    }

    async updateTest(testPath: string, testItem: TestItem): Promise<void> {
        try {
            const filePath = path.join(this.webTestPilotDir, testPath);
            
            // Ensure the directory exists
            const dir = path.dirname(filePath);
            await fs.mkdir(dir, { recursive: true });
            
            await this.writeTestFile(filePath, testItem);
        } catch (error) {
            console.error('FileSystemService.updateTest failed:', error);
            
            // Provide more specific error messages
            if (error instanceof Error && 'code' in error) {
                const errorCode = (error as any).code;
                if (errorCode === 'EACCES') {
                    throw new Error(`Permission denied: Cannot write to file. Please check file permissions for: ${this.webTestPilotDir}`);
                } else if (errorCode === 'ENOENT') {
                    throw new Error(`Directory not found: ${this.webTestPilotDir}. Please ensure the workspace directory exists.`);
                }
            }
            throw error;
        }
    }

    private async writeTestFile(filePath: string, testItem: TestItem): Promise<void> {
        const testContent = {
            name: testItem.name,
            url: testItem.url,
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