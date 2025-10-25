# VS Code Extension ↔ Python Agent Integration

This document explains how the VS Code WebTestPilot extension integrates with the Python automation agent.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code Extension                         │
│                                                               │
│  ┌─────────────┐      ┌──────────────┐                      │
│  │  Tree View  │─────▶│ Run Test Cmd │                      │
│  │  (UI)       │      └──────┬───────┘                      │
│  └─────────────┘             │                               │
│                               ▼                               │
│                    ┌─────────────────────┐                   │
│                    │ TestRunnerPanel     │                   │
│                    │  - Load test JSON   │                   │
│                    │  - Spawn Python CLI │                   │
│                    │  - Stream output    │                   │
│                    └──────────┬──────────┘                   │
└───────────────────────────────┼───────────────────────────────┘
                                │
                                │ spawn process with test JSON
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                     Python Agent (CLI)                        │
│                                                               │
│  ┌──────────────┐                                            │
│  │  cli.py      │  Entry point - parses arguments            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────────────┐           │
│  │  1. Load test JSON file                       │           │
│  │  2. Convert actions → Steps                   │           │
│  │  3. Connect to browser via CDP                │           │
│  │  4. Create Session                            │           │
│  │  5. Execute WebTestPilot.run()                │           │
│  │  6. Save trace.zip                            │           │
│  │  7. Return JSON result                        │           │
│  └──────────────────────────────────────────────┘           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                                │
                                │ CDP Protocol
                                │
                        ┌───────▼────────┐
                        │   Chrome/      │
                        │   Chromium     │
                        │   Browser      │
                        └────────────────┘
```

## Data Flow

### 1. Test Definition (VS Code)

Test data is stored in `.webtestpilot/{test-id}.json`:

```json
{
  "id": "abc-123",
  "name": "Login Test",
  "type": "test",
  "url": "https://example.com/login",
  "actions": [
    {
      "action": "Click the login button",
      "expectedResult": "Login form appears"
    },
    {
      "action": "Type 'admin' in username field",
      "expectedResult": "Username field contains 'admin'"
    }
  ],
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-01T00:00:00Z"
}
```

### 2. Execution Trigger (VS Code → Python)

When user clicks "Run Test":

1. **TestRunnerPanel.createOrShow()** is called
2. Test JSON file is loaded
3. Python CLI is spawned with arguments:

```bash
python3 webtestpilot/src/cli.py \
  .webtestpilot/abc-123.json \
  --config webtestpilot/src/config.yaml \
  --cdp-endpoint http://localhost:9222 \
  --trace-output .webtestpilot/traces/abc-123-trace.zip \
  --json-output
```

### 3. Python Processing (cli.py)

```python
# 1. Load test JSON
test_data = json.load(test_file)

# 2. Convert actions to Steps
test_steps = [
    Step(
        condition="",
        action=action["action"],
        expectation=action["expectedResult"]
    )
    for action in test_data["actions"]
]

# 3. Connect to browser
browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
context = browser.contexts[0]
page = context.pages[0]

# 4. Create session and run test
config = Config.load(config_path)
session = Session(page, config)
WebTestPilot.run(session, test_steps, assertion=True)

# 5. Save trace and return result
context.tracing.stop(path=trace_output)
return {"success": True, "steps_executed": len(test_steps)}
```

### 4. Result Communication (Python → VS Code)

Python outputs JSON to stdout:

```json
{
  "success": true,
  "test_name": "Login Test",
  "url": "https://example.com/login",
  "steps_executed": 2,
  "errors": []
}
```

VS Code:
- Captures stdout/stderr
- Parses JSON result
- Shows success/error notification
- Displays output in Output Channel
- Offers to open trace file

## File Structure

```
webtestpilot/
├── src/                          # TypeScript extension code
│   ├── extension.ts              # Extension activation & commands
│   ├── testRunnerPanel.ts        # Test execution & Python integration
│   ├── treeDataProvider.ts       # Tree view data provider
│   ├── testEditorPanel.ts        # Test editor webview
│   └── models.ts                 # TypeScript interfaces
│
├── webtestpilot/                 # Python agent code
│   ├── src/
│   │   ├── main.py               # Main WebTestPilot class
│   │   ├── cli.py                # ⭐ NEW: CLI interface for VS Code
│   │   ├── config.py             # Configuration loader
│   │   ├── config.yaml           # LLM & agent configuration
│   │   ├── executor/             # Action execution logic
│   │   └── parser/               # Test parsing logic
│   │
│   └── pyproject.toml            # Python dependencies
│
└── .webtestpilot/                # Test data directory
    ├── {test-id}.json            # Individual test files
    └── traces/                   # Execution traces
        └── {test-id}-trace.zip
```

## Key Components

### cli.py (New File)

**Purpose**: CLI interface that bridges VS Code extension with Python agent

**Key Functions**:
- `parse_test_action_to_step()`: Converts VS Code action format to Step format
- `run_test_from_file()`: Main execution function
- `main()`: CLI argument parsing and execution

**Usage**:
```bash
# Basic usage
python cli.py path/to/test.json

# With options
python cli.py test.json \
  --config config.yaml \
  --cdp-endpoint http://localhost:9222 \
  --trace-output trace.zip \
  --no-assertions \
  --json-output
```

### main.py (Modified)

**Changes**:
- Refactored `__main__` block to be an example/template
- Removed hardcoded test steps
- Added proper error handling
- Added CLI-friendly output
- Now used as a library by cli.py

**Usage**:
- Import and use `WebTestPilot.run()` in other scripts
- Run directly for quick testing/examples

### testRunnerPanel.ts (Modified)

**Changes**:
- Added Python CLI integration
- Added output channel for real-time logs
- Added trace file management
- Added progress notifications
- Added Python path detection (uses Python extension API)

**New Methods**:
- `getPythonPath()`: Detects correct Python interpreter
- Enhanced `createOrShow()`: Now spawns Python process

## Configuration

### VS Code Settings

Add to `.vscode/settings.json`:

```json
{
  "webtestpilot.cdpEndpoint": "http://localhost:9222",
  "python.defaultInterpreterPath": "path/to/venv/bin/python"
}
```

### Python Config (config.yaml)

Location: `webtestpilot/src/config.yaml`

Contains LLM client configurations, action proposers, assertion settings, etc.

## Prerequisites

### 1. Chrome/Chromium with CDP

Start Chrome with remote debugging:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --remote-debugging-port=9222
```

### 2. Python Environment

Install dependencies:

```bash
cd webtestpilot
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

### 3. VS Code Extensions

- Python extension (ms-python.python) - recommended for interpreter detection
- WebTestPilot extension (this extension)

## Testing the Integration

### Manual Test

1. **Start Chrome with CDP**:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=/tmp/chrome-debug
   ```

2. **Create a test in VS Code**:
   - Open WebTestPilot view
   - Click "Create Test"
   - Add test name and URL
   - Add actions (e.g., "Click login button")

3. **Run the test**:
   - Right-click test in tree view
   - Select "Run Test"
   - Watch output in Output Channel

4. **Check results**:
   - Success/failure notification
   - Trace file in `.webtestpilot/traces/`
   - Detailed logs in Output Channel

### CLI Test (Bypass VS Code)

Test the Python CLI directly:

```bash
cd webtestpilot

# Create a test JSON file
cat > test-example.json << 'EOF'
{
  "id": "test-1",
  "name": "Example Test",
  "url": "https://example.com",
  "actions": [
    {
      "action": "Click the 'More information...' link",
      "expectedResult": "IANA page opens"
    }
  ]
}
EOF

# Run with CLI
python src/cli.py test-example.json \
  --config src/config.yaml \
  --cdp-endpoint http://localhost:9222 \
  --trace-output trace.zip \
  --json-output
```

## Troubleshooting

### Python not found

**Error**: `Failed to start Python process`

**Solutions**:
1. Install Python extension in VS Code
2. Select Python interpreter: Cmd+Shift+P → "Python: Select Interpreter"
3. Check Python path: `which python3`
4. Set explicit path in settings.json

### CDP connection failed

**Error**: `Failed to connect to CDP at http://localhost:9222`

**Solutions**:
1. Check Chrome is running with `--remote-debugging-port=9222`
2. Visit `http://localhost:9222/json` in browser (should show JSON)
3. Check firewall settings
4. Try different port in settings

### cli.py not found

**Error**: `CLI Script: .../cli.py` but file doesn't exist

**Solutions**:
1. Make sure you created `cli.py` in `webtestpilot/src/`
2. Check file permissions: `chmod +x cli.py`
3. Verify workspace structure

### Import errors in Python

**Error**: `ModuleNotFoundError: No module named 'playwright'`

**Solutions**:
1. Install dependencies: `pip install -e .` in webtestpilot directory
2. Check Python environment is activated
3. Verify `pyproject.toml` has correct dependencies

### No actions defined

**Warning**: `Test has no actions defined`

**Solutions**:
1. Open test in editor (double-click in tree view)
2. Add actions and expected results
3. Save the test
4. Try running again

## Advanced Usage

### Custom Test Execution

You can also use the Python agent directly in your own scripts:

```python
from playwright.sync_api import sync_playwright
from baml_client.types import Step
from executor.assertion_api import Session
from config import Config
from main import WebTestPilot

# Define your test steps
steps = [
    Step(condition="", action="Click login", expectation="Form appears"),
    Step(condition="", action="Type username", expectation="Username filled")
]

# Run with Playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    
    config = Config.load("config.yaml")
    session = Session(page, config)
    
    WebTestPilot.run(session, steps, assertion=True)
```

### Disable Assertions

For faster execution without verification:

```bash
python cli.py test.json --no-assertions
```

Or in code:
```python
WebTestPilot.run(session, steps, assertion=False)
```

### Custom Trace Locations

```bash
python cli.py test.json --trace-output /custom/path/trace.zip
```

## Future Enhancements

Potential improvements:

- [ ] Real-time test execution updates in webview
- [ ] Interactive pause/resume/step debugging
- [ ] Test recording from live browser
- [ ] Parallel test execution for folders
- [ ] Test result history and comparison
- [ ] Integration with CI/CD pipelines
- [ ] Test templates and snippets
- [ ] AI-powered test generation from descriptions

## Support

For issues or questions:
1. Check this documentation
2. Review logs in Output Channel
3. Check Python agent logs
4. Verify Chrome CDP connection
5. Create GitHub issue with logs

