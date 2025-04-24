import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


def gerar_resumo_pivotado(df_pagamentos):
    resumo = df_pagamentos.groupby(['data_pagamento', 'hasbeenpaid'])['valor'].sum().reset_index()
    resumo_pivotado = resumo.pivot(index='data_pagamento', columns='hasbeenpaid', values='valor').fillna(0)

    if True in resumo_pivotado.columns and False in resumo_pivotado.columns:
        resumo_pivotado.columns = ['Valor Dívida', 'Valor Recebido']
    elif True in resumo_pivotado.columns:
        resumo_pivotado.columns = ['Valor Recebido']
    elif False in resumo_pivotado.columns:
        resumo_pivotado.columns = ['Valor Dívida']

    return resumo_pivotado.reset_index()

def gerar_resumo_por_cliente(df_pagamentos, df_clientes):
    df_join = df_pagamentos.merge(df_clientes, left_on='id_cliente', right_on='id', how='left')

    return df_join.groupby('apelido').apply(
        lambda x: pd.Series({
            'Valor Dívida': x.loc[x['hasbeenpaid'] == False, 'valor'].sum(),
            'Valor Pago': x.loc[x['hasbeenpaid'] == True, 'valor'].sum()
        })
    ).reset_index()

def gerar_excel_completo():
    load_dotenv()
    engine = create_engine(f"postgresql+psycopg2://{os.getenv('USER')}:{os.getenv('PW')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('SCHEMA')}")

    df_clientes = pd.read_sql_table('clientes', con=engine)
    df_pagamentos = pd.read_sql_table('pagamentos', con=engine)

    # Sheet 1
    resumo_pivotado = gerar_resumo_pivotado(df_pagamentos)

    # Sheet 2
    df_clientes_resumo = gerar_resumo_por_cliente(df_pagamentos, df_clientes)

    # Exportar pro Excel
    with pd.ExcelWriter("relatorio_financeiro.xlsx") as writer:
        resumo_pivotado.to_excel(writer, sheet_name="Resumo por Data", index=False)
        df_clientes_resumo.to_excel(writer, sheet_name="Clientes", index=False)


if __name__ == '__main__':
    gerar_excel_completo()