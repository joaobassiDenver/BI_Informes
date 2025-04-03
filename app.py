import psycopg2
import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def iniciarConexao():
    try:
        conn = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("conn successful!")
        
    except Exception as e:
        print(f"Failed to connect: {e}")
    
    return conn

def registrarAtuantes(name):
    
    conn = iniciarConexao()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO pessoasAtuando (name) VALUES (%s)", (name,))
    conn.commit()
    conn.close()

def cadastrarADM(adm):
    
    conn = iniciarConexao()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO admCadastro (name) VALUES (%s)", (adm,))
    
    conn.commit()
    conn.close()

def obterPessoasAtuantes():
    conn = iniciarConexao()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pessoasAtuando")
    registros = cursor.fetchall()
    
    conn.close()
    
    return pd.DataFrame(registros, columns=["ID", "Nome"])  # Colunas personalizadas de acordo com a tabela

def obterAdmCadastrado():
    conn = iniciarConexao()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM admCadastro")
    registros = cursor.fetchall()
    
    conn.close()
    
    return pd.DataFrame(registros, columns=["ID", "ADM"])  # Colunas personalizadas de acordo com a tabela

def excluir_registro(id):  # Conectando ao banco de dados
    conn = iniciarConexao()
    cursor = conn.cursor()
    
    # Certificando-se de que o id é um número inteiro
    try:
        id = int(id)
    except ValueError:
        st.error("ID inválido. Por favor, insira um número.")
        return
    
    # SQL para excluir o registro com base no ID
    cursor.execute("DELETE FROM pessoasAtuando WHERE id = %s", (id,))
    
    conn.commit()  # Confirma a transação
    conn.close()   # Fecha a conexão

def obterDatas():
    conn = iniciarConexao()
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT startDate FROM registroFundos;
                   ''')

    datas = cursor.fetchall()
    
    conn.close()
    
    return np.unique(datas)

def obterRegistroFundo(data=None, complete=False):
    conn = iniciarConexao()
    cursor = conn.cursor()
    
    if complete == False:
        cursor.execute("SELECT * FROM registroFundos WHERE startDate = %s", (data,))
    else: 
        cursor.execute("SELECT * FROM registroFundos")
        
    registrosDF = cursor.fetchall()
    
    conn.close()
    
    return pd.DataFrame(registrosDF, columns=["ID", "Responsável", "Data", "Hora Início", "Hora Término","Fundo", "Obs.", "Adm"])

def registrarFundo(pessoaResponsavel, nomeFundo, adm, dataAtual, hora_inicio, hora_termino, obs):
    conn = iniciarConexao()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO registroFundos (userName, fundoName, adm, startDate, startTime, finishTime, obs)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (pessoaResponsavel, nomeFundo, adm, dataAtual, hora_inicio, hora_termino, obs))
    
    conn.commit()
    conn.close()

st.sidebar.title("Menu")

escolha = st.sidebar.radio(
    "Escolha uma opção: ", ("Cadastro", "Controle Entregas", "Registros")
)

if escolha == "Cadastro":

    st.header("Área de Cadastro - Informe Mensal")

    name = st.text_input("Registrar novos atuantes: ")
    
    if name:
        cadastro =st.button("Cadastrar")
        if cadastro:
            registrarAtuantes(name)
            st.success(f"{name} - Cadastrado com sucesso!")

    pessoasAtuandoDF = obterPessoasAtuantes()
    
    st.table(pessoasAtuandoDF)
    
    admName = st.text_input("Cadastrar novo administrator: ")
    
    if admName:
        cadastroAdm =st.button("Cadastrar")
        if cadastroAdm:
            cadastrarADM(admName)
            st.success(f"{admName} - Cadastrado com sucesso!")
        
    admCadastradosDF = obterAdmCadastrado()
    
    st.table(admCadastradosDF)

elif escolha == "Controle Entregas":
    
    st.header("Controle Entregas - Informe Mensal")
    
    metaDiaria = 14
    
    st.text(f"Meta de informes diários por pessoa: {metaDiaria}")
    
    pessoaResponsavel = st.selectbox("Selecione o responsável pelo registro: ", options=obterPessoasAtuantes()["Nome"])
    
    nomeFundo = st.text_input("Digite o nome do Fundo: ")
    
    adm = st.selectbox("Selecione o administrador: ", options=obterAdmCadastrado()["ADM"])
    
    dataAtual = datetime.now().strftime("%d/%m/%Y")
    
    if nomeFundo:
        if 'hora_inicio' not in st.session_state:
            st.session_state['hora_inicio'] = None
        
        if 'hora_termino' not in st.session_state:
            st.session_state['hora_termino'] = None
            
        inicio = st.button("Iniciar")
        if inicio and st.session_state['hora_inicio'] is None:
            st.session_state['hora_inicio'] = datetime.now().strftime("%H:%M:%S")
            st.success(f"Início do fundo registrado: {st.session_state['hora_inicio']}")
        
        obs = st.text_area("Digite suas observações sobre o Fundo: ")
        
        termino = st.button("Finalizar")
        if termino and st.session_state['hora_inicio'] is not None:
            st.session_state['hora_termino'] = datetime.now().strftime("%H:%M:%S")
            registrarFundo(pessoaResponsavel, nomeFundo, adm,dataAtual, 
                           st.session_state['hora_inicio'], st.session_state['hora_termino'], obs)
            st.success(f"{nomeFundo} - finalizado com sucesso")
            
            st.session_state['hora_inicio'] = None
            st.session_state['hora_termino'] = None

elif escolha == "Registros":
    st.header("Registros de Entregas - Informes Mensais")
    
    periodo_extracao = st.selectbox("Deseja data específica, ou histórico completo: ", options=["Data Específica", "Histórico Completo"])
    
    if periodo_extracao == "Data Específica":
        dataEscolhida = st.selectbox("Escolha a data :", obterDatas())
        
        st.dataframe(obterRegistroFundo(dataEscolhida))
    else:
        st.dataframe(obterRegistroFundo(complete=True))
        
    
