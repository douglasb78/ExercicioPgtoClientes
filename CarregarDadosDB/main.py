#
# Só abrir o pgAdmin e criar um banco de dados chamado sistema_pagamentos, o resto é feito pelo script.
# Usuário "postgres" e senha "ucs"
#

import datetime
import psycopg2

dirClientes = "1428624292050_clientes.txt"
dirPagamentos = "1428624292736_pagamentos.txt"

class Cliente:
    def __init__(self, id, desconhecido1, desconhecido2, telefone, apelido):
        self.id = id
        self.desconhecido1 = desconhecido1
        self.desconhecido2 = desconhecido2
        self.telefone = telefone
        self.apelido = apelido
    def toString(self):
        return "[{0}] \"{1}\" \"{2}\"".format(self.id, self.apelido, self.telefone)

class Pagamento:
    def __init__(self, id_cliente, data_pagamento, desconhecido, valor, hasBeenPaid):
        self.id_cliente = id_cliente
        self.data_pagamento = data_pagamento
        self.desconhecido = desconhecido
        self.valor = valor
        self.hasBeenPaid = hasBeenPaid
    def toString(self):
        return "[{0}] \"{1}\" \"{2}\" \"{3}\"".format(self.id_cliente, self.data_pagamento, self.valor, self.hasBeenPaid)

def ler_clientes(arquivo: str):
    clientes = []
    try:
        arqClientes = open(arquivo, "r")
        # Extrair clientes
        counter = 0
        for linha in arqClientes:
            linha = linha.split(';')
            clientes.append(Cliente(linha[0], linha[1], linha[2], linha[3], linha[4]))
            print(clientes[counter].toString())
            counter += 1
    except:
        print("Não foi possível abrir o arquivo de clientes.")
        return []
    return clientes

def ler_pagamentos(arquivo:str):
    pagamentos = []
    try:
        arqPagamentos = open(arquivo, "r")
        # Extrair pagamentos
        counter = 0
        for linha in arqPagamentos:
            linha = linha.split(';')
            if len(linha[1]) == 7:
                linha[1] = '0' + linha[1]
            data_formatada = datetime.datetime.strptime(linha[1], '%d%m%Y')
            pagamentos.append(Pagamento(linha[0], data_formatada.strftime("%Y-%m-%d"), linha[2], linha[3], linha[4] == 't'))
            counter += 1
    except:
        print("Não foi possível abrir o arquivo de pagamentos.")
        return []
    return pagamentos

def main():
    # Fazer a leitura:
    clientes = ler_clientes(dirClientes)
    pagamentos = ler_pagamentos(dirPagamentos)

    # Conectar e criar tabelas:
    conn = psycopg2.connect("dbname=sistema_pagamentos user=postgres password=ucs")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS public.clientes (id BIGINT, desconhecido1 BIGINT, desconhecido2 BIGINT, telefone CHAR(24), apelido CHAR(128));")
    cur.execute("CREATE TABLE IF NOT EXISTS public.pagamentos (id_cliente BIGINT, data_pagamento DATE, desconhecido BIGINT, valor MONEY, hasBeenPaid boolean);")
    cur.execute("TRUNCATE clientes, pagamentos;")
    conn.commit()

    # Guardar clientes o banco de dados:
    for cliente in clientes:
        if not cliente.desconhecido1: cliente.desconhecido1 = -1
        if not cliente.desconhecido2: cliente.desconhecido2 = -1
        if not cliente.telefone: cliente.telefone = -1

        query = "INSERT INTO clientes (id, desconhecido1, desconhecido2, telefone, apelido)"
        query += "VALUES ({0}, {1}, {2}, {3}, '{4}');"
        query = query.format(cliente.id, cliente.desconhecido1, cliente.desconhecido2, cliente.telefone, cliente.apelido)
        print(query)
        cur.execute(query)
    conn.commit()
    # Guardar pagamentos no banco:
    # id_cliente, data_pagamento, desconhecido, valor, hasBeenPaid
    for pagamento in pagamentos:
        query = "INSERT INTO pagamentos (id_cliente, data_pagamento, desconhecido, valor, hasBeenPaid)"
        query += "VALUES({0}, '{1}', {2}, {3}, {4});"
        query = query.format(pagamento.id_cliente, pagamento.data_pagamento, pagamento.desconhecido, pagamento.valor, pagamento.hasBeenPaid)
        print(query)
        cur.execute(query)
    conn.commit()

if __name__ == "__main__":
    main()