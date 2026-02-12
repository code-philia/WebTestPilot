import logging
from enum import Enum
from typing import Any, Dict, Literal, List, Set, Mapping, Type, Tuple, Union, get_args, get_origin

from pydantic import BaseModel

from webtestpilot.assertion_api.oracle_execution.baml_types import (
    BamlClass, 
    BamlField,
    BamlType, 
    BamlEnum,
    BamlNode,
    UnionType,
    OptionalType,
    LiteralType,
    ArrayType,
    NamedType,
    MapType,
    PrimitiveType
)


logger = logging.getLogger(__name__)


class BamlTypeBuilder:
    def __init__(self):
        self._root: BamlType | None = None
        self._classes: dict[str, BamlClass] = {}
        self._enums: dict[str, BamlEnum] = {}
        self._visited: set[str] = set()


    def type(self) -> str:
        if self._root is None:
            raise ValueError("No type has been parsed yet")
        return self._root.render()


    def schema(self) -> str:
        nodes: List[BamlNode] = [*self._enums.values(), *self._classes.values()]
        return "\n\n".join(n.render() for n in nodes)


    def __call__(self, tp: Type) -> None:
        baml_type = self._parse(tp)
        if self._root is None:
            self._root = baml_type


    def _parse(self, tp: Type) -> BamlType:
        origin = get_origin(tp)
    
        if origin is Union:
            return self._parse_union(tp)
        
        if origin is Literal:
            return self._parse_literal(tp)
        
        if origin in (list, List, tuple, Tuple, set, Set):
            args = get_args(tp)
            inner = args[0] if args else str
            return ArrayType(self._parse(inner))
        
        if origin in (dict, Dict, Mapping):
            return self._parse_map(tp)
        
        if isinstance(tp, type) and issubclass(tp, Enum):
            self._parse_enum(tp)
            return NamedType(tp.__name__)
        
        if isinstance(tp, type) and issubclass(tp, BaseModel):
            self._parse_basemodel(tp)
            return NamedType(tp.__name__)
        
        if tp in (str, int, float, bool, type(None)):
            return PrimitiveType(tp)
        
        if tp in (list, tuple, set):
            logger.warning(f"Bare container: {tp}, defaulting to string[]")
            return ArrayType(PrimitiveType(str))
        
        if tp is dict:
            logger.warning(f"Bare container: {tp}, defaulting to map<string, string>")
            return MapType(key=PrimitiveType(str), value=PrimitiveType(str))

        logger.warning(f"Failed to resolve type: {tp}, defaulting to string")
        return PrimitiveType(str)


    def _parse_basemodel(self, basemodel: Type[BaseModel]) -> NamedType:
        if basemodel.__name__ in self._visited:
            return NamedType(basemodel.__name__)
        
        self._visited.add(basemodel.__name__)

        RESERVED = {"image"}
        fields: List[BamlField] = []
        for name, field in basemodel.model_fields.items():
            baml_type = self._parse(field.annotation)

            if name in RESERVED:
                logger.warning(f"{name} is a reserved keyword in BAML, changing to {name}_ (will convert back)")
                name = f"{name}_"

            fields.append(BamlField(name=name, type=baml_type, description=field.description))

        self._classes[basemodel.__name__] = BamlClass(
            name=basemodel.__name__, 
            fields=fields
        )
        return NamedType(basemodel.__name__)


    def _parse_enum(self, enum: Type[Enum]) -> NamedType:
        if enum.__name__ in self._visited:
            return NamedType(enum.__name__)
        
        self._visited.add(enum.__name__)
        
        self._enums[enum.__name__] = BamlEnum(
            name=enum.__name__, 
            values=[m.name for m in enum]
        )
        return NamedType(enum.__name__)
        

    def _parse_union(self, tp: Any) -> OptionalType | UnionType:
        args = get_args(tp)
        args_without_none = [a for a in args if a is not type(None)]

        if len(args_without_none) == 1 and type(None) in args:
            inner = self._parse(args_without_none[0])
            if isinstance(inner, (ArrayType, MapType)):
                return inner
            return OptionalType(inner)
        else:
            return UnionType([self._parse(a) for a in args])
        

    def _parse_literal(self, tp: Any) -> UnionType | LiteralType:
        literals = [LiteralType(v) for v in get_args(tp)]
        if len(literals) == 1:
            return literals[0]
        return UnionType(literals)
    

    def _parse_map(self, tp: Any) -> MapType:
        key_type, value_type = get_args(tp)

        if key_type is str:
            key_baml =  PrimitiveType(str)
        elif isinstance(key_type, type) and issubclass(key_type, Enum):
            self._parse_enum(key_type)
            key_baml = NamedType(key_type.__name__)
        elif get_origin(key_type) is Literal:
            key_baml = UnionType([LiteralType(v) for v in get_args(key_type)])
        else:
            raise TypeError(f"Invalid map key type: {key_type}")
    
        value_baml = self._parse(value_type)
        return MapType(key=key_baml, value=value_baml)


def python_to_baml_type(python_type: Union[Type[BaseModel], Type]) -> tuple[str, str]:
    """
    Convert a Python type or Pydantic BaseModel into its corresponding BAML representation.

    This function constructs a BAML type schema from a Python type, including
    Pydantic models with nested or recursive fields, enums, and standard primitives.

    Args:
        python_type (Union[Type[BaseModel], Type]):
            The Python type to convert. This can be:
                - A Pydantic BaseModel subclass, including models with nested or recursive fields.
                - A primitive type (int, str, bool, etc.), a typing.List, typing.Dict, or other supported type hints.

    Returns:
        tuple[str, str]:
            - schema: The full BAML schema definition for all parsed types, including any referenced classes or enums.
            - type: The BAML type string corresponding to the top-level `python_type` (e.g., `Comment[]` for `list[Comment]`).

    Example:
        >>> class Comment(BaseModel):
        ...     id: int
        ...     content: str
        ...     replies: list[Comment] = []
        >>> schema, type_str = python_to_baml_type(list[Comment])
        >>> print(type_str)
        Comment[]
        >>> print(schema)
        class Comment {
            id int
            content string
            replies Comment[]
        }
    """
    python_type_str = getattr(python_type, "__name__", str(python_type))
    logger.debug(f"Building BAML type from type: {python_type_str}")
    builder = BamlTypeBuilder()
    builder(python_type)
    return builder.schema(), builder.type()