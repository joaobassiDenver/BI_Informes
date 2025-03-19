import pandas as pd
import streamlit as st
from datetime import datetime
import os

st.header("Controle Entrega Informes")

# Selecao Usuario
usuarios_list = ["Joao Bassi", "Daniel Lima", "Gabi", "Felipe", "Juliana", "Carpi", "Rodrigo"]
usuario_selected = st.selectbox("Selecione o usuario responsavel:", usuarios_list)

db_arquivo = f"{usuario_selected}_Relatorio_Entregas.xlsx"

# Calculo de Informes por dia
informes_por_pessoa = 14
informes_feitos = 0  # Inicializa a contagem de informes feitos

st.text(f"Informes por pessoa: {informes_por_pessoa}")

# Campo para o nome do fundo
fundo_iniciado = st.text_input("Digite o Nome do Fundo Iniciado")

# Listas para armazenar as horas
hora_inicio_list = []
hora_termino_list = []
observacoes_list = []

def hora_atual():
    return datetime.now()

# Variáveis globais para controlar o fundo iniciado
if 'hora_inicio' not in st.session_state:
    st.session_state.hora_inicio = None

if 'relatorio' not in st.session_state:
    st.session_state.relatorio = []

if 'informes_feitos' not in st.session_state:
    st.session_state.informes_feitos = 0

if 'informes_restantes' not in st.session_state:
    st.session_state.informes_restantes = informes_por_pessoa

# Exibe os informes restantes
st.text(f"Informes restantes: {st.session_state.informes_restantes}")

# Iniciar fundo
if st.button("Iniciar Fundo"):
    st.session_state.hora_inicio = hora_atual().strftime('%H:%M:%S')
    st.write(f"Início registrado: {st.session_state.hora_inicio}")

# Observações do usuário
observacoes = st.text_area("Observações: ")

# Finalizar fundo
if st.button("Finalizar Fundo"):
    if st.session_state.hora_inicio:
        hora_final = hora_atual().strftime('%H:%M:%S')
        st.write(f"Hora final registrada: {hora_final}")
        
        # Adicionando ao relatório
        st.session_state.relatorio.append({
            "Usuario": usuario_selected,
            "Fundo": fundo_iniciado,
            "Hora Inicio": st.session_state.hora_inicio,
            "Hora Termino": hora_final,
            "Observacoes": observacoes
        })

        # Incrementar a contagem de informes feitos
        st.session_state.informes_feitos += 1

        # Reduzir os informes restantes
        st.session_state.informes_restantes = informes_por_pessoa - st.session_state.informes_feitos

        # Resetando hora_inicio após o fundo ser finalizado
        st.session_state.hora_inicio = None
    else:
        st.warning("Por favor, inicie o fundo antes de finalizar.")

# Exibir todos os registros do relatório
if st.session_state.relatorio:
    df_relatorio = pd.DataFrame(st.session_state.relatorio)
    st.write(df_relatorio)

# Se quiser salvar o arquivo Excel
if st.button("Salvar Relatório"):
    if st.session_state.relatorio:

        if os.path.exists(db_arquivo):
            # Se o arquivo já existe, carrega o arquivo existente
            df_existente = pd.read_excel(db_arquivo)

            # Adiciona os novos dados ao DataFrame existente
            df_novo = pd.DataFrame(st.session_state.relatorio)
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)

            # Salva o DataFrame atualizado no arquivo
            df_final.to_excel(db_arquivo, index=False)
            st.success(f"Relatório atualizado e salvo como {db_arquivo}")
        else:
            # Se o arquivo não existe, cria um novo
            df_novo = pd.DataFrame(st.session_state.relatorio)
            df_novo.to_excel(db_arquivo, index=False)
            st.success(f"Relatório salvo como {db_arquivo}")

# Botão para fazer download do arquivo
with open(f'/mount/src/bi_informes/{db_arquivo}', 'rb') as f:
    st.download_button(
        label="Baixar Relatório",
        data=f,
        file_name='Joao_Bassi_Relatorio_Entregas.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

