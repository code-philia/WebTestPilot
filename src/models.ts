export const TEST_MENU_ID = 'test';
export const FIXTURE_MENU_ID = 'fixture';
export const ENV_MENU_ID = 'environment';
export const POSSIBLE_MENU_IDS = [TEST_MENU_ID, FIXTURE_MENU_ID, ENV_MENU_ID];
export type POSSIBLE_MENUS = typeof TEST_MENU_ID | typeof FIXTURE_MENU_ID | typeof ENV_MENU_ID;

export interface TestAction {
    action: string;
    expectedResult: string;
}

interface SidebarItemBase {
    id: string;
    name: string;
    type: string;
    parentId: string | undefined;
    createdAt: Date;
    updatedAt: Date;
    fullPath: string;
}

export interface MenuItem extends SidebarItemBase {
    type: 'menu';
    icon: string;
}

export interface TestItem extends SidebarItemBase {
    type: 'test';
    url?: string;
    fixtureId?: string;
    actions?: TestAction[];
}

export interface FixtureItem extends SidebarItemBase {
    type: 'fixture';
    actions: TestAction[];
}

export interface EnvironmentItem extends SidebarItemBase {
    type: 'environment';
    environmentVariables: Record<string, string>;
}

export interface FolderItem extends SidebarItemBase {
    type: 'folder';
}


export type TreeItem = TestItem | FolderItem | MenuItem | FixtureItem | EnvironmentItem;