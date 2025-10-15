// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { WebTestPilotTreeDataProvider, WebTestPilotTreeItem } from './treeDataProvider';
import { TestItem, FolderItem } from './models';
import { TestEditorPanel } from './testEditorPanel';
import { TestRunnerPanel } from './testRunnerPanel';
import { ImportPanel, ImportData } from './importPanel';

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

			// Open the test editor panel
			TestEditorPanel.createOrShow(
				context.extensionUri,
				fullTestItem,
				async (updatedTest: TestItem) => {
					// Save the updated test
					await treeDataProvider.updateTest(test.id, updatedTest);
				}
			);
		} catch (error) {
			// If file doesn't exist, create a new test with default actions
			const newTestItem: TestItem = {
				...test,
				actions: []
			};

			TestEditorPanel.createOrShow(
				context.extensionUri,
				newTestItem,
				async (updatedTest: TestItem) => {
					// Save the updated test
					await treeDataProvider.updateTest(test.id, updatedTest);
				}
			);
		}
	});

	const createTestRootCommand = vscode.commands.registerCommand('webtestpilot.createTestRoot', () => {
		vscode.commands.executeCommand('webtestpilot.createTest');
	});

	const createFolderRootCommand = vscode.commands.registerCommand('webtestpilot.createFolderRoot', () => {
		vscode.commands.executeCommand('webtestpilot.createFolder');
	});

	const runTestCommand = vscode.commands.registerCommand('webtestpilot.runTest', async (test: TestItem) => {
		console.log('runTestCommand called for test:', test);
		
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

	const runFolderCommand = vscode.commands.registerCommand('webtestpilot.runFolder', async (folder: FolderItem) => {
		// Get all tests in this folder (including subfolders)
		const testsInFolder = treeDataProvider.getChildrenTests(folder.id);
		
		if (testsInFolder.length === 0) {
			vscode.window.showInformationMessage(`No test cases found in folder "${folder.name}"`);
			return;
		}

		vscode.window.showInformationMessage(`Running ${testsInFolder.length} test case(s) in folder "${folder.name}"...`, {
			detail: `Found ${testsInFolder.length} test case(s) to execute`
		});

		// TODO: Implement actual test execution logic for all tests in folder
		// For now, just show the message
	});

	const importCommand = vscode.commands.registerCommand('webtestpilot.import', async () => {
		console.log('Import command triggered');
		vscode.window.showInformationMessage('Import command triggered!');
		
		ImportPanel.createOrShow(
			context.extensionUri,
			async (data: ImportData) => {
				console.log('Import data received:', data);
				// Create a new test based on the imported data
				const testName = `${data.appName} - Imported Test`;
				
				// Create the test with basic information and get the created test
				const newTest = await treeDataProvider.createTest(testName, undefined);
				
				// Update the test with the imported data
				const updatedTest: TestItem = {
					...newTest,
					url: data.url,
					actions: data.requirements ? [{
						action: `Verify requirements: ${data.requirements}`,
						expectedResult: "Requirements should be met"
					}] : []
				};
				
				await treeDataProvider.updateTest(newTest.id, updatedTest);
				
				// Open the test editor for further customization
				TestEditorPanel.createOrShow(
					context.extensionUri,
					updatedTest,
					async (testItem: TestItem) => {
						await treeDataProvider.updateTest(testItem.id, testItem);
					}
				);
			}
		);
	});

	const testCdpConnectionCommand = vscode.commands.registerCommand('webtestpilot.testCdpConnection', async () => {
		const cdpEndpoint = TestRunnerPanel.getCdpEndpoint();
		vscode.window.withProgress({
			location: vscode.ProgressLocation.Notification,
			title: `Testing CDP connection to ${cdpEndpoint}...`,
			cancellable: false
		}, async () => {
			const isConnected = await TestRunnerPanel.testCdpConnection();
			if (isConnected) {
				vscode.window.showInformationMessage(
					`✅ CDP connection successful!`,
					{ detail: `Connected to: ${cdpEndpoint}\n\nYour Python automation scripts can use this endpoint.` }
				);
			} else {
				vscode.window.showErrorMessage(
					`❌ CDP connection failed`,
					{
						modal: true,
						detail: `Could not connect to: ${cdpEndpoint}\n\nMake sure Chrome/Chromium is running with remote debugging enabled:\n\ngoogle-chrome --remote-debugging-port=9222`
					},
					'Open Settings'
				).then(selection => {
					if (selection === 'Open Settings') {
						vscode.commands.executeCommand('workbench.action.openSettings', 'webtestpilot.cdpEndpoint');
					}
				});
			}
		});
	});

	// Add all disposables to context
	context.subscriptions.push(
		treeView,
		createTestCommand,
		createFolderCommand,
		deleteItemCommand,
		openTestCommand,
		createTestRootCommand,
		createFolderRootCommand,
		runTestCommand,
		addTestCaseCommand,
		addFolderCommand,
		runFolderCommand,
		importCommand,
		testCdpConnectionCommand,
		treeDataProvider // Dispose the tree provider to clean up file watchers
	);
}

// This method is called when your extension is deactivated
export function deactivate() {
	// Cleanup will be handled by disposables
}
