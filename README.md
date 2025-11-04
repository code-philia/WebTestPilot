# WebTestPilot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Node.js Version](https://img.shields.io/badge/node-%3E%3D22.12.0-brightgreen)](https://nodejs.org/)

An AI-powered VS Code extension for automated web testing and test case generation.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)

## Prerequisites

- [Google Chrome](https://www.google.com/chrome/) installed locally
- Node.js >= 22.12.0
- Python 3.12
- uv

### 2. Setup WebTestPilot Runtime

#### Install Chrome
Install Chrome from instructions here [Google Chrome](https://www.google.com/chrome/).

#### Install uv
Install uv using the following scripts:
```
# For MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# For Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Test the command
uv
```

For more details, refer to [original uv document](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1).

### Setup Extension
```bash
# Node 22
nvm install lts/jod
nvm use lts/jod

# If don't have yarn
npm install --global yarn

# MacOS / Linux / WSL
source setup.sh

# Windows
sh setup.sh
```

## Usage

### Start the Development Server
1. Start chrome browser instance: ```source browser.sh```
2. Open `src/extension.ts` in a new VS Code window.
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and type "Debug: Start Debugging", then select it.
![start-debugging](./docs/assets/start-debugging.png)

4. In the extension debug window, press `Ctrl+Shift+P` and type "WebTestPilot: Set Workspace...", then select the WebTestPilot folder.
![set-workspace](./docs/assets/set-workspace.png)
![choose-workspace](./docs/assets/choose-workspace.png)

5. Click the WebTestPilot extension icon in the sidebar to start using it.
![extension-icon](./docs/assets/extension-icon.png)
6. In the debugger window, open a folder in it.
7. Put the given test cases into .webtestpilot folder of the opened folder in the Extension Development Host window.
![test-folder](./docs/assets/test-folder.png)

### In case of updates
When there are updates to the code base, run the following command and then restart the extension.

First, update build
```bash
# MacOS / Linux / WSL
source setup.sh

# Windows
sh setup.sh
```

Second, restart the extension. Click the restart button here (after debugging started)
![restart-extension](./docs/assets/restart-extension.png)

or, stop the debugger and start again
![stop-extension](./docs/assets/stop-extension.png)

![start-debugging](./docs/assets/start-debugging.png)
