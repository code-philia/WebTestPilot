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
- Python 3.12 (for runtime)

## Installation

### 1. Start the Local Remote Browser

```bash
source browser.sh
```

### 2. Setup WebTestPilot Runtime

#### Environment Variables (if using OpenAI)

```bash
cp .env.example .env
# Add your OPENAI_API_KEY
```

#### Python Environment

```bash
cd webtestpilot
uv sync
source ./.venv/bin/activate
python3 -V
uv run baml-cli generate
```

### 3. Setup Extension

```bash
yarn install:all
yarn package
```

## Usage

### Start the Development Server

1. Open `src/extension.ts` in a new VS Code window.
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and type "Debug: Start Debugging", then select it.
3. (Temporary workaround) In the debug window, press `Ctrl+Shift+P` and type "WebTestPilot: Set Workspace...", then select the WebTestPilot folder.
4. Click the WebTestPilot extension icon in the sidebar to start using it.
