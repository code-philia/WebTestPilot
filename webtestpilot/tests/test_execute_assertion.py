import pytest
from unittest.mock import Mock, MagicMock
from typing import Any
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from executor.assertion_api import execute_assertion


class TestExecuteAssertion:
    """Test cases for the execute_assertion function."""

    @pytest.mark.parametrize("function_name", ["precondition", "postcondition"])
    def test_successful_assertion(self, mock_session, function_name):
        """Test successful execution of both precondition and postcondition assertions."""
        response = f"""
        ```python
        def {function_name}(session):
            return True
        ```
        """

        success, message = execute_assertion(response, mock_session)

        assert success is True
        assert message == "Success."

    @pytest.mark.parametrize(
        "return_value,expected_success,expected_message",
        [
            ("None", True, "Success."),
            ("False", False, "Assertion failed without message"),
            ("'Error message'", False, "Error message"),
        ],
    )
    def test_assertion_return_values(
        self, mock_session, return_value, expected_success, expected_message
    ):
        """Test assertion function with different return values."""
        response = f"""
        ```python
        def precondition(session):
            return {return_value}
        ```
        """

        success, message = execute_assertion(response, mock_session)

        assert success is expected_success
        if expected_success:
            assert message == expected_message
        else:
            assert expected_message in message

    def test_assertion_raising_assertion_error(self, mock_session):
        """Test assertion function that raises an AssertionError."""
        response = """
        ```python
        def precondition(session):
            assert False, "Custom error message"
        ```
        """

        success, message = execute_assertion(response, mock_session)

        assert success is False
        assert "Custom error message" in message
        assert "Variable trace:" in message

    @pytest.mark.parametrize(
        "response,expected_error",
        [
            (
                "No code blocks here",
                "No callable 'precondition' or 'postcondition' function found",
            ),
            (
                """
        ```python
        def some_other_function(session):
            return True
        ```
        """,
                "No callable 'precondition' or 'postcondition' function found",
            ),
        ],
    )
    def test_missing_code_or_function(self, mock_session, response, expected_error):
        """Test responses with missing code blocks or assertion functions."""
        success, message = execute_assertion(response, mock_session)

        assert success is False
        assert expected_error in message

    def test_multiple_code_blocks(self, mock_session):
        """Test response with multiple Python code blocks."""
        response = """
        ```python
        def helper_function():
            return "helper"
        ```
        
        ```python
        def precondition(session):
            helper_function()
            return True
        ```
        """

        success, message = execute_assertion(response, mock_session)

        assert success is True
        assert message == "Success."

    def test_assertion_with_session_access(self, mock_session):
        """Test assertion function that accesses session properties."""
        mock_session.page.url = "https://example.com/test"

        response = """
        ```python
        def precondition(session):
            return "test" in session.page.url
        ```
        """

        success, message = execute_assertion(response, mock_session)

        assert success is True
        assert message == "Success."

    @pytest.mark.parametrize(
        "import_type,code",
        [
            (
                "pydantic",
                """
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
        
        def precondition(session):
            model = TestModel(name="test")
            return model.name == "test"
        """,
            ),
            (
                "typing",
                """
        from typing import List, Dict
        
        def precondition(session):
            data: List[str] = ["a", "b", "c"]
            mapping: Dict[str, int] = {"a": 1, "b": 2}
            return len(data) == 3 and len(mapping) == 2
        """,
            ),
        ],
    )
    def test_assertion_with_imports(self, mock_session, import_type, code):
        """Test assertion function that uses various imports."""
        response = f"""
        ```python
        {code}
        ```
        """

        success, message = execute_assertion(response, mock_session)

        assert success is True
        assert message == "Success."

    @pytest.mark.parametrize(
        "error_type,expected_exception",
        [
            ("syntax", SyntaxError),
            ("runtime", ValueError),
        ],
    )
    def test_error_handling(self, mock_session, error_type, expected_exception):
        """Test handling of syntax and runtime errors in assertion code."""
        if error_type == "syntax":
            response = """
            ```python
            def precondition(session):
                return True
            # Missing closing parenthesis
            if True:
                print("test"
            ```
            """
        else:  # runtime
            response = """
            ```python
            def precondition(session):
                raise ValueError("Runtime error occurred")
            ```
            """

        if error_type == "syntax":
            with pytest.raises(expected_exception):
                execute_assertion(response, mock_session)
        else:
            with pytest.raises(expected_exception, match="Runtime error occurred"):
                execute_assertion(response, mock_session)
