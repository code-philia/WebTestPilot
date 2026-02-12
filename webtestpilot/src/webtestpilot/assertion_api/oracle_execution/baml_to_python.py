import logging
from typing import Type, Literal, Mapping, Dict, List, Tuple, Set, Union, Any, get_args, get_origin
from enum import Enum

from pydantic import BaseModel

from webtestpilot.assertion_api.oracle_execution.baml_types import RESERVED_KEYWORDS


logger = logging.getLogger(__name__)


def _restore_field_names(obj: Any) -> Any:
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k.endswith("_") and k[:-1] in RESERVED_KEYWORDS:
                new_key = k[:-1]
            else:
                new_key = k
            new[new_key] = _restore_field_names(v)
        return new

    if isinstance(obj, list):
        return [_restore_field_names(x) for x in obj]

    return obj


def _unwrap_baml_output(output: Any):
    """
    Unwrap BAML Output { data ... } containers.
    """
    if hasattr(output, "model_dump"):
        dumped = output.model_dump(by_alias=False)
        if isinstance(dumped, dict) and "data" in dumped:
            data = dumped.get("data", {})
            return _restore_field_names(data)
        
    return output


def _convert_primitive(tp: Type, value: Any):
    if value is None:
        return None
    try:
        return tp(value)
    except Exception:
        logger.warning(f"Failed to coerce value {value!r} to {tp}")
        return value
    

def _convert(schema: Type, value: Any):
    """
    Recursively convert `value` to match `schema`.
    """
    origin = get_origin(schema)
    args = get_args(schema)

    logger.debug(f"_convert: {schema=}, {value=}")

    # Optional[T]  (Union[T, None])
    if origin is Union and type(None) in args:
        inner = next(a for a in args if a is not type(None))
        return None if value is None else _convert(inner, value)

    # Union[T1, T2, ...]
    if origin is Union:
        for option in args:
            try:
                return _convert(option, value)
            except Exception:
                continue
        logger.warning(f"Failed to match Union {schema} for value {value!r}")
        return value

    # Literal[...]
    if origin is Literal:
        if value in args:
            return value
        logger.warning(f"Value {value!r} not in Literal{args}")
        return value

    # list[T]
    if origin in (list, List):
        (item_type,) = args
        if value is None:
            return []
        if not isinstance(value, list):
            logger.warning(f"Expected list for {schema}, got {type(value)}")
            return []
        return [_convert(item_type, item) for item in value]

    # tuple[T, ...] | Tuple[T1, T2, ...]
    if origin in (tuple, Tuple):
        if value is None:
            return ()
        if not isinstance(value, list):
            logger.warning(f"Expected list for {schema}, got {type(value)}")
            return ()

        # Tuple[T, ...]
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_convert(args[0], v) for v in value)

        # Tuple[T1, T2, ...]
        if len(args) == len(value):
            return tuple(_convert(t, v) for t, v in zip(args, value))

        logger.warning(f"Tuple length mismatch for {schema}")
        return tuple(value)
    
    # set[T]
    if origin in (set, Set):
        (item_type,) = args
        if value is None:
            return set()
        if not isinstance(value, list):
            logger.warning(f"Expected list for {schema}, got {type(value)}")
            return set()
        return set(_convert(item_type, item) for item in value)
    
    # dict[str, T] / Mapping[K, V]
    if origin in (dict, Dict, Mapping):
        key_type, value_type = args
        if not isinstance(value, dict):
            logger.warning(f"Expected dict for {schema}, got {type(value)}")
            return {}
        return {
            _convert(key_type, k): _convert(value_type, v)
            for k, v in value.items()
        }

    # Enum
    if isinstance(schema, type) and issubclass(schema, Enum):
        try:
            return schema[value]
        except Exception:
            try:
                return schema(value)
            except Exception:
                logger.warning(f"Failed to convert {value!r} to Enum {schema}")
                return value

    # Primitive types
    if schema in (int, float, str, bool, type(None)):
        return _convert_primitive(schema, value)

    # BaseModel
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        # LLM hallucination: list returned for singular schema
        if isinstance(value, list):
            logger.warning(
                "LLM returned list for singular schema %s; coercing",
                schema.__name__,
            )
            return [
                schema.model_validate(v, by_alias=False, by_name=True)
                for v in value
            ]

        if value is None:
            return None

        return schema.model_validate(value, by_alias=False, by_name=True)

    # Fallback
    logger.warning(f"Falling back to raw value for {schema}")
    return value


def baml_to_python_type(schema: Type, output: Any):
    """
    Convert BAML extraction output into a Python value matching the given schema.

    This function performs the inverse of `python_to_baml_type` by:
    - Unwrapping BAML `Output { data ... }` containers
    - Recursively converting collections and Pydantic models
    - Coercing primitive values to their declared Python types

    Args:
        schema:
            The expected Python type. This may be a primitive, a collection
            (e.g. list[T]), or a Pydantic BaseModel subclass.
        output:
            The raw output returned by a BAML extraction call.

    Returns:
        A Python value conforming to `schema`.
    """
    logger.debug(f"Converting BAML output to python type: {schema=}, {output=}")
    value = _unwrap_baml_output(output)
    return _convert(schema, value)