// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { WebTestPilotTreeDataProvider, WebTestPilotTreeItem } from './treeDataProvider';
import { TestItem, FolderItem } from './models';
import { TestEditorPanel } from './testEditorPanel';
import { FixtureEditorPanel } from './fixtureEditorPanel';
import { TestRunnerPanel } from './testRunnerPanel';
import { ParallelTestRunner } from './parallelTestRunner';
import { ImportPanel } from './importPanel';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "webtestpilot" is now active!');

	// Create tree data provider
	const treeDataProvider = new WebTestPilotTreeDataProvider(context);
	
	// Register tree view
	const treeView = vscode.window.createTreeView('webtestpilot.treeView', {
		treeDataProvider,
		showCollapseAll: true
	});

	// Register commands
	const createTestCommand = vscode.commands.registerCommand('webtestpilot.createTest', async () => {
		// Get the currently selected tree item
		const selectedItem = treeView.selection[0];
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

			await treeDataProvider.createTest(name.trim(), folderId);
			const location = folderItem ? `in "${folderItem.name}"` : 'at root';
			vscode.window.showInformationMessage(`Test "${name}" created ${location}!`);
		}
	});

	const createFolderCommand = vscode.commands.registerCommand('webtestpilot.createFolder', async () => {
		// Get the currently selected tree item
		const selectedItem = treeView.selection[0];
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

			await treeDataProvider.createFolder(name.trim(), parentId);
			const location = parentFolder ? `in "${parentFolder.name}"` : 'at root';
			vscode.window.showInformationMessage(`Folder "${name}" created ${location}!`);
		}
	});

	const deleteItemCommand = vscode.commands.registerCommand('webtestpilot.deleteItem', async (treeItem: WebTestPilotTreeItem) => {
		const itemType = treeItem.item.type === 'test' ? 'test' : 'folder';
		const result = await vscode.window.showWarningMessage(
			`Are you sure you want to delete this ${itemType}?`,
			{ modal: true },
			'Delete',
			'Cancel'
		);

		if (result === 'Delete') {
			treeDataProvider.deleteItem(treeItem.item);
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

		const testFilePath = require('path').join(workspaceRoot, '.webtestpilot', test.id);
		
		try {
			const fs = require('fs').promises;
			const content = await fs.readFile(testFilePath, 'utf-8');
			const testData = JSON.parse(content);
			
		// Merge the file data with the tree item data
			const fullTestItem: TestItem = {
				...test,
				actions: testData.actions || []
			};

			// Open the fixture editor panel with test tab
			FixtureEditorPanel.createOrShow(
				context.extensionUri,
				treeDataProvider,
				fullTestItem
			);
		} catch (error) {
			// If file doesn't exist, create a new test with default actions
			const newTestItem: TestItem = {
				...test,
				actions: []
			};

			FixtureEditorPanel.createOrShow(
				context.extensionUri,
				treeDataProvider,
				newTestItem
			);
		}
	});

	const openFixtureEditorCommand = vscode.commands.registerCommand('webtestpilot.openFixtureEditor', async () => {
		// Open the fixture editor panel without a specific test
		FixtureEditorPanel.createOrShow(
			context.extensionUri,
			treeDataProvider
		);
	});

	const createTestRootCommand = vscode.commands.registerCommand('webtestpilot.createTestRoot', () => {
		vscode.commands.executeCommand('webtestpilot.createTest');
	});

	const createFolderRootCommand = vscode.commands.registerCommand('webtestpilot.createFolderRoot', () => {
		vscode.commands.executeCommand('webtestpilot.createFolder');
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
		await TestRunnerPanel.createOrShow(test, workspaceRoot);
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
		const testsInFolder = treeDataProvider.getChildrenTests(folderItem.id);
		
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
			// Store tree data provider globally for parallel runner access
			(global as any).webTestPilotTreeDataProvider = treeDataProvider;
			
			// Start parallel test runner
			await ParallelTestRunner.createOrShow(folderItem, workspaceRoot);
		}
	});

	const importCommand = vscode.commands.registerCommand('webtestpilot.import', async () => {
		console.log('Import command triggered');
		ImportPanel.createOrShow(context.extensionUri, context, treeDataProvider);
	});



	const setWorkspaceRootCommand = vscode.commands.registerCommand('webtestpilot.setWorkspaceRoot', async () => {
		const options: vscode.OpenDialogOptions = {
			canSelectMany: false,
			canSelectFolders: true,
			openLabel: 'Select WebTestPilot Workspace Root'
		};

		const folderUri = await vscode.window.showOpenDialog(options);
		if (folderUri && folderUri[0]) {
			const { WorkspaceRootService } = await import('./workspaceRootService.js');
			await WorkspaceRootService.setWorkspaceRoot(folderUri[0].fsPath);
		}
	});

	const showWorkspaceRootCommand = vscode.commands.registerCommand('webtestpilot.showWorkspaceRoot', async () => {
		const { WorkspaceRootService } = await import('./workspaceRootService.js');
		const root = WorkspaceRootService.getWorkspaceRoot();
		if (root) {
			vscode.window.showInformationMessage(`WebTestPilot workspace root: ${root}`);
		} else {
			vscode.window.showWarningMessage('No WebTestPilot workspace root configured');
		}
	});

	// Add all disposables to context
	context.subscriptions.push(
		treeView,
		createTestCommand,
		createFolderCommand,
		deleteItemCommand,
		openTestCommand,
		openFixtureEditorCommand,
		createTestRootCommand,
		createFolderRootCommand,
		runTestCommand,
		addTestCaseCommand,
		addFolderCommand,
		runFolderCommand,
		importCommand,
		setWorkspaceRootCommand,
		showWorkspaceRootCommand,
		treeDataProvider // Dispose the tree provider to clean up file watchers
	);
}

// This method is called when your extension is deactivated
export function deactivate() {
	// Cleanup will be handled by disposables
}
