#!/usr/bin/env python3
"""
CLI interface for WebTestPilot - called from VS Code extension
Accepts test data via JSON and runs the automation agent
"""
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright
from baml_client.types import Step

from executor.assertion_api import Session
from config import Config
from main import WebTestPilot


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_test_action_to_step(action: dict[str, Any]) -> Step:
    """
    Convert a test action from VS Code format to WebTestPilot Step format
    
    VS Code format:
    {
        "action": "Click the login button",
        "expectedResult": "Login form appears"
    }
    
    WebTestPilot Step format:
    Step(condition="", action="...", expectation="...")
    """
    return Step(
        condition="",
        action=action.get("action", ""),
        expectation=action.get("expectedResult", "")
    )


def run_test_from_file(test_file_path: str, config_path: str, cdp_endpoint: str, 
                       enable_assertions: bool = True, output_trace: str = "trace.zip") -> dict[str, Any]:
    """
    Run a test from a JSON file
    
    Args:
        test_file_path: Path to the test JSON file
        config_path: Path to the config.yaml file
        cdp_endpoint: CDP endpoint URL (e.g., http://localhost:9222)
        enable_assertions: Whether to verify expectations/postconditions
        output_trace: Path to save the Playwright trace file
        
    Returns:
        Dict with test results including success status and any errors
    """
    try:
        # Load test data
        with open(test_file_path, 'r') as f:
            test_data = json.load(f)
        
        logger.info(f"Loaded test: {test_data.get('name', 'Unnamed Test')}")
        logger.info(f"Test URL: {test_data.get('url', 'No URL specified')}")
        
        # Convert test actions to Steps
        actions = test_data.get('actions', [])
        if not actions:
            logger.warning("No actions found in test file")
            return {
                "success": False,
                "error": "No actions defined in test",
                "test_name": test_data.get('name')
            }
        
        test_steps = [parse_test_action_to_step(action) for action in actions]
        logger.info(f"Converted {len(test_steps)} actions to test steps")
        
        # Load configuration
        config = Config.load(config_path)
        
        # Run the test with Playwright
        result = {
            "success": True,
            "test_name": test_data.get('name'),
            "url": test_data.get('url'),
            "steps_executed": 0,
            "errors": []
        }
        
        with sync_playwright() as p:
            logger.info(f"Connecting to browser at {cdp_endpoint}")
            
            # Connect to existing browser via CDP
            browser = p.chromium.connect_over_cdp(cdp_endpoint)
            
            # Get or create context
            context = (
                browser.contexts[0]
                if browser.contexts
                else browser.new_context()
            )
            
            # Start tracing
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            
            # Get or create page
            page = context.pages[0] if context.pages else context.new_page()
            
            # Navigate to test URL if specified
            test_url = test_data.get('url')
            if test_url:
                logger.info(f"Navigating to {test_url}")
                page.goto(test_url)
            
            # Create session
            session = Session(page, config)
            
            try:
                # Run the test
                logger.info(f"Starting test execution with {len(test_steps)} steps")
                WebTestPilot.run(session, test_steps, assertion=enable_assertions)
                result["steps_executed"] = len(test_steps)
                logger.info("Test execution completed successfully")
                
            except Exception as e:
                logger.error(f"Test execution failed: {str(e)}", exc_info=True)
                result["success"] = False
                result["errors"].append(str(e))
            
            finally:
                # Stop tracing and save
                context.tracing.stop(path=output_trace)
                logger.info(f"Trace saved to {output_trace}")
                
                # Don't close browser/context - keep it open for user to inspect
                # context.close()
                # browser.close()
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Test file not found: {test_file_path}")
        return {
            "success": False,
            "error": f"Test file not found: {str(e)}"
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test file: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='WebTestPilot CLI - Run automated web tests from VS Code'
    )
    
    parser.add_argument(
        'test_file',
        type=str,
        help='Path to the test JSON file'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config.yaml file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--cdp-endpoint',
        type=str,
        default='http://localhost:9222',
        help='CDP endpoint URL (default: http://localhost:9222)'
    )
    
    parser.add_argument(
        '--no-assertions',
        action='store_true',
        help='Disable assertion verification (only execute actions)'
    )
    
    parser.add_argument(
        '--trace-output',
        type=str,
        default='trace.zip',
        help='Output path for Playwright trace (default: trace.zip)'
    )
    
    parser.add_argument(
        '--json-output',
        action='store_true',
        help='Output results as JSON instead of human-readable format'
    )
    
    args = parser.parse_args()
    
    # Run the test
    result = run_test_from_file(
        test_file_path=args.test_file,
        config_path=args.config,
        cdp_endpoint=args.cdp_endpoint,
        enable_assertions=not args.no_assertions,
        output_trace=args.trace_output
    )
    
    # Output results
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Test: {result.get('test_name', 'Unknown')}")
        print(f"{'='*60}")
        
        if result["success"]:
            print(f"✅ Test PASSED")
            print(f"   Steps executed: {result.get('steps_executed', 0)}")
        else:
            print(f"❌ Test FAILED")
            if result.get('errors'):
                print(f"   Errors:")
                for error in result['errors']:
                    print(f"   - {error}")
        
        print(f"\nTrace saved to: {args.trace_output}")
        print(f"{'='*60}\n")
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
