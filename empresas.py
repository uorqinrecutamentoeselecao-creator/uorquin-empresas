import streamlit as st
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Uorquin Empresas", layout="centered")

# =========================
# ESTILO (UORQUIN BRAND)
# =========================
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}

.header {
    text-align: center;
    padding: 10px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.gradient {
    background: linear-gradient(90deg, #1F2A44, #4CAF7A);
    padding: 12px;
    border-radius: 10px;
    color: white;
    text-align: center;
    font-weight: bold;
}

.stButton>button {
    border-radius: 10px;
    padding: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.png", width=180)
st.markdown("<h2>Cadastro de Vagas</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:gray'>Conectando pessoas a oportunidades</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
# GERAR CODIGO
# =========================
def gerar_codigo_vaga(estado, cidade, empresa):
    estado = estado.upper()
    cidade = cidade.replace(" ", "")[:3].upper()
    empresa = empresa.replace(" ", "")[:3].upper()

    data = datetime.now()
    return f"{estado}{cidade}{empresa}{data.strftime('%d%m')}"

# =========================
# GOOGLE SHEETS
# =========================
def conectar_planilha():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )

    client = gspread.authorize(creds)
    return client.open("Banco_Uorquin").worksheet("Sheet2")

def salvar_vaga(dados):
    planilha = conectar_planilha()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    codigo = gerar_codigo_vaga(
        dados["empresa"]["estado"],
        dados["empresa"]["cidade"],
        dados["empresa"]["nome"]
    )

    if not planilha.row_values(1):
        cabecalho = [
            "Codigo_Vaga","Data","Empresa","CNPJ","Email","Telefone",
            "Estado","Cidade","Titulo_Vaga","Descricao",
            "Salario","Tipo","Modalidade"
        ]
        for i in range(1,11): cabecalho.append(f"Beneficio_{i}")
        for i in range(1,11): cabecalho.append(f"Requisito_{i}")
        planilha.append_row(cabecalho)

    linha = [
        codigo, data_hora,
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

    linha += dados["beneficios"] + [""]*(10-len(dados["beneficios"]))
    linha += dados["requisitos"] + [""]*(10-len(dados["requisitos"]))

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

# =========================
# PROGRESSO VISUAL
# =========================
steps = ["Empresa", "Vaga", "Benefícios", "Requisitos"]
st.markdown(f'<div class="gradient">Etapa {st.session_state.step_emp}/4 - {steps[st.session_state.step_emp-1]}</div>', unsafe_allow_html=True)
st.progress(st.session_state.step_emp / 4)

# =========================
# ETAPA 1
# =========================
if st.session_state.step_emp == 1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🏢 Informações da Empresa")

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

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ETAPA 2
# =========================
elif st.session_state.step_emp == 2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📄 Descrição da Vaga")

    titulo = st.text_input("Título da vaga")
    descricao = st.text_area("Descrição")

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

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ETAPA 3
# =========================
elif st.session_state.step_emp == 3:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🎁 Benefícios")

    beneficios = []

    for i in range(st.session_state.qtd_beneficios):
        beneficios.append(st.text_input(f"Benefício {i+1}", key=f"benef_{i}"))

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

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ETAPA 4
# =========================
elif st.session_state.step_emp == 4:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📌 Pré-requisitos")

    requisitos = []

    for i in range(st.session_state.qtd_requisitos):
        requisitos.append(st.text_input(f"Requisito {i+1}", key=f"req_{i}"))

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

        st.success("✅ Vaga publicada com sucesso!")

        st.session_state.step_emp = 1
        st.session_state.dados_emp = {}
        st.session_state.qtd_beneficios = 1
        st.session_state.qtd_requisitos = 1

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
