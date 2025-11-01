import * as vscode from 'vscode';

export class WorkspaceRootService {
    /**
     * Gets the workspace root from configuration
     */
    public static getWorkspaceRoot(): string {
        const config = vscode.workspace.getConfiguration('webtestpilot');
        const workspaceRoot = config.get<string>('workspaceRoot');
        
        if (workspaceRoot && workspaceRoot.trim()) {
            return workspaceRoot.trim();
        }
        
        // Fallback to current workspace folder
        return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
    }

    public static getOpenedFolderWorkspaceRoot(): string {
        return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
    }

    /**
     * Sets the workspace root configuration
     */
    public static async setWorkspaceRoot(rootPath: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('webtestpilot');
        await config.update('workspaceRoot', rootPath, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`Workspace root: ${rootPath}`);
    }
}