# VS Code ↔ Python Integration - Quick Start

## What Was Done

The VS Code extension now seamlessly integrates with the Python automation agent. When you click "Run Test" in VS Code, it:

1. ✅ Loads your test definition from JSON
2. ✅ Spawns the Python CLI with the test data
3. ✅ Streams live execution logs to VS Code Output
4. ✅ Saves Playwright traces for debugging
5. ✅ Shows success/failure notifications
6. ✅ Keeps the browser open for inspection

## Files Created/Modified

### New Files ✨

1. **`webtestpilot/src/cli.py`** - CLI interface for VS Code integration
   - Accepts test JSON file path as argument
   - Connects to browser via CDP
   - Executes test steps dynamically
   - Returns structured JSON results

2. **`INTEGRATION.md`** - Comprehensive integration documentation
   - Architecture overview with diagrams
   - Data flow explanation
   - Configuration guide
   - Troubleshooting section

3. **`validate_integration.py`** - Validation script
   - Checks all required files exist
   - Validates Python environment
   - Tests CLI functionality
   - Provides setup guidance

### Modified Files 🔧

1. **`webtestpilot/src/main.py`**
   - Refactored to remove hardcoded test steps
   - Now used as a library by cli.py
   - Added example usage in `__main__`
   - Better error handling

2. **`src/testRunnerPanel.ts`**
   - Added Python CLI integration
   - Spawns Python process with test data
   - Captures and displays output in real-time
   - Manages trace files
   - Shows progress notifications
   - Auto-detects Python interpreter path

## How It Works

```
User clicks "Run Test" in VS Code
         ↓
TestRunnerPanel loads test JSON
         ↓
Spawns: python cli.py test.json --cdp-endpoint http://localhost:9222
         ↓
cli.py:
  • Loads test.json
  • Converts actions → Steps
  • Connects to browser via CDP
  • Runs WebTestPilot.run(session, steps)
  • Saves trace.zip
  • Returns JSON result
         ↓
VS Code:
  • Captures output
  • Shows in Output Channel
  • Displays success/error notification
  • Offers to open trace file
```

## Setup Instructions

### 1. Start Chrome with Remote Debugging

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug

# Linux  
google-chrome --remote-debugging-port=9222

# Windows
chrome.exe --remote-debugging-port=9222
```

Verify it's working: Visit http://localhost:9222/json in a browser

### 2. Install Python Dependencies

```bash
cd webtestpilot
pip install -e .
```

Or with uv:
```bash
uv pip install -e .
```

### 3. Validate Setup

Run the validation script:

```bash
python validate_integration.py
```

This checks:
- ✅ All required files exist
- ✅ Python environment is configured
- ✅ Dependencies are installed
- ✅ CLI script is functional
- ✅ Test files are valid

### 4. Configure VS Code (Optional)

Create/edit `.vscode/settings.json`:

```json
{
  "webtestpilot.cdpEndpoint": "http://localhost:9222",
  "python.defaultInterpreterPath": "${workspaceFolder}/webtestpilot/.venv/bin/python"
}
```

## Usage

### From VS Code (Recommended)

1. Open WebTestPilot view in sidebar
2. Create or select a test
3. Right-click → "Run Test"
4. Watch execution in Output Channel
5. View results in notification

### From Command Line (For Testing)

```bash
# Navigate to webtestpilot directory
cd webtestpilot

# Run a test
python src/cli.py ../.webtestpilot/sample-gui-test.json \
  --config src/config.yaml \
  --cdp-endpoint http://localhost:9222 \
  --trace-output trace.zip \
  --json-output
```

## Test File Format

Your tests are stored as JSON in `.webtestpilot/`:

```json
{
  "id": "test-123",
  "name": "My Test",
  "url": "https://example.com",
  "actions": [
    {
      "action": "Click the login button",
      "expectedResult": "Login form appears"
    },
    {
      "action": "Type 'admin' in username field", 
      "expectedResult": "Username is filled"
    }
  ],
  "createdAt": "2025-10-15T00:00:00Z",
  "updatedAt": "2025-10-15T00:00:00Z"
}
```

The CLI automatically converts these actions into `Step` objects:

```python
Step(
    condition="",
    action="Click the login button",
    expectation="Login form appears"
)
```

## Output and Logs

### VS Code Output Channel

Open: View → Output → Select "WebTestPilot Test Runner"

Shows:
- Test execution progress
- Python agent logs
- Step-by-step results
- Error messages
- Trace file location

### Trace Files

Located in: `.webtestpilot/traces/{test-id}-trace.zip`

View with:
- Playwright Trace Viewer: `playwright show-trace trace.zip`
- VS Code: Click "View Trace" in notification

Contains:
- Screenshots of each step
- Network requests
- Console logs
- DOM snapshots
- Timing information

## Troubleshooting

### "Failed to connect to CDP"

❌ **Problem**: Python can't connect to browser

✅ **Solution**:
1. Make sure Chrome is running with `--remote-debugging-port=9222`
2. Test connection: `curl http://localhost:9222/json`
3. Check firewall settings
4. Verify CDP endpoint in settings

### "Failed to start Python process"

❌ **Problem**: VS Code can't find Python

✅ **Solution**:
1. Install Python extension in VS Code
2. Select interpreter: Cmd/Ctrl+Shift+P → "Python: Select Interpreter"
3. Or set path in settings.json: `"python.defaultInterpreterPath": "..."`

### "ModuleNotFoundError"

❌ **Problem**: Python dependencies not installed

✅ **Solution**:
```bash
cd webtestpilot
pip install -e .
```

### "No actions defined"

❌ **Problem**: Test has no actions

✅ **Solution**:
1. Double-click test in tree view
2. Add actions in editor
3. Save test
4. Run again

## Advanced Features

### Disable Assertions (Faster Execution)

```bash
python cli.py test.json --no-assertions
```

This only executes actions without verifying expectations.

### Custom Trace Location

```bash
python cli.py test.json --trace-output /custom/path/trace.zip
```

### Use as Python Library

```python
from playwright.sync_api import sync_playwright
from baml_client.types import Step
from executor.assertion_api import Session
from config import Config
from main import WebTestPilot

steps = [
    Step(condition="", action="Click button", expectation="Page loads")
]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0]
    
    config = Config.load("config.yaml")
    session = Session(page, config)
    
    WebTestPilot.run(session, steps, assertion=True)
```

## Next Steps

1. ✅ **Validate** - Run `python validate_integration.py`
2. ✅ **Start Chrome** - With CDP enabled on port 9222
3. ✅ **Create Test** - In VS Code WebTestPilot view
4. ✅ **Run Test** - Right-click → "Run Test"
5. ✅ **View Results** - Check Output Channel and notifications

## Example Output

```
============================================================
Running Test: Login Test
============================================================
Test File: .webtestpilot/test-123.json
URL: https://example.com/login
CDP Endpoint: http://localhost:9222
Actions: 2
============================================================

Python: /usr/bin/python3
CLI Script: webtestpilot/src/cli.py
Config: webtestpilot/src/config.yaml
Trace Output: .webtestpilot/traces/test-123-trace.zip

Executing Python agent...

2025-10-15 10:00:00 - INFO - Loaded test: Login Test
2025-10-15 10:00:00 - INFO - Connecting to browser at http://localhost:9222
2025-10-15 10:00:01 - INFO - Starting test execution with 2 steps
2025-10-15 10:00:05 - INFO - Test execution completed successfully

============================================================
✅ Test execution completed successfully!

Test Results:
  Success: true
  Steps Executed: 2

Trace saved to: .webtestpilot/traces/test-123-trace.zip
============================================================
```

## Support

For issues:
1. Check `INTEGRATION.md` for detailed docs
2. Run `validate_integration.py` to diagnose
3. Check Output Channel for logs
4. Verify Chrome CDP connection
5. Review trace files

## Architecture

See `INTEGRATION.md` for:
- Detailed architecture diagrams
- Data flow documentation
- Component descriptions
- Configuration reference
- Advanced usage patterns

---

**Happy Testing! 🚀**
