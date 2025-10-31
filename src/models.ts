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