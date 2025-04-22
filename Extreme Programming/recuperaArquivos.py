import pandas as pd
from datetime import datetime

def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r') as arquivo:
            return [linha.strip().split(';') for linha in arquivo]
    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado.")
        return []

def formatar_data(data_str):
    if len(data_str) == 7:
        data_str = '0' + data_str
    return f"{data_str[:2]}/{data_str[2:4]}/{data_str[4:]}"

def extrair_clientes(linhas_clientes):
    devedores = {}
    for cliente in linhas_clientes:
        id_cliente = cliente[0]
        nome_cliente = cliente[4]
        devedores[id_cliente] = [nome_cliente, 0.0, 0.0]  # [nome, dívida, pago]
    return devedores

def extrair_pagamentos(linhas_pagamentos, devedores):
    pagamentos_por_data = {}
    todas_datas = set()

    for pagamento in linhas_pagamentos:
        id_cliente = pagamento[0]
        data = formatar_data(pagamento[1])
        valor = float(pagamento[3])
        foi_pago = pagamento[4] == "t"

        # Atualiza valores no dicionário devedores
        if id_cliente in devedores:
            if foi_pago:
                devedores[id_cliente][2] += valor
            else:
                devedores[id_cliente][1] += valor

        # Coleta todas as datas
        todas_datas.add(data)

    # Organiza as datas em ordem crescente
    datas_ordenadas = sorted(
        [datetime.strptime(data, '%d/%m/%Y') for data in todas_datas]
    )
    datas_formatadas = [data.strftime('%d/%m/%Y') for data in datas_ordenadas]
    pagamentos_por_data = {data: [0.0, 0.0] for data in datas_formatadas}

    # Preenche os valores por data
    for pagamento in linhas_pagamentos:
        data = formatar_data(pagamento[1])
        valor = float(pagamento[3])
        foi_pago = pagamento[4] == "t"
        if data in pagamentos_por_data:
            if foi_pago:
                pagamentos_por_data[data][1] += valor
            else:
                pagamentos_por_data[data][0] += valor

    return devedores, pagamentos_por_data

def transformar_em_excel(devedores, pagamentos_por_data):
    # DataFrame das datas
    df_datas = pd.DataFrame(pagamentos_por_data.items(), columns=['Data', 'Valores'])
    df_datas[['Valor Dívida', 'Valor Pago']] = pd.DataFrame(df_datas['Valores'].tolist(), index=df_datas.index)
    df_datas.drop(columns='Valores', inplace=True)

    # DataFrame dos devedores
    df_devedores = pd.DataFrame(devedores.values(), columns=['Cliente', 'Valor Dívida', 'Valor Pago'])

    # Exporta para Excel
    with pd.ExcelWriter('Lista_Devedores.xlsx') as writer:
        df_datas.to_excel(writer, sheet_name='Datas', index=False)
        df_devedores.to_excel(writer, sheet_name='Devedores', index=False)


if __name__ == '__main__':
    caminho_clientes = "1428624292050_clientes.txt"
    caminho_pagamentos = "1428624292736_pagamentos.txt"

    linhas_clientes = ler_arquivo(caminho_clientes)
    linhas_pagamentos = ler_arquivo(caminho_pagamentos)

    devedores = extrair_clientes(linhas_clientes)
    devedores, pagamentos_por_data = extrair_pagamentos(linhas_pagamentos, devedores)

    transformar_em_excel(devedores, pagamentos_por_data)