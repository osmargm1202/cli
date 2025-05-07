from enum import Enum


class TipoFactura(str, Enum):
    NCFC = "NCFC"
    NCF = "NCF"
    NCG = "NCG"
    NCRE = "NCRE"
