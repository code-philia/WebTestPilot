// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as path from 'path';
import { promises as fs } from 'fs';
import { WebTestPilotTreeDataProvider, WebTestPilotTreeItem } from './treeDataProvider';
import { TestItem, FixtureItem, EnvironmentItem, FolderItem, ENV_MENU_ID, FIXTURE_MENU_ID, TEST_MENU_ID } from './models';
import { TestEditorPanel } from './panels/testEditorPanel';
import { FixtureEditorPanel } from './panels/fixtureEditorPanel';
import { EnvironmentEditorPanel } from './panels/environmentEditorPanel';
import { TestRunnerPanel } from './panels/testRunnerPanel';
import { ParallelTestPanel } from './panels/parallelTestPanel';
import { WorkspaceRootService } from './services/workspaceRootService';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "webtestpilot" is now active!');

    // Create tree data provider
    const treeTestDataProvider = new WebTestPilotTreeDataProvider(context, TEST_MENU_ID);
    const treeFixtureDataProvider = new WebTestPilotTreeDataProvider(context, FIXTURE_MENU_ID);
    const treeEnvironmentDataProvider = new WebTestPilotTreeDataProvider(context, ENV_MENU_ID);

    // Register tree view
    const treeTestView = vscode.window.createTreeView('webtestpilot.treeView', {
        treeDataProvider: treeTestDataProvider,
        showCollapseAll: true
    });
    const treeFixtureView = vscode.window.createTreeView('webtestpilot.treeFixtureView', {
        treeDataProvider: treeFixtureDataProvider,
        showCollapseAll: true
    });
    const treeEnvironmentView = vscode.window.createTreeView('webtestpilot.treeEnvironmentView', {
        treeDataProvider: treeEnvironmentDataProvider,
        showCollapseAll: true
    });

    // Register commands
    const createTestCommand = vscode.commands.registerCommand('webtestpilot.createTest', async () => {
        // Get the currently selected tree item
        const selectedItem = treeTestView.selection[0];
        const folderItem = selectedItem?.item.type === 'folder' ? selectedItem.item as FolderItem : undefined;
		
        const name = await vscode.window.showInputBox({
            prompt: folderItem ? `Enter test name for "${folderItem.name}"` : 'Enter test name',
            placeHolder: 'My Test',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Test name is required';
                }
                return null;
            }
        });

        if (name) {
            const folderId = folderItem?.id;

            await treeTestDataProvider.createTest(name.trim(), folderId);
            const location = folderItem ? `in "${folderItem.name}"` : 'at root';
            vscode.window.showInformationMessage(`Test "${name}" created ${location}!`);
        }
    });

    const createFolderCommand = vscode.commands.registerCommand('webtestpilot.createFolder', async () => {
        // Get the currently selected tree item
        const selectedItem = treeTestView.selection[0];
        const parentFolder = selectedItem?.item.type === 'folder' ? selectedItem.item as FolderItem : undefined;
		
        const name = await vscode.window.showInputBox({
            prompt: parentFolder ? `Enter subfolder name for "${parentFolder.name}"` : 'Enter folder name',
            placeHolder: 'My Folder',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Folder name is required';
                }
                // Validate folder name doesn't contain invalid characters
                if (/[<>:"/\\|?*]/.test(value)) {
                    return 'Folder name contains invalid characters';
                }
                return null;
            }
        });

        if (name) {
            const parentId = parentFolder?.id;

            await treeTestDataProvider.createFolder(name.trim(), parentId);
            const location = parentFolder ? `in "${parentFolder.name}"` : 'at root';
            vscode.window.showInformationMessage(`Folder "${name}" created ${location}!`);
        }
    });

    const deleteItemCommand = vscode.commands.registerCommand('webtestpilot.deleteItem', async (treeItem: WebTestPilotTreeItem) => {
        const itemType = treeItem.item.type === 'test' ? 'test' : treeItem.item.type === 'fixture' ? 'fixture' : 'folder';
        const result = await vscode.window.showWarningMessage(
            `Are you sure you want to delete this ${itemType}?`,
            { modal: true },
            'Delete',
            'Cancel'
        );

        if (result === 'Delete') {
            treeTestDataProvider.deleteItem(treeItem.item);
            vscode.window.showInformationMessage(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully!`);
        }
    });

    const openTestCommand = vscode.commands.registerCommand('webtestpilot.openTest', async (test: TestItem) => {
        // Load the actual test data from file to get the complete test with actions
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        TestEditorPanel.createOrShow(
            context.extensionUri,
            test,
            treeTestDataProvider,
            treeFixtureDataProvider
        );
    });

    const openFixtureCommand = vscode.commands.registerCommand('webtestpilot.openFixture', async (fixture: FixtureItem) => {
        // Load the actual fixture data from file to get the complete fixture with actions
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        // Open the fixture editor panel
        FixtureEditorPanel.createOrShow(
            context.extensionUri,
            fixture,
            treeFixtureDataProvider
        );
    });

    const createFixtureCommand = vscode.commands.registerCommand('webtestpilot.createFixture', async () => {
        // Get the currently selected tree item
        const selectedItem = treeFixtureView.selection[0];
        const folderItem = selectedItem?.item.type === 'folder' ? selectedItem.item as FolderItem : undefined;
		
        const name = await vscode.window.showInputBox({
            prompt: folderItem ? `Enter fixture name for "${folderItem.name}"` : 'Enter fixture name',
            placeHolder: 'My Fixture',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Fixture name is required';
                }
                return null;
            }
        });

        if (name) {
            const folderId = folderItem?.id;

            await treeFixtureDataProvider.createFixture(name.trim(), folderId);
            const location = folderItem ? `in "${folderItem.name}"` : 'at root';
            vscode.window.showInformationMessage(`Fixture "${name}" created ${location}!`);
        }
    });

    const createFixtureRootCommand = vscode.commands.registerCommand('webtestpilot.createFixtureRoot', () => {
        vscode.commands.executeCommand('webtestpilot.createFixture');
    });

    const createEnvironmentCommand = vscode.commands.registerCommand('webtestpilot.createEnvironment', async () => {
        // Get the currently selected tree item
        const selectedItem = treeEnvironmentView.selection[0];
        const folderItem = selectedItem?.item.type === 'folder' ? selectedItem.item as FolderItem : undefined;
		
        const name = await vscode.window.showInputBox({
            prompt: folderItem ? `Enter environment name for "${folderItem.name}"` : 'Enter environment name',
            placeHolder: 'My Environment',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Environment name cannot be empty';
                }
                return null;
            }
        });

        if (name) {
            const folderId = folderItem?.id;
            await treeEnvironmentDataProvider.createEnvironment(name.trim(), folderId);
            const location = folderItem ? `in "${folderItem.name}"` : 'at root';
            vscode.window.showInformationMessage(`Environment "${name}" created ${location}!`);
        }
    });

    const createEnvironmentRootCommand = vscode.commands.registerCommand('webtestpilot.createEnvironmentRoot', () => {
        vscode.commands.executeCommand('webtestpilot.createEnvironment');
    });

    const openEnvironmentCommand = vscode.commands.registerCommand('webtestpilot.openEnvironment', async (environment: EnvironmentItem) => {
        // Load the actual environment data from file to get the complete environment
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        EnvironmentEditorPanel.createOrShow(
            context.extensionUri,
            environment,
            treeEnvironmentDataProvider
        );
    });

    const runTestCommand = vscode.commands.registerCommand('webtestpilot.runTest', async (treeItemOrTest: any) => {
        console.log('runTestCommand called with:', treeItemOrTest);
		
        // Extract TestItem from WebTestPilotTreeItem if needed
        let test: TestItem;
        if (treeItemOrTest && treeItemOrTest.item && treeItemOrTest.item.type === 'test') {
            // This is a WebTestPilotTreeItem
            test = treeItemOrTest.item as TestItem;
        } else if (treeItemOrTest && treeItemOrTest.type === 'test') {
            // This is already a TestItem
            test = treeItemOrTest as TestItem;
        } else {
            vscode.window.showErrorMessage('Invalid test item');
            return;
        }
		
        // Validate test item
        if (!test || !test.id) {
            vscode.window.showErrorMessage('Invalid test item');
            return;
        }
		
        // Get workspace root
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        // Use TestRunnerPanel to run the test
        await TestRunnerPanel.createOrShow(test, workspaceRoot, context.extensionUri);
    });

    const createTestRootCommand = vscode.commands.registerCommand('webtestpilot.createTestRoot', () => {
        vscode.commands.executeCommand('webtestpilot.createTest');
    });

    const createFolderRootCommand = vscode.commands.registerCommand('webtestpilot.createFolderRoot', () => {
        vscode.commands.executeCommand('webtestpilot.createFolder');
    });

    const addTestCaseCommand = vscode.commands.registerCommand('webtestpilot.addTestCase', async (folderItem: FolderItem) => {
        vscode.commands.executeCommand('webtestpilot.createTest', folderItem);
    });

    const addFolderCommand = vscode.commands.registerCommand('webtestpilot.addFolder', async (parentFolder: FolderItem) => {
        vscode.commands.executeCommand('webtestpilot.createFolder', parentFolder);
    });

    const runFolderCommand = vscode.commands.registerCommand('webtestpilot.runFolder', async (treeItem: any) => {
        // Extract folder item from tree item (similar to createTest command)
        const folderItem = treeItem?.item?.type === 'folder' ? treeItem.item as FolderItem : undefined;
		
        if (!folderItem) {
            vscode.window.showErrorMessage('Invalid folder selection');
            return;
        }

        // Get workspace root
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceRoot) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        // Get all tests in this folder (including subfolders)
        const testsInFolder = treeTestDataProvider.getChildrenTests(folderItem.id);
		
        if (testsInFolder.length === 0) {
            vscode.window.showInformationMessage(`No test cases found in folder "${folderItem.name}"`);
            return;
        }

        // Show confirmation dialog
        const result = await vscode.window.showInformationMessage(
            `Run ${testsInFolder.length} test case(s) in folder "${folderItem.name}" in parallel?`,
            { modal: true },
            'Run Parallel',
            'Cancel'
        );

        if (result === 'Run Parallel') {
            // Store tree data provider and extensionUri globally for parallel runner access
            (global as any).webTestPilotTreeDataProvider = treeTestDataProvider;
            (global as any).extensionUri = context.extensionUri;
			
            // Start parallel test runner
            await ParallelTestPanel.createOrShow(folderItem, workspaceRoot);
        }
    });

    const setWorkspaceRootCommand = vscode.commands.registerCommand('webtestpilot.setWorkspaceRoot', async () => {
        const options: vscode.OpenDialogOptions = {
            canSelectMany: false,
            canSelectFolders: true,
            openLabel: 'Select WebTestPilot Workspace Root'
        };

        const folderUri = await vscode.window.showOpenDialog(options);
        if (folderUri && folderUri[0]) {
            await WorkspaceRootService.setWorkspaceRoot(folderUri[0].fsPath);
        }
    });

    const showWorkspaceRootCommand = vscode.commands.registerCommand('webtestpilot.showWorkspaceRoot', async () => {
        const root = WorkspaceRootService.getWorkspaceRoot();
        if (root) {
            vscode.window.showInformationMessage(`${root}`);
        } else {
            vscode.window.showWarningMessage('No WebTestPilot workspace root configured');
        }
    });

    // Add all disposables to context
    context.subscriptions.push(
        treeTestView,
        treeFixtureView,
        treeEnvironmentView,
        createTestCommand,
        createFolderCommand,
        createFixtureCommand,
        createEnvironmentCommand,
        deleteItemCommand,
        openTestCommand,
        openFixtureCommand,
        openEnvironmentCommand,
        createTestRootCommand,
        createFolderRootCommand,
        createFixtureRootCommand,
        createEnvironmentRootCommand,
        runTestCommand,
        addTestCaseCommand,
        addFolderCommand,
        runFolderCommand,
        setWorkspaceRootCommand,
        showWorkspaceRootCommand,
        treeTestDataProvider, // Dispose the tree provider to clean up file watchers
        treeFixtureDataProvider,
        treeEnvironmentDataProvider
    );
}

// This method is called when your extension is deactivated
export function deactivate() {
    // Cleanup will be handled by disposables
}
