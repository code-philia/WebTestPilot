from enum import Enum


class MethodEnum(str, Enum):
    lavague = "lavague"
    pinata = "pinata"
    naviqate = "naviqate"
    webtestpilot = "webtestpilot"


class ApplicationEnum(str, Enum):
    bookstack = "bookstack"
    invoiceninja = "invoiceninja"
    indico = "indico"
    prestashop = "prestashop"


class ProviderEnum(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    mistral = "mistral"
    openrouter = "openrouter"
