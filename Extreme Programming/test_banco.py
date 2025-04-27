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

    with engine.connect() as connection:
        resultado = connection.execute(text("SELECT 1"))
        valor = resultado.scalar()  # pega o resultado

    assert valor == 1

def test_gerar_resumo_pivotado():
    dados = {
        'data_pagamento': ['2024-04-01', '2024-04-01', '2024-04-02'],
        'hasbeenpaid': [True, False, True],
        'valor': [100, 50, 200]
    }
    df = pd.DataFrame(dados)

    resultado = gerar_resumo_pivotado(df)

    esperado = pd.DataFrame({
        'data_pagamento': ['2024-04-01', '2024-04-02'],
        'Valor Dívida': [50.0, 0.0],
        'Valor Recebido': [100.0, 200.0]
    })

    # Compara os dois DataFrames
    pd.testing.assert_frame_equal(resultado, esperado)

def test_gerar_resumo_pivotado_faltando_coluna():
    df = pd.DataFrame({
        'data_pagamento': ['2024-04-01'],
        'valor': [100]
        # falta o hasbeenpaid
    })
    with pytest.raises(KeyError):
        gerar_resumo_pivotado(df)

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