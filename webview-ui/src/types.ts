// Mirror of src/models.ts types for type safety in webview

export interface TestAction {
  action: string;
  expectedResult: string;
}

export interface TestItem {
  id: string;
  name: string;
  type: 'test';
  url?: string;
  actions?: TestAction[];
  folderId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface FolderItem {
  id: string;
  name: string;
  type: 'folder';
  parentId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export type TreeItem = TestItem | FolderItem;

// Webview-specific types
export interface TestEditorData {
  id?: string;
  folderId?: string;
  name: string;
  url: string;
  actions: TestAction[];
}

export type SavePayload = Pick<TestEditorData, 'name' | 'url' | 'actions'>;

// Message types
export type ExtensionMessage =
  | { command: 'setTestData'; payload: Partial<TestEditorData> }
  | { command: 'saveSuccess'; message?: string }
  | { command: 'error'; message: string };

export type WebviewMessage =
  | { command: 'save'; data: SavePayload }
  | { command: 'saveAndRun'; data: SavePayload }
  | { command: 'updateTest'; data: Partial<TestEditorData> }
  | { command: 'close' }
  | { command: 'showError'; text: string };
