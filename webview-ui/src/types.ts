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

export interface FixtureItem {
  id: string;
  name: string;
  type: 'fixture';
  actions: TestAction[];
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

export interface EnvironmentItem {
  id: string;
  name: string;
  type: 'environment';
  environmentVariables: Record<string, string>;
  folderId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export type TreeItem = TestItem | FixtureItem | FolderItem | EnvironmentItem;

// Webview-specific types
export interface TestEditorData {
  id?: string;
  folderId?: string;
  name: string;
  url: string;
  fixtureId?: string;
  actions: TestAction[];
}

export interface FixtureEditorData {
  id?: string;
  folderId?: string;
  name: string;
  actions: TestAction[];
}

export interface EnvironmentEditorData {
  id?: string;
  folderId?: string;
  name: string;
  environmentVariables: Record<string, string>;
}

export type SavePayload = Pick<TestEditorData, 'name' | 'url' | 'fixtureId' | 'actions'>;
export type SaveFixturePayload = Pick<FixtureEditorData, 'name' | 'actions'>;
export type SaveEnvironmentPayload = Pick<EnvironmentEditorData, 'name' | 'environmentVariables'>;

// Message types
export type ExtensionMessage =
  | { command: 'setTestData'; payload: Partial<TestEditorData> }
  | { command: 'saveSuccess'; message?: string }
  | { command: 'error'; message: string };

export type WebviewMessage =
  | { command: 'save'; data: SavePayload }
  | { command: 'saveAndRun'; data: SavePayload }
  | { command: 'updateTest'; data: Partial<TestEditorData> }
  | { command: 'updateFixture'; data: Partial<FixtureEditorData> }
  | { command: 'updateEnvironment'; data: Partial<EnvironmentEditorData> }
  | { command: 'close' }
  | { command: 'showError'; text: string }
  | { command: 'ready' }
  | { command: 'stopTest'; testId: string }
  | { command: 'stopAll' }
  | { command: 'viewLogs'; testId: string; testName: string }
  | { command: 'clearTabs' };
