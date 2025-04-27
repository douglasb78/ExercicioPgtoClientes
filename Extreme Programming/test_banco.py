import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, mock_open
from banco import gerar_excel_completo, gerar_resumo_pivotado, gerar_resumo_por_cliente
from dotenv import load_dotenv
from sqlalchemy import create_engine,text
import os

def test_conectar_banco():
    load_dotenv()
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('USER')}:{os.getenv('PW')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('SCHEMA')}"
    )

    # Testa abrindo uma conexão real
    with engine.connect() as connection:
        resultado = connection.execute(text("SELECT 1"))
        valor = resultado.scalar()  # pega o resultado

    # Agora sim você pode fazer o assert
    assert valor == 1


def test_gerar_resumo_pivotado():
    # Arrange: monta o DataFrame de entrada
    dados = {
        'data_pagamento': ['2024-04-01', '2024-04-01', '2024-04-02'],
        'hasbeenpaid': [True, False, True],
        'valor': [100, 50, 200]
    }
    df = pd.DataFrame(dados)

    # Act: chama a função
    resultado = gerar_resumo_pivotado(df)

    # Expected: cria manualmente o DataFrame esperado
    esperado = pd.DataFrame({
        'data_pagamento': ['2024-04-01', '2024-04-02'],
        'Valor Dívida': [50.0, 0.0],
        'Valor Recebido': [100.0, 200.0]
    })

    # Assert: compara os dois DataFrames
    pd.testing.assert_frame_equal(resultado, esperado)

def test_gerar_resumo_por_cliente():
    df_pagamentos = pd.DataFrame({
        'id_cliente': [1, 2, 1, 3],
        'hasbeenpaid': [True, False, False, True],
        'valor': [100, 50, 30, 70]
    })
    df_clientes = pd.DataFrame({
        'id': [1, 2, 3],
        'apelido': ['João', 'Maria', 'Carlos']
    })

    resultado = gerar_resumo_por_cliente(df_pagamentos, df_clientes)

    esperado = pd.DataFrame({
        'apelido': ['Carlos', 'João', 'Maria'],
        'Valor Dívida': [0.0, 30.0, 50.0],
        'Valor Pago': [70.0, 100.0, 0.0]
    })

    # Essas linhas são pq o assert_frame_equal do pandas não deixa comparar se não for o mesmo tipo
    resultado['Valor Dívida'] = resultado['Valor Dívida'].astype(float)
    resultado['Valor Pago'] = resultado['Valor Pago'].astype(float)

    esperado['Valor Dívida'] = esperado['Valor Dívida'].astype(float)
    esperado['Valor Pago'] = esperado['Valor Pago'].astype(float)

    pd.testing.assert_frame_equal( # O drop=True serve pra não colocar o índice antigo como uma coluna do df
        resultado.sort_values('apelido').reset_index(drop=True),
        esperado.sort_values('apelido').reset_index(drop=True)
    )




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


