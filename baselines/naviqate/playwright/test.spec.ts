import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

function getDirectories(source: string): string[] {
  return fs.readdirSync(source, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => path.join(source, dirent.name));
}

const outFolderPath = '../out';
const websiteDirectories = getDirectories(outFolderPath);

for (const websiteDirectory of websiteDirectories) {
  const website = path.basename(websiteDirectory);
  const taskDirectories = getDirectories(websiteDirectory);

  for (const taskDirectory of taskDirectories) {
    test(`Dynamic actions for ${website} - ${path.basename(taskDirectory)}`, async ({ page , context }) => {
      page.setViewportSize({ width: 1920, height: 1080 });
      const historyFilePath = path.join(taskDirectory, 'history.json');
      if (!fs.existsSync(historyFilePath)) {
        console.error(`history.json not found in ${taskDirectory}`);
        return;
      }
      const actions = JSON.parse(fs.readFileSync(historyFilePath, 'utf-8'));

      await page.goto(`https://${website}`, { waitUntil: 'load' });
      

      await context.tracing.start({ screenshots: true, snapshots: true });

      for (const action of actions) {
        const [actionType, actionValue] = action.action.split(':');

        const processedXPath = action.xpath.replace(/^\/html\/body/, '/');

        switch (actionType) {
          case 'click':
            await page.waitForSelector(`xpath=${processedXPath}`);
            await page.click(`xpath=${processedXPath}`, { force: true });
            break;
          case 'type':
            await page.waitForSelector(`xpath=${processedXPath}`, { state: 'visible' });
            await page.fill(`xpath=${processedXPath}`, actionValue);
            break;
          case 'select':
            await page.waitForSelector(`xpath=${processedXPath}`, { state: 'visible' });
            const index = parseInt(actionValue, 10);
            const selectElement = await page.$(`xpath=${processedXPath}`);
            await selectElement.selectOption({ index });
            break;
        }
        await page.waitForLoadState('load');
      }

      await page.waitForLoadState('load', { timeout: 60000 });

      await context.tracing.stop({ path: `trace-${website}-${path.basename(taskDirectory)}.zip` });
    });
  }
}
