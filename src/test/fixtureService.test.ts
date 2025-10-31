import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs/promises';
import { FileSystemService } from '../fileSystemService';
import { FixtureItem } from '../models';

suite('Fixture Service Test Suite', () => {
    let fileSystemService: FileSystemService;
    let testWorkspaceRoot: string;

    setup(async () => {
        // Create a temporary directory for testing
        testWorkspaceRoot = path.join(__dirname, '../../../test-workspace');
        await fs.mkdir(testWorkspaceRoot, { recursive: true });
        
        fileSystemService = new FileSystemService(testWorkspaceRoot);
        await fileSystemService.initialize();
    });

    teardown(async () => {
        // Clean up test directory
        try {
            await fs.rm(testWorkspaceRoot, { recursive: true, force: true });
        } catch (error) {
            // Ignore cleanup errors
        }
    });

    test('Should create .fixtures directory on initialization', async () => {
        const fixturesDir = path.join(testWorkspaceRoot, '.webtestpilot', '.fixtures');
        try {
            await fs.access(fixturesDir);
            assert.ok(true, 'Fixtures directory was created');
        } catch (error) {
            assert.fail('Fixtures directory was not created');
        }
    });

    test('Should create a fixture', async () => {
        const fixture = await fileSystemService.createFixture('Test Fixture');
        
        assert.strictEqual(fixture.name, 'Test Fixture');
        assert.strictEqual(fixture.type, 'fixture');
        assert.ok(fixture.id.endsWith('.json'));
        assert.ok(fixture.actions !== undefined);
        assert.strictEqual(fixture.actions?.length, 0);
    });

    test('Should create a fixture with base fixture', async () => {
        const baseFixture = await fileSystemService.createFixture('Base Fixture');
        const derivedFixture = await fileSystemService.createFixture('Derived Fixture', baseFixture.id);
        
        assert.strictEqual(derivedFixture.baseFixtureId, baseFixture.id);
    });

    test('Should read fixtures from structure', async () => {
        await fileSystemService.createFixture('Fixture 1');
        await fileSystemService.createFixture('Fixture 2');
        
        const structure = await fileSystemService.readStructure();
        const fixtures = structure.filter(item => item.type === 'fixture');
        
        assert.strictEqual(fixtures.length, 2);
        assert.ok(fixtures.some(f => f.name === 'Fixture 1'));
        assert.ok(fixtures.some(f => f.name === 'Fixture 2'));
    });

    test('Should update a fixture', async () => {
        const fixture = await fileSystemService.createFixture('Original Name');
        fixture.name = 'Updated Name';
        fixture.actions = [{ action: 'click', expectedResult: 'element clicked' }];
        
        await fileSystemService.updateFixture(fixture.id, fixture);
        
        const structure = await fileSystemService.readStructure();
        const updatedFixture = structure.find(item => item.id === fixture.id) as FixtureItem;
        
        assert.strictEqual(updatedFixture.name, 'Updated Name');
        assert.strictEqual(updatedFixture.actions?.length, 1);
        assert.strictEqual(updatedFixture.actions![0].action, 'click');
    });

    test('Should delete a fixture', async () => {
        const fixture = await fileSystemService.createFixture('To Delete');
        
        // Verify fixture exists
        let structure = await fileSystemService.readStructure();
        assert.ok(structure.some(item => item.id === fixture.id));
        
        // Delete fixture
        await fileSystemService.deleteFixture(fixture.id);
        
        // Verify fixture is gone
        structure = await fileSystemService.readStructure();
        assert.ok(!structure.some(item => item.id === fixture.id));
    });
});