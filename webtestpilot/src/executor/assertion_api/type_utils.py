"""
Centralized type handling utilities for extract methods.
"""

import logging
from typing import get_args, get_origin

from baml_client.types import ExtractedData
from pydantic import BaseModel

PRIMITIVE_TYPES = (int, float, str, bool, type(None))
COLLECTION_TYPES = (list,)
logger = logging.getLogger(__name__)


def is_primitive_type(python_type: type) -> bool:
    """Check if a type is a supported primitive."""
    return python_type in PRIMITIVE_TYPES


def is_collection_type(python_type: type) -> bool:
    """Check if a type is a supported collection."""
    return python_type in COLLECTION_TYPES


def is_basemodel_type(python_type: type) -> bool:
    """Check if a type is a BaseModel subclass."""
    try:
        return isinstance(python_type, type) and issubclass(python_type, BaseModel)
    except TypeError:
        return False


def convert_extracted_data(
    schema: ExtractedData, output: ExtractedData
) -> ExtractedData:
    """
    Convert extracted data to appropriate Python type.

    Args:
        schema: The target schema type
        extracted_data: Raw data from BAML extraction

    Returns:
        Converted data matching schema type
    """
    logger.debug(f"Converting extracted data for schema: {schema}, output: {output}")

    # Handle generic types like list[BaseModel]
    origin = get_origin(schema)
    logger.debug(f"Origin: {origin}")
    if origin is list:
        args = get_args(schema)
        logger.debug(f"List args: {args}, ")
        if args and is_basemodel_type(args[0]):
            # Handle list[BaseModel]
            model_class = args[0]
            extracted_data = output.model_dump().get("schema", [])
            return [model_class.model_validate(item) for item in extracted_data]
        else:
            return list(output) if output else []

    if is_primitive_type(schema):
        if schema is str:
            return str(output)
        elif schema is int:
            return int(output)
        elif schema is float:
            return float(output)
        elif schema is bool:
            return bool(output)
        elif schema is type(None):
            return None
    elif is_collection_type(schema):
        if schema is list:
            return list(output) if output else []
    elif is_basemodel_type(schema):
        # NOTE: Sometimes model does not annotate as list[Type], but just Type
        # And it returns a list at the end :).
        if isinstance(output, list):
            res = []
            for item in output:
                extracted_data = item.model_dump().get("schema", {})
                res.append(schema.model_validate(extracted_data))
            return res
        else:
            extracted_data = output.model_dump().get("schema", {})
            logger.debug(
                f"Checking type of extracted data {type(extracted_data)} {extracted_data} {schema=}"
            )
            return schema.model_validate(extracted_data)

    return output
