from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DOMCandidate:
    label: int
    xpath: str
    tag: str = ""
    role: str = ""
    type: str = ""
    text: str = ""
    aria_label: str = ""
    title: str = ""
    placeholder: str = ""
    name: str = ""
    value: str = ""
    href: str = ""
    context: str = ""
    selector_hint: str = ""
    rect: dict[str, Any] = field(default_factory=dict)
    disabled: bool = False
    score: float = 0.0

    def searchable_text(self) -> str:
        return " ".join(
            str(x)
            for x in [
                self.role,
                self.type,
                self.text,
                self.aria_label,
                self.title,
                self.placeholder,
                self.name,
                self.value,
                self.href,
                self.context,
                self.selector_hint,
            ]
            if x
        )