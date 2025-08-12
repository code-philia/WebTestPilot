"""
Usage:
    python evaluate.py --method lavague --application bookstack
    python evaluate.py --method pinata --application bookstack --provider openai
    python evaluate.py --method naviqate --application bookstack
"""

import argparse
import sys
from pathlib import Path

from lavague.lavague_runner import LavagueTestRunner
from naviqate.naviqate_runner import NaviqateTestRunner
from pinata.pinata_runner import PinataTestRunner

# Add testcases directory to path
sys.path.append(str(Path(__file__).parent.parent))


def get_runner_class(method: str):
    """Get the appropriate runner class based on method."""
    if method == "lavague":
        return LavagueTestRunner
    elif method == "pinata":
        return PinataTestRunner
    elif method == "naviqate":
        return NaviqateTestRunner
    else:
        raise ValueError(f"Unknown method: {method}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run test cases using different agent implementations"
    )

    # Required arguments
    parser.add_argument(
        "--method",
        type=str,
        required=True,
        choices=["lavague", "pinata", "naviqate"],
        help="The test method/agent to use for running tests",
    )

    parser.add_argument(
        "--application",
        type=str,
        required=True,
        choices=["bookstack", "invoiceninja", "indico", "prestashop"],
        help="The application to test",
    )

    # Optional arguments
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "anthropic", "google", "mistral", "openrouter"],
        help="LLM provider (for pinata method)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode",
    )

    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Filter pattern for test case files (e.g., 'book_create')",
    )

    parser.add_argument(
        "--max-steps", type=int, default=1, help="Maximum steps for naviqate method"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory for results",
    )

    parser.add_argument(
        "--test-dir", type=str, default=None, help="Custom test cases directory"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def main():
    """Main entry point for the evaluation script."""
    args = parse_arguments()

    # Set up paths
    base_dir = Path(__file__).parent.parent  # testcases directory

    # Test cases directory
    if args.test_dir:
        test_case_path = Path(args.test_dir)
    else:
        test_case_path = base_dir / "eval_data" / "test_cases" / args.application

    # Output directory
    if args.output_dir:
        output_path = Path(args.output_dir) / f"{args.method}_{args.application}.json"
    else:
        output_path = (
            base_dir
            / "eval_data"
            / "results"
            / args.method
            / f"{args.application}.json"
        )

    # Print configuration
    print("=" * 60)
    print("TEST EXECUTION CONFIGURATION")
    print("=" * 60)
    print(f"Method: {args.method}")
    print(f"Application: {args.application}")
    print(f"Test cases: {test_case_path}")
    print(f"Output: {output_path}")
    print(f"Headless: {args.headless}")

    if args.method == "pinata":
        print(f"LLM Provider: {args.provider}")
    elif args.method == "naviqate":
        print(f"Max Steps: {args.max_steps}")

    if args.filter:
        print(f"Filter: {args.filter}")

    print("=" * 60)
    print()

    # Verify test cases directory exists
    if not test_case_path.exists():
        print(f"Error: Test cases directory does not exist: {test_case_path}")
        sys.exit(1)

    # Get the appropriate runner class
    try:
        RunnerClass = get_runner_class(args.method)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Prepare runner kwargs
    runner_kwargs = {
        "test_case_path": str(test_case_path),
        "test_output_path": str(output_path),
        "application": args.application,
        "headless": args.headless,
    }

    # Add method-specific parameters
    if args.method == "pinata":
        runner_kwargs["provider"] = args.provider
        runner_kwargs["save_screenshot"] = True
        runner_kwargs["tracer"] = True
    elif args.method == "naviqate":
        runner_kwargs["max_steps"] = args.max_steps
        runner_kwargs["abstracted"] = False

    # Create and run the test runner
    try:
        print(f"Initializing {args.method} test runner...")
        runner = RunnerClass(**runner_kwargs)

        print("Starting test execution...")
        results = runner.run_test_cases(filter_pattern=args.filter)

        # Exit with appropriate code
        if results.success_rate == 1.0:
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print(
                f"\n✗ {len([r for r in results.results if not r.success])} tests failed"
            )
            sys.exit(1)
    except Exception as e:
        print(f"Error during test execution: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
