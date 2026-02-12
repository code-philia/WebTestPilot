from enum import Enum


class Viewport:
    WIDTH = 1280
    HEIGHT = 720


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