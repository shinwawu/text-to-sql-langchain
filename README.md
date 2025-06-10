# text-to-sql-langchain

Este Programa foi feito na matéria ICSB30 - S01 - 2025-1 - Introdução A Banco De Dados da UTFPR. Ministrada pelo professor LEANDRO BATISTA DE ALMEIDA da UTFPR-CT.

O programa tem o objetivo conectar um banco de dados MySQL e/ou PostgreSQL, e uma LLM(DeepSeek) pelo Openrouter. A LLM retorna uma query ao usuário inserir um comando na linguagem natural pela interface e o programa executa essa query retornando a visualização dessa query igual ao modelo relacional (colunas/tabelas)

Projeto foi feito em Python3.

Como executar:

Tenha uma Chave da API do site Openrouter e insira nas ""da linha 242 os.environ["OPENROUTER_API_KEY"] = "" #insira a chave do Openrouter aqui

