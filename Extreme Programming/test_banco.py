import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, mock_open
from banco import gerar_excel_completo


@pytest.fixture
def mock_dfs():
    df_pagamentos = pd.DataFrame({
        'id_cliente': [1, 1, 2],
        'data_pagamento': ['2024-01-01', '2024-01-01', '2024-01-02'],
        'valor': [100.0, 200.0, 300.0],
        'hasbeenpaid': [True, False, True]
    })

    df_clientes = pd.DataFrame({
        'id': [1, 2],
        'apelido': ['João', 'Maria']
    })

    return df_clientes, df_pagamentos


@patch("banco.load_dotenv")
@patch("banco.create_engine")
@patch("banco.pd.read_sql_table")
@patch("pandas.ExcelWriter")  # Mock do ExcelWriter
@patch("builtins.open", new_callable=mock_open)  # Mock do open para interceptar a criação do arquivo
def test_gerar_excel_completo(mock_open, mock_writer, mock_read_sql_table, mock_dfs):
    df_clientes, df_pagamentos = mock_dfs

    # Mock do retorno de read_sql_table
    mock_read_sql_table.side_effect = [df_clientes, df_pagamentos]

    # Cria o MagicMock para o contexto do ExcelWriter
    mock_context = MagicMock()
    mock_writer.return_value.__enter__.return_value = mock_context  # Isso é o que o `with` retorna

    # Executa a função que irá chamar o ExcelWriter
    gerar_excel_completo()

    # Garante que o ExcelWriter foi chamado
    mock_writer.assert_called_once_with("relatorio_financeiro.xlsx")

    # Verifica que o to_excel foi chamado duas vezes (uma para cada sheet)
    assert mock_context.to_excel.call_count == 2

    # Checa os nomes das abas/sheets
    chamadas = [call.kwargs["sheet_name"] for call in mock_context.to_excel.call_args_list]
    assert "Resumo por Data" in chamadas
    assert "Clientes" in chamadas

    # Verifica se o arquivo foi "aberto"
    mock_open.assert_called_once_with("relatorio_financeiro.xlsx", "wb")
