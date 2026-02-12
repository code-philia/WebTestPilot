from typing import Optional, Union
from dataclasses import dataclass, field


RESERVED_KEYWORDS = {"image"}


class BamlNode:
    def render(self) -> str:
        raise NotImplementedError
    

# BAML Types
# --------------------------------

@dataclass(frozen=True)
class BamlType(BamlNode):
    pass


@dataclass(frozen=True)
class PrimitiveType(BamlType):
    tp: Union[str, int, float, bool, type[None]]

    def render(self) -> str:
        PRIMITIVES = {
            str: "string",
            int: "int",
            float: "float",
            bool: "bool",
            type(None): "null",
        }
        return PRIMITIVES.get(self.tp)
    

@dataclass(frozen=True)
class LiteralType(BamlType):
    value: Union[str, int, float, bool]

    def render(self) -> str:
        if isinstance(self.value, str):
            return f'"{self.value}"'
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)
    
    
@dataclass(frozen=True)
class OptionalType(BamlType):
    inner: BamlType

    def render(self) -> str:
        return f"{self.inner.render()}?"
    

@dataclass(frozen=True)
class ArrayType(BamlType):
    inner: BamlType

    def render(self) -> str:
        return f"{self.inner.render()}[]"
    

@dataclass(frozen=True)
class MapType(BamlType):
    key: BamlType
    value: BamlType

    def render(self) -> str:
        return f"map<{self.key.render()}, {self.value.render()}>"


@dataclass(frozen=True)
class UnionType(BamlType):
    options: list[BamlType]

    def render(self) -> str:
        if len(self.options) == 1:
            return self.options[0].render()
        return " | ".join(o.render() for o in self.options)
        

@dataclass(frozen=True)
class NamedType(BamlType):
    name: str

    def render(self) -> str:
        return self.name
    

@dataclass
class BamlField(BamlNode):
    name: str
    type: BamlType
    description: Optional[str] = None

    def render(self) -> str:
        line = f"  {self.name} {self.type.render()}"
        if self.description:
            line += f' @description("{self.description}")'
        return line
    

@dataclass
class BamlEnum(BamlNode):
    name: str
    values: list[str]

    def render(self) -> str:
        body = "\n".join(f"  {v}" for v in self.values)
        return f"enum {self.name} {{\n{body}\n}}"


@dataclass
class BamlClass(BamlNode):
    name: str
    fields: list[BamlField] = field(default_factory=list)

    def render(self) -> str:
        body = "\n".join(f.render() for f in self.fields)
        return f"class {self.name} {{\n{body}\n}}"