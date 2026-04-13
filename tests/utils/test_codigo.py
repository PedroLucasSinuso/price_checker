from price_checker.utils.codigo import Codigo
import pytest

def test_codigo_valido():
    c = Codigo("123456")
    assert c.valor == "123456"
    assert c.tipo == "PLU6"

def test_codigo_invalido():
    with pytest.raises(ValueError):
        Codigo("abc")

def test_normalizacao():
    c = Codigo(" 123-456 ")
    assert c.valor == "123456"