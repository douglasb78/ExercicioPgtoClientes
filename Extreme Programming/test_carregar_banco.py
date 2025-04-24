from unittest.mock import mock_open, patch
from carregar_banco import ler_clientes, Cliente

def test_ler_clientes_funciona():
    mock_data = "1;1234;5678;123456789;João\n2;2345;6789;987654321;Maria\n"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        clientes = ler_clientes("clientes.txt")

        assert len(clientes) == 2
        assert clientes[0].id == "1"
        assert clientes[0].apelido.strip() == "João"
        assert clientes[1].id == "2"
        assert clientes[1].apelido.strip() == "Maria"