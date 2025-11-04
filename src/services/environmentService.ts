import * as vscode from 'vscode';
import { EnvironmentItem } from '../models';

export class EnvironmentService {
    private _onDidChangeEnvironment = new vscode.EventEmitter<EnvironmentItem | undefined>();
    readonly onDidChangeEnvironment = this._onDidChangeEnvironment.event;

    constructor(private context: vscode.ExtensionContext) {}

    getSelectedEnvironment(): EnvironmentItem | undefined {
        return this.context.workspaceState.get<EnvironmentItem>('selectedEnv');
    }

    async setSelectedEnvironment(env: EnvironmentItem | undefined): Promise<void> {
        await this.context.workspaceState.update('selectedEnv', env);
        this._onDidChangeEnvironment.fire(env);
    }

    isSelected(envId: string): boolean {
        const selected = this.getSelectedEnvironment();
        return selected?.id === envId;
    }

    dispose(): void {
        this._onDidChangeEnvironment.dispose();
    }
}
