Para rodar os testes precisa escrever pytest -v no terminal.

Para rodar o banco, deve-se criar um banco no pg admin com o nome 'sistemas_pagamentos' e rodar o arquivo carregar_banco.py (deve-se colocar mesmo user e senha que tem no arquivo)

Criar um .env com o conteúdo:

USER = 'postgres'
PORT = '5432'
SCHEMA = 'sistema_pagamentos'
PW = 'ucs'
HOST = 'localhost'