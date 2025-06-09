# -*- coding: utf-8 -*-

import mysql.connector as sql
import psycopg2 as psql
import tkinter as tk
from tkinter import ttk
import os
import re
#biblioteca utilizadas pela langchain para llm,sql e prompts
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate


#define template para a resposta da LLM
class SQLQuery(BaseModel):
    sql: str = Field(description="Consulta SQL gerada para responder a pergunta do usuario")

def conectarsql(host, usuario, senha, bancodedados):
    return sql.connect(host=host, user=usuario, password=senha, database=bancodedados)

def conectarpsql(host, usuario, senha, bancodedados):
    conn = psql.connect(host=host, user=usuario, password=senha, dbname=bancodedados)
    conn.set_client_encoding('UTF8')
    return conn

class Interface:
    def __init__(self, Interface):
        self.Interface = Interface
        self.Interface.title("Ferramenta text to sql")
        self.Interface.geometry("1024x894")
        self.Interface.configure(bg="#151515")

        #criacao de frames para inserir elementos graficos do tkinter
        self.frame_principal = tk.Frame(self.Interface, bg="#151515")
        self.frame_principal.pack(fill="both", expand=True)

        self.frame_esquerda = tk.Frame(self.frame_principal, bg="#151515")
        self.frame_esquerda.pack(side="left", fill="y", padx=20, pady=20)

        self.frame_direita = tk.Frame(self.frame_principal, bg="#151515")
        self.frame_direita.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        #campos e elementos visuais 
        self.escolher = tk.Label(self.frame_esquerda, text="Escolha entre mysql ou psql", fg="white", bg="#151515")
        self.escolher.pack(pady=5)
        self.entradaescolha = tk.Entry(self.frame_esquerda, width=30)
        self.entradaescolha.pack(pady=5)

        self.host = tk.Label(self.frame_esquerda, text="Digite o host", fg="white", bg="#151515")
        self.host.pack(pady=5)
        self.entradahost = tk.Entry(self.frame_esquerda, width=30)
        self.entradahost.pack(pady=5)

        self.usuario = tk.Label(self.frame_esquerda, text="Digite o usuario", fg="white", bg="#151515")
        self.usuario.pack(pady=5)
        self.entradausuario = tk.Entry(self.frame_esquerda, width=30)
        self.entradausuario.pack(pady=5)

        self.senha = tk.Label(self.frame_esquerda, text="Digite a senha", fg="white", bg="#151515")
        self.senha.pack(pady=5)
        self.entradasenha = tk.Entry(self.frame_esquerda, width=30, show="*")
        self.entradasenha.pack(pady=5)

        self.bancodedados = tk.Label(self.frame_esquerda, text="Digite o banco de dados", fg="white", bg="#151515")
        self.bancodedados.pack(pady=5)
        self.entradabanco = tk.Entry(self.frame_esquerda, width=30)
        self.entradabanco.pack(pady=5)

        
        self.salvarbotao = tk.Button(self.frame_esquerda, text="Salvar", command=self.salvardados)
        self.salvarbotao.pack(pady=10)

        self.tabelas = tk.Button(self.frame_esquerda, text="Mostrar Tabelas", command=self.chamar_mostrartabelas)
        self.tabelas.pack(pady=10)

        self.query = tk.Label(self.frame_esquerda, text="Insira a comando em linguagem natural", fg="white", bg="#151515")
        self.query.pack(pady=11)
        self.entradaquery = tk.Entry(self.frame_esquerda, width=30)
        self.entradaquery.pack(pady=11)

        self.querybotao = tk.Button(self.frame_esquerda, text="Query", command=self.realizarquery)
        self.querybotao.pack(pady=12)

        self.msg = tk.Label(self.frame_esquerda, text="", fg="lime", bg="#151515")
        self.msg.pack()

        
        self.texto_frame = tk.Frame(self.frame_direita, bg="#151515")
        self.texto_frame.pack(fill="both")
        self.saida_texto = tk.Text(self.texto_frame, width=80, height=30, bg="#1e1e1e", fg="white", yscrollcommand=lambda *args: self.scrollbar.set(*args))
        self.saida_texto.pack(side="left", fill="both")

        self.scrollbar = tk.Scrollbar(self.texto_frame, orient="vertical", command=self.saida_texto.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.saida_texto.config(yscrollcommand=self.scrollbar.set)

     
        self.resultado_label = tk.Label(self.frame_direita, text="Resultado da Consulta:", fg="white", bg="#151515")
        self.resultado_label.pack(pady=(10, 0))

        self.resultado_frame = tk.Frame(self.frame_direita, bg="#151515")
        self.resultado_frame.pack(fill="both", expand=True)

        self.resultado_tabela = ttk.Treeview(self.resultado_frame)
        self.resultado_tabela.pack(side="left", fill="both", expand=True)

        self.scroll_resultado = tk.Scrollbar(self.resultado_frame, orient="vertical", command=self.resultado_tabela.yview)
        self.scroll_resultado.pack(side="right", fill="y")
        self.resultado_tabela.config(yscrollcommand=self.scroll_resultado.set)


        self.dados = {}

    
    def salvardados(self):
        ferramenta = self.entradaescolha.get().strip().lower()
        host = self.entradahost.get().strip()
        usuario = self.entradausuario.get().strip()
        senha = self.entradasenha.get().strip()
        database = self.entradabanco.get().strip()

        if not (ferramenta and host and usuario and database):
            self.msg.config(text="insira todos os dados")
            return

        if ferramenta not in ("mysql", "psql"):
            self.msg.config(text="insira as ferramentas validas : mysql ou psql")
            return

        self.dados = {
            "ferramenta": ferramenta,
            "host": host,
            "usuario": usuario,
            "senha": senha,
            "banco de dados": database
        }
        self.msg.config(text="Dados salvos com sucesso")
        self.Interface.after(3000, lambda: self.msg.config(text=""))

        try:
            conexao = self.procurarconexao()
            conexao.close()
            self.msg.config(text="Conexao bem-sucedida")
        except Exception as e:
            self.msg.config(text=f"Erro na conexao {e}")

        self.msg.after(5000, lambda: self.msg.config(text=""))

    def procurarconexao(self):
        if self.dados["ferramenta"] == "mysql":
            return conectarsql(self.dados["host"], self.dados["usuario"], self.dados["senha"], self.dados["banco de dados"])
        elif self.dados["ferramenta"] == "psql":
            return conectarpsql(self.dados["host"], self.dados["usuario"], self.dados["senha"], self.dados["banco de dados"])
        else:
            self.msg.config(text="Tipo invalido: use 'mysql' ou 'psql'")
            return

    def chamar_mostrartabelas(self):
        try:
            conexao = self.procurarconexao()
            self.Mostrartabelas(conexao)
            conexao.close()
        except Exception as e:
            self.msg.config(text=f"Erro ao conectar: {e}")

    def Mostrartabelas(self, conexao):
        cursor = conexao.cursor()
        self.saida_texto.delete("1.0", tk.END)  

        try:
            if self.dados["ferramenta"] == "mysql": #mostrar tabelas pelo mysql
                cursor.execute("SHOW TABLES;")
                tabelas = [linha[0] for linha in cursor.fetchall()]
                for tabela in tabelas:
                    self.saida_texto.insert(tk.END, f"Tabela: {tabela}\n")
                    cursor.execute(f"DESCRIBE {tabela}")
                    for colunas in cursor.fetchall():
                        self.saida_texto.insert(tk.END, f"  Coluna: {colunas[0]} | Tipo: {colunas[1]}\n")

            elif self.dados["ferramenta"] == "psql": #mostrar tabelas pelo postgresql
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tabelas = cursor.fetchall()
                for (tabela,) in tabelas:
                    self.saida_texto.insert(tk.END, f"Tabela: {tabela}\n")
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s;
                    """, (tabela,))
                    colunas = cursor.fetchall()
                    for nome, tipo in colunas:
                        self.saida_texto.insert(tk.END, f"  Coluna: {nome} | Tipo: {tipo}\n")
        except Exception as e:
            self.saida_texto.insert(tk.END, f"Erro ao listar tabelas: {e}\n")
        finally:
            cursor.close()


    def extrair_sql(self, resposta):
        if isinstance(resposta, dict): #verifica se e dicionario
            resposta = resposta.get("result", "")

        #remove as marcas do codigo
        resposta = re.sub( 
            r"```(?:sql)?\s*(.*?)\s*```",
            r"\1",
            resposta,
            flags=re.DOTALL | re.IGNORECASE
        )
        #remove linhas e formatacao
        resposta = "\n".join(
            l for l in resposta.splitlines()
            if not l.strip().startswith(("**", "*", "-", "1.", "2.", "3.", "#"))
        )
        #procura onde comeca o comando sql
        for linha in resposta.splitlines():
            linha_limpa = linha.strip()
            if re.match(r'^(SELECT|INSERT|UPDATE|DELETE|WITH|CREATE|DROP|ALTER)', linha_limpa, re.IGNORECASE):
                return linha_limpa
        #caso nao encontre, remove os acentos e retorna
        return resposta.replace("`", "").strip()

    
    def realizarquery(self):
        texto_usuario = self.entradaquery.get().strip()
        if not texto_usuario:
            self.msg.config(text="Insira o comando em linguagem natural.")
            self.msg.after(5000, lambda: self.msg.config(text=""))
            return

        try:
            ferramenta = self.dados.get("ferramenta")
            usuario = self.dados.get("usuario")
            senha = self.dados.get("senha")
            host = self.dados.get("host")
            banco = self.dados.get("banco de dados")

            os.environ["OPENROUTER_API_KEY"] = "" #insira a chave do Openrouter aqui
            #configuracao da llm, com temperatura 0 para menor variacao nos resultados
            llm = ChatOpenAI( 
                model="deepseek/deepseek-r1-0528:free",
                temperature=0.0,
                openai_api_base="https://openrouter.ai/api/v1",
                openai_api_key=os.environ["OPENROUTER_API_KEY"]
            )

            parser = PydanticOutputParser(pydantic_object=SQLQuery) #o template da resposta da llm
            #prompt para a llm
            prompt = PromptTemplate(
                template="Voce e um assistente que converte linguagem natural em SQL.\n{format_instructions}\nPergunta: {query}",
                input_variables=["query"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )
            #envia os componentes e recebe o comando
            chain = prompt | llm | parser 
            resultado = chain.invoke({"query": texto_usuario}) #transforma em uma query sql
            sql_gerado = resultado.sql.strip() #retira o espaco

            if not sql_gerado:
                self.saida_texto.insert(tk.END, "\nNenhuma consulta SQL foi retornada.\n")
                self.msg.config(text="Consulta vazia.")
                return

            self.saida_texto.insert(tk.END, f"\nSQL Gerado:\n{sql_gerado}\n")

            conexao = self.procurarconexao() #conecta no banco d dados
            cursor = conexao.cursor()
            cursor.execute(sql_gerado) #executa o codigo
            resultado_query = cursor.fetchall() #pega tudo
            colunas = [desc[0] for desc in cursor.description] #lista de colunas para visualizacao
            cursor.close()
            conexao.close()

            self.resultado_tabela.delete(*self.resultado_tabela.get_children()) #deleta as informacoes anteriores
            self.resultado_tabela["columns"] = colunas
            self.resultado_tabela["show"] = "headings" #constroi as colunas

            for col in colunas:
                self.resultado_tabela.heading(col, text=col)    #configura
                self.resultado_tabela.column(col, width=150)

            for linha in resultado_query:
                self.resultado_tabela.insert("", "end", values=linha) #insere os dados

        except Exception as e:
            self.saida_texto.insert(tk.END, f"Erro ao realizar query: {e}\n")
            self.msg.config(text="Erro na execucao.")
            self.msg.after(5000, lambda: self.msg.config(text=""))

def Inicializacao():
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()

if __name__ == "__main__":
    Inicializacao()