import streamlit as st
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Uorquin Empresas", layout="wide")

# =========================
# CSS PROFISSIONAL (PADRÃO MOCKUP)
# =========================
st.markdown("""
<style>

/* Fundo geral */
body {
    background-color: #f4f7fb;
}

/* HERO */
.hero {
    background: linear-gradient(90deg, #1F2A44, #4CAF7A);
    padding: 40px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 32px;
    margin-bottom: 5px;
}

.hero p {
    opacity: 0.8;
}

/* CARD CENTRAL */
.card {
    background: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.08);
    max-width: 900px;
    margin: auto;
}

/* INPUTS */
.stTextInput input, .stTextArea textarea {
    border-radius: 10px;
}

/* BOTÕES */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
    font-weight: bold;
    border: none;
}

/* BOTÃO PRINCIPAL */
.primary button {
    background: linear-gradient(90deg, #1F2A44, #4CAF7A);
    color: white;
}

/* SUCESSO CUSTOM */
.success-box {
    background: linear-gradient(90deg, #1F2A44, #4CAF7A);
    padding: 30px;
    border-radius: 20px;
    color: white;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <h1>Uorquin Empresas</h1>
    <p>Cadastre vagas e encontre os melhores talentos</p>
</div>
""", unsafe_allow_html=True)

# =========================
# ESTADOS
# =========================
estados = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
"MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]

@st.cache_data
def buscar_cidades(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    r = requests.get(url)
    if r.status_code == 200:
        return sorted([c["nome"] for c in r.json()])
    return []

def gerar_codigo_vaga(estado, cidade, empresa):
    data = datetime.now()
    return f"{estado[:2]}{cidade[:3]}{empresa[:3]}{data.strftime('%d%m')}"

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
    planilha.append_row([
        dados["empresa"]["nome"],
        dados["vaga"]["titulo"]
    ])

# =========================
# CONTROLE
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1

if "dados" not in st.session_state:
    st.session_state.dados = {}

# =========================
# CARD INÍCIO
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

# =========================
# ETAPA 1
# =========================
if st.session_state.step == 1:

    st.subheader("🏢 Dados da Empresa")

    nome = st.text_input("Nome da empresa")
    email = st.text_input("Email")
    estado = st.selectbox("Estado", estados)
    cidade = st.selectbox("Cidade", buscar_cidades(estado))

    st.markdown('<div class="primary">', unsafe_allow_html=True)
    if st.button("Continuar"):
        st.session_state.dados["empresa"] = {
            "nome": nome,
            "email": email,
            "estado": estado,
            "cidade": cidade
        }
        st.session_state.step = 2
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ETAPA 2
# =========================
elif st.session_state.step == 2:

    st.subheader("📄 Dados da Vaga")

    titulo = st.text_input("Título da vaga")
    descricao = st.text_area("Descrição")

    col1, col2 = st.columns(2)

    if col1.button("Voltar"):
        st.session_state.step = 1
        st.rerun()

    st.markdown('<div class="primary">', unsafe_allow_html=True)
    if col2.button("Publicar Vaga"):
        st.session_state.dados["vaga"] = {
            "titulo": titulo,
            "descricao": descricao
        }

        salvar_vaga(st.session_state.dados)

        st.session_state.step = 3
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SUCESSO
# =========================
elif st.session_state.step == 3:

    st.markdown("""
    <div class="success-box">
        🚀 Vaga cadastrada com sucesso!
    </div>
    """, unsafe_allow_html=True)

    if st.button("Cadastrar nova vaga"):
        st.session_state.step = 1
        st.session_state.dados = {}
        st.rerun()

# =========================
# FECHA CARD
# =========================
st.markdown('</div>', unsafe_allow_html=True)
