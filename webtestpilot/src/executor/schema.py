from typing import Any

from pydantic import BaseModel


def extract_models_and_schemas(code: str) -> dict[str, Any]:
    """
    Execute a Python code snippet, find all Pydantic BaseModel subclasses it defines,
    and return their JSON Schemas.

    Args:
        code (str): A string containing valid Python code that may define
            one or more Pydantic models.

    Returns:
        dict[str, Any]: A dictionary mapping each discovered model's name
        to its corresponding JSON Schema (as a Python dictionary).
    """
    # Run code to get classes in namespace
    namespace = {}
    exec(code, namespace)

    # Find all BaseModel subclasses in the namespace
    models = {
        name: obj
        for name, obj in namespace.items()
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel
    }

    # Extract schemas
    schemas = {name: model.model_json_schema() for name, model in models.items()}
    return schemas
