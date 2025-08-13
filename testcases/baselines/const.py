from enum import Enum


class Method(str, Enum):
    lavague = "lavague"
    pinata = "pinata"
    naviqate = "naviqate"
    webtestpilot = "webtestpilot"


class Application(str, Enum):
    bookstack = "bookstack"
    invoiceninja = "invoiceninja"
    indico = "indico"
    prestashop = "prestashop"


class Provider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    mistral = "mistral"
    openrouter = "openrouter"
