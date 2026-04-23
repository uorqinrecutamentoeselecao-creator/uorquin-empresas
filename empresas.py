import streamlit as st
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Uorquin Empresas", layout="centered")

st.image("logo.png", width=220)
st.markdown("<h3 style='text-align:center'>Cadastro de Vagas - Empresas</h3>", unsafe_allow_html=True)

# =========================
# ESTADOS
# =========================
estados = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
"MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]

# =========================
# IBGE
# =========================
@st.cache_data
def buscar_cidades(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    r = requests.get(url)
    if r.status_code == 200:
        return sorted([c["nome"] for c in r.json()])
    return []

# =========================
# GERAR CODIGO DA VAGA
# =========================
def gerar_codigo_vaga(estado, cidade, empresa):
    estado = estado.upper()
    cidade = cidade.replace(" ", "")[:3].upper()
    empresa = empresa.replace(" ", "")[:3].upper()

    data = datetime.now()
    dia = data.strftime("%d")
    mes = data.strftime("%m")

    return f"{estado}{cidade}{empresa}{dia}{mes}"

# =========================
# GOOGLE SHEETS (SHEET2)
# =========================
def conectar_planilha():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
    client = gspread.authorize(creds)

    return client.open("Banco_Uorquin").worksheet("Sheet2")

# =========================
# SALVAR VAGA
# =========================
def salvar_vaga(dados):
    planilha = conectar_planilha()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    codigo = gerar_codigo_vaga(
        dados["empresa"]["estado"],
        dados["empresa"]["cidade"],
        dados["empresa"]["nome"]
    )

    # Cabeçalho automático
    if not planilha.row_values(1):

        cabecalho = [
            "Codigo_Vaga",
            "Data",
            "Empresa","CNPJ","Email","Telefone",
            "Estado","Cidade",
            "Titulo_Vaga","Descricao",
            "Salario","Tipo","Modalidade"
        ]

        for i in range(1,11):
            cabecalho.append(f"Beneficio_{i}")

        for i in range(1,11):
            cabecalho.append(f"Requisito_{i}")

        planilha.append_row(cabecalho)

    linha = [
        codigo,
        data_hora,
        dados["empresa"]["nome"],
        dados["empresa"]["cnpj"],
        dados["empresa"]["email"],
        dados["empresa"]["telefone"],
        dados["empresa"]["estado"],
        dados["empresa"]["cidade"],
        dados["vaga"]["titulo"],
        dados["vaga"]["descricao"],
        dados["vaga"]["salario"],
        dados["vaga"]["tipo"],
        dados["vaga"]["modalidade"]
    ]

    # Benefícios
    for i in range(10):
        if i < len(dados["beneficios"]):
            linha.append(dados["beneficios"][i])
        else:
            linha.append("")

    # Requisitos
    for i in range(10):
        if i < len(dados["requisitos"]):
            linha.append(dados["requisitos"][i])
        else:
            linha.append("")

    planilha.append_row(linha)

# =========================
# CONTROLE
# =========================
if "step_emp" not in st.session_state:
    st.session_state.step_emp = 1

if "dados_emp" not in st.session_state:
    st.session_state.dados_emp = {}

if "qtd_beneficios" not in st.session_state:
    st.session_state.qtd_beneficios = 1

if "qtd_requisitos" not in st.session_state:
    st.session_state.qtd_requisitos = 1

st.progress(st.session_state.step_emp / 4)

# =========================
# ETAPA 1 - EMPRESA
# =========================
if st.session_state.step_emp == 1:

    st.subheader("Informações da Empresa")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome da empresa")
        cnpj = st.text_input("CNPJ")
        email = st.text_input("Email")

    with col2:
        telefone = st.text_input("Telefone")
        estado = st.selectbox("Estado", estados)
        cidade = st.selectbox("Cidade", buscar_cidades(estado))

    if st.button("Continuar ➡️"):

        st.session_state.dados_emp["empresa"] = {
            "nome": nome,
            "cnpj": cnpj,
            "email": email,
            "telefone": telefone,
            "estado": estado,
            "cidade": cidade
        }

        st.session_state.step_emp = 2
        st.rerun()

# =========================
# ETAPA 2 - VAGA
# =========================
elif st.session_state.step_emp == 2:

    st.subheader("Descrição da Vaga")

    titulo = st.text_input("Título da vaga")
    descricao = st.text_area("Descrição completa")

    col1, col2, col3 = st.columns(3)

    with col1:
        salario = st.text_input("Salário")

    with col2:
        tipo = st.selectbox("Tipo", ["CLT","PJ","Estágio"])

    with col3:
        modalidade = st.selectbox("Modalidade", ["Presencial","Remoto","Híbrido"])

    col1, col2 = st.columns(2)

    if col1.button("⬅️ Voltar"):
        st.session_state.step_emp = 1
        st.rerun()

    if col2.button("Continuar ➡️"):

        st.session_state.dados_emp["vaga"] = {
            "titulo": titulo,
            "descricao": descricao,
            "salario": salario,
            "tipo": tipo,
            "modalidade": modalidade
        }

        st.session_state.step_emp = 3
        st.rerun()

# =========================
# ETAPA 3 - BENEFÍCIOS
# =========================
elif st.session_state.step_emp == 3:

    st.subheader("Benefícios")

    beneficios = []

    for i in range(st.session_state.qtd_beneficios):
        b = st.text_input(f"Benefício {i+1}", key=f"benef_{i}")
        beneficios.append(b)

    if st.session_state.qtd_beneficios < 10:
        if st.button("➕ Adicionar benefício"):
            st.session_state.qtd_beneficios += 1
            st.rerun()

    col1, col2 = st.columns(2)

    if col1.button("⬅️ Voltar"):
        st.session_state.step_emp = 2
        st.rerun()

    if col2.button("Continuar ➡️"):
        st.session_state.dados_emp["beneficios"] = beneficios
        st.session_state.step_emp = 4
        st.rerun()

# =========================
# ETAPA 4 - REQUISITOS
# =========================
elif st.session_state.step_emp == 4:

    st.subheader("Pré-requisitos")

    requisitos = []

    for i in range(st.session_state.qtd_requisitos):
        r = st.text_input(f"Requisito {i+1}", key=f"req_{i}")
        requisitos.append(r)

    if st.session_state.qtd_requisitos < 10:
        if st.button("➕ Adicionar requisito"):
            st.session_state.qtd_requisitos += 1
            st.rerun()

    col1, col2 = st.columns(2)

    if col1.button("⬅️ Voltar"):
        st.session_state.step_emp = 3
        st.rerun()

    if col2.button("🚀 Publicar vaga"):

        st.session_state.dados_emp["requisitos"] = requisitos

        salvar_vaga(st.session_state.dados_emp)

        st.success("Vaga cadastrada com sucesso!")

        # RESET
        st.session_state.step_emp = 1
        st.session_state.dados_emp = {}
        st.session_state.qtd_beneficios = 1
        st.session_state.qtd_requisitos = 1

        st.rerun()
