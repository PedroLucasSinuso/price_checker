import re
from typing import Optional


class Codigo:
    def __init__(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("Codigo deve ser uma string")
        normalizado = self.normalizar(valor)
        if not self.validar(normalizado):
            raise ValueError(f"Codigo invalido: {valor!r}")
        self._valor = normalizado
        self._tipo = self.detectar_tipo(normalizado)

    @property
    def valor(self) -> str:
        return self._valor

    @property
    def tipo(self) -> Optional[str]:
        return self._tipo

    @staticmethod
    def normalizar(codigo: str) -> str:
        codigo = codigo.strip()
        return re.sub(r"[\s-]", "", codigo)

    @classmethod
    def validar(cls, codigo: str) -> bool:
        return cls.detectar_tipo(codigo) is not None

    @classmethod
    def detectar_tipo(cls, codigo: str) -> Optional[str]:
        if cls.is_ean13(codigo):
            return "EAN13"
        if cls.is_ean12(codigo):
            return "EAN12"
        if cls.is_ean8(codigo):
            return "EAN8"
        if cls.is_plu6(codigo):
            return "PLU6"
        return None

    @classmethod
    def is_ean13(cls, codigo: str) -> bool:
        return cls._validar_ean(codigo, 13)

    @classmethod
    def is_ean12(cls, codigo: str) -> bool:
        return cls._validar_ean(codigo, 12)

    @classmethod
    def is_ean8(cls, codigo: str) -> bool:
        return cls._validar_ean(codigo, 8)

    @staticmethod
    def is_plu6(codigo: str) -> bool:
        return codigo.isdigit() and len(codigo) == 6

    @staticmethod
    def _validar_ean(codigo: str, tamanho: int) -> bool:
        if len(codigo) != tamanho or not codigo.isdigit():
            return False
        corpo = codigo[:-1]
        digito = int(codigo[-1])
        soma = 0
        peso = 3
        for ch in reversed(corpo):
            soma += int(ch) * peso
            peso = 1 if peso == 3 else 3
        calculado = (10 - (soma % 10)) % 10
        return calculado == digito
    
    def __repr__(self):
        return f"Codigo({self._valor})"
    
    def __eq__(self, other):
        if isinstance(other, Codigo):
            return self.valor == other.valor
        return False