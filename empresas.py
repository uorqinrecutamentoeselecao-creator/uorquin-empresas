import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Empresas - Uorquin", layout="wide")

st.title("🏢 Cadastro de Vagas")

# =========================
# CONEXÃO
# =========================
def conectar_planilha():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )

    client = gspread.authorize(creds)
    return client.open("Banco_Uorquin")

# =========================
# GERAR CÓDIGO DA VAGA
# =========================
def gerar_codigo(estado, cidade, empresa):
    hoje = datetime.now()
    return f"{estado[:2].upper()}{cidade[:3].upper()}{empresa[:3].upper()}{hoje.day:02d}{hoje.month:02d}"

# =========================
# FORMULÁRIO
# =========================
st.subheader("📋 Informações da vaga")

col1, col2 = st.columns(2)

with col1:
    empresa = st.text_input("Empresa")
    cidade = st.text_input("Cidade")

with col2:
    estado = st.text_input("Estado")
    titulo = st.text_input("Título da vaga")

salario = st.text_input("Salário")
descricao = st.text_area("Descrição da vaga")

st.subheader("🎁 Benefícios")
beneficios = []
for i in range(3):
    beneficios.append(st.text_input(f"Benefício {i+1}", key=f"b{i}"))

st.subheader("📌 Pré-requisitos")
requisitos = []
for i in range(3):
    requisitos.append(st.text_input(f"Requisito {i+1}", key=f"r{i}"))

# =========================
# SALVAR
# =========================
if st.button("🚀 Publicar vaga"):

    if not empresa or not cidade or not estado or not titulo:
        st.warning("Preencha os campos obrigatórios")
    else:
        client = conectar_planilha()

        try:
            planilha = client.worksheet("Sheet2")
        except:
            planilha = client.add_worksheet(title="Sheet2", rows="1000", cols="20")

            planilha.append_row([
                "Codigo_Vaga","Empresa","Cidade","Estado","Titulo_Vaga",
                "Salario","Descricao",
                "Beneficio_1","Beneficio_2","Beneficio_3",
                "Requisito_1","Requisito_2","Requisito_3"
            ])

        codigo = gerar_codigo(estado, cidade, empresa)

        linha = [
            codigo, empresa, cidade, estado, titulo,
            salario, descricao,
            beneficios[0], beneficios[1], beneficios[2],
            requisitos[0], requisitos[1], requisitos[2]
        ]

        planilha.append_row(linha)

        st.success(f"Vaga publicada com sucesso! Código: {codigo}")
