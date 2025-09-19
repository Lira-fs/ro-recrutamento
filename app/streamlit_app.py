# app/streamlit_app.py - VERSÃO EXPANDIDA COM SISTEMA DE VAGAS
import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Adicionar pasta backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato_completa, gerar_ficha_vaga_completa  # ✅ Import para vagas

# Configurar página
st.set_page_config(
    page_title="R.O Recrutamento - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mantendo o padrão existente
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #a65e2e 0%, #d4a574 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #a65e2e;
        margin: 0.5rem 0;
    }
    
    .candidate-card, .vaga-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: #a65e2e;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: #8b4d22;
        color: white;
    }

    .status-ativa {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-preenchida {
        background: #007bff;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-pausada {
        background: #ffc107;
        color: #000;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-cancelada {
        background: #dc3545;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# FUNÇÕES EXISTENTES DE CANDIDATOS (preservadas do seu código)
# =====================================

@st.cache_data(ttl=300)
def carregar_candidatos():
    """Carrega candidatos do Supabase com cache"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('candidatos').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar candidatos: {str(e)}")
        return pd.DataFrame()

def qualificar_candidato_simples(candidato_id, nota, observacoes, instrutor):
    """Função simplificada para qualificar candidato"""
    try:
        supabase = get_supabase_client()
        
        # Buscar tipo de formulário do candidato
        candidato_resp = supabase.table('candidatos').select('formulario_id').eq('id', candidato_id).execute()
        
        if not candidato_resp.data:
            return False, None
        
        tipo_treinamento = candidato_resp.data[0].get('formulario_id', 'GERAL')
        
        # Gerar certificado
        import uuid
        certificado_numero = f"RO-{tipo_treinamento.upper().replace('CANDI-', '')}-{str(uuid.uuid4())[:8]}"
        
        # Dados para inserir
        dados = {
            'candidato_id': candidato_id,
            'nota_treinamento': int(nota),
            'observacoes_treinamento': observacoes,
            'instrutor_responsavel': instrutor,
            'tipo_treinamento': tipo_treinamento,
            'certificado_numero': certificado_numero,
            'certificado_emitido': True if nota >= 7 else False,
            'data_qualificacao': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        # Inserir no banco
        resultado = supabase.table('candidatos_qualificados').insert(dados).execute()
        
        if resultado.data and len(resultado.data) > 0:
            return True, certificado_numero
        else:
            return False, None
            
    except Exception as e:
        st.error(f"Erro técnico: {str(e)}")
        return False, None

def carregar_candidatos_qualificados():
    """Carrega candidatos qualificados com dados combinados"""
    try:
        supabase = get_supabase_client()
        
        # Buscar qualificações
        qualificacoes = supabase.table('candidatos_qualificados').select('*').execute()
        
        if not qualificacoes.data:
            return pd.DataFrame()
        
        # Buscar candidatos que estão qualificados
        candidatos_ids = [q['candidato_id'] for q in qualificacoes.data]
        candidatos = supabase.table('candidatos').select('*').in_('id', candidatos_ids).execute()
        
        if not candidatos.data:
            return pd.DataFrame()
        
        # Combinar dados manualmente
        dados_combinados = []
        for candidato in candidatos.data:
            qualificacao = next((q for q in qualificacoes.data if q['candidato_id'] == candidato['id']), None)
            
            if qualificacao:
                candidato_completo = candidato.copy()
                candidato_completo.update({
                    'data_qualificacao': qualificacao.get('data_qualificacao'),
                    'nota_treinamento': qualificacao.get('nota_treinamento'),
                    'certificado_emitido': qualificacao.get('certificado_emitido'),
                    'certificado_numero': qualificacao.get('certificado_numero'),
                    'instrutor_responsavel': qualificacao.get('instrutor_responsavel')
                })
                dados_combinados.append(candidato_completo)
        
        return pd.DataFrame(dados_combinados)
            
    except Exception as e:
        st.error(f"Erro ao carregar candidatos qualificados: {str(e)}")
        return pd.DataFrame()

def carregar_candidatos_pendentes():
    """Carrega candidatos que ainda não foram qualificados"""
    try:
        supabase = get_supabase_client()
        
        # Buscar todos os candidatos
        todos_candidatos = supabase.table('candidatos').select('*').execute()
        
        if not todos_candidatos.data:
            return pd.DataFrame()
        
        # Buscar IDs dos candidatos já qualificados
        qualificacoes = supabase.table('candidatos_qualificados').select('candidato_id').execute()
        
        candidatos_qualificados_ids = []
        if qualificacoes.data:
            candidatos_qualificados_ids = [q['candidato_id'] for q in qualificacoes.data]
        
        # Filtrar candidatos pendentes
        candidatos_pendentes = [
            c for c in todos_candidatos.data 
            if c['id'] not in candidatos_qualificados_ids
        ]
        
        return pd.DataFrame(candidatos_pendentes)
            
    except Exception as e:
        st.error(f"Erro ao carregar candidatos pendentes: {str(e)}")
        return pd.DataFrame()

def formatar_whatsapp_link(numero_whatsapp):
    """Converte número do WhatsApp em link clicável"""
    if not numero_whatsapp or numero_whatsapp == 'Não informado' or str(numero_whatsapp).lower() == 'nan':
        return "Não informado"
    
    # Limpar o número
    numero_limpo = str(numero_whatsapp)
    numero_limpo = ''.join(filter(str.isdigit, numero_limpo))
    
    if len(numero_limpo) < 10:
        return f"📲 {numero_whatsapp} (número inválido)"
    
    # Se não começar com 55 (Brasil), adicionar
    if not numero_limpo.startswith('55'):
        if len(numero_limpo) >= 10:
            numero_limpo = '55' + numero_limpo
    
    # Criar link do WhatsApp
    link_whatsapp = f"https://wa.me/{numero_limpo}"
    
    # Formatar número para exibição
    if len(numero_limpo) == 13:
        numero_formatado = f"+{numero_limpo[:2]} ({numero_limpo[2:4]}) {numero_limpo[4:9]}-{numero_limpo[9:]}"
    elif len(numero_limpo) == 12:
        numero_formatado = f"+{numero_limpo[:2]} ({numero_limpo[2:4]}) {numero_limpo[4:8]}-{numero_limpo[8:]}"
    else:
        numero_formatado = numero_limpo
    
    return f'<a href="{link_whatsapp}" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">📲 {numero_formatado}</a>'

def atualizar_status_ficha(candidato_id):
    """Atualiza status de ficha_emitida no banco"""
    try:
        supabase = get_supabase_client()
        
        supabase.table('candidatos').update({
            'ficha_emitida': True,
            'data_ficha_gerada': datetime.now().isoformat()
        }).eq('id', candidato_id).execute()
        
        return True
            
    except Exception as e:
        st.error(f"❌ Erro ao atualizar status: {str(e)}")
        return False

def formatar_funcao(formulario_id):
    """Converte ID da função em nome amigável para candidatos"""
    funcoes = {
        'candi-baba': '👶 Babá',
        'candi-caseiro': '🏠 Caseiro',
        'candi-copeiro': '🍷 Copeiro', 
        'candi-cozinheira': '👨‍🍳 Cozinheira(o)',
        'candi-governanta': '👑 Governanta',
        'candi-arrumadeira': '🧹 Arrumadeira',
        'candi-casal': '👫 Casal'
    }
    return funcoes.get(formulario_id, formulario_id or 'Não especificado')

# =====================================
# NOVAS FUNÇÕES PARA SISTEMA DE VAGAS
# =====================================

@st.cache_data(ttl=300)
def carregar_vagas():
    """Carrega vagas do Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('vagas').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar vagas: {str(e)}")
        return pd.DataFrame()

def carregar_observacoes_vaga(vaga_id):
    """Carrega observações de uma vaga específica"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('vaga_observacoes').select('*').eq('vaga_id', vaga_id).order('data_criacao', desc=True).execute()
        
        if response.data:
            return response.data
        else:
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar observações: {str(e)}")
        return []

def adicionar_observacao_vaga(vaga_id, observacao, tipo='geral'):
    """Adiciona nova observação à vaga"""
    try:
        supabase = get_supabase_client()
        
        dados_observacao = {
            'vaga_id': vaga_id,
            'observacao': observacao,
            'tipo_observacao': tipo
        }
        
        result = supabase.table('vaga_observacoes').insert(dados_observacao).execute()
        
        if result.data:
            return True
        return False
        
    except Exception as e:
        st.error(f"❌ Erro ao adicionar observação: {str(e)}")
        return False

def atualizar_status_vaga(vaga_id, novo_status):
    """Atualiza status da vaga"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('vagas').update({
            'status_detalhado': novo_status,
            'updated_at': datetime.now().isoformat()
        }).eq('id', vaga_id).execute()
        
        return result.data is not None
        
    except Exception as e:
        st.error(f"❌ Erro ao atualizar status: {str(e)}")
        return False

def formatar_funcao_vaga(formulario_id):
    """Converte ID da vaga em nome amigável"""
    funcoes = {
        'vaga-baba': '👶 Vaga Babá',
        'vaga-caseiro': '🏠 Vaga Caseiro',
        'vaga-copeiro': '🍷 Vaga Copeiro', 
        'vaga-cozinheira': '👨‍🍳 Vaga Cozinheira(o)',
        'vaga-governanta': '👑 Vaga Governanta',
        'vaga-arrumadeira': '🧹 Vaga Arrumadeira',
        'vaga-domestica': '🏠 Vaga Doméstica'
    }
    return funcoes.get(formulario_id, formulario_id or 'Vaga não especificada')

def relacionar_candidato_vaga(candidato_id, vaga_id, observacao=""):
    """Relaciona candidato com vaga"""
    try:
        supabase = get_supabase_client()
        
        dados_relacao = {
            'candidato_id': candidato_id,
            'vaga_id': vaga_id,
            'observacoes': observacao
        }
        
        result = supabase.table('candidatos_vagas').insert(dados_relacao).execute()
        
        if result.data:
            # Adicionar observação automática na vaga
            obs_automatica = f"Candidato enviado para esta vaga. {observacao}"
            adicionar_observacao_vaga(vaga_id, obs_automatica, 'candidato_enviado')
            return True
        return False
        
    except Exception as e:
        st.error(f"❌ Erro ao relacionar candidato-vaga: {str(e)}")
        return False

def carregar_relacionamentos():
    """Carrega relacionamentos candidatos-vagas"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('candidatos_vagas_detalhado').select('*').order('data_envio', desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar relacionamentos: {str(e)}")
        return pd.DataFrame()

# =====================================
# FUNÇÃO MAIN COM SISTEMA DE ABAS
# =====================================

def main():
    # CABEÇALHO
    st.markdown("""
    <div class="main-header">
        <h1>🏠 R.O RECRUTAMENTO - Dashboard</h1>
        <p>Gerenciamento Completo de Candidatos e Vagas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SISTEMA DE ABAS
    tab1, tab2, tab3 = st.tabs(["👥 Candidatos", "💼 Vagas", "🔗 Relacionamentos"])
    
    with tab1:
        gerenciar_candidatos()
    
    with tab2:
        gerenciar_vagas()
    
    with tab3:
        gerenciar_relacionamentos()

# =====================================
# GESTÃO DE CANDIDATOS (seu código atual preservado)
# =====================================

def gerenciar_candidatos():
    """Função com código existente dos candidatos - PRESERVADO TOTALMENTE"""
    
    # SIDEBAR - FILTROS
    st.sidebar.header("🔍 Filtros de Candidatos")

    # Filtro de qualificação
    tipo_visualizacao = st.sidebar.selectbox(
        "Visualizar:",
        [
            "Todos os candidatos",
            "Candidatos qualificados", 
            "Pendentes de qualificação"
        ]
    )

    # Carregamento condicional baseado no filtro
    with st.spinner("Carregando candidatos..."):
        if tipo_visualizacao == "Candidatos qualificados":
            df = carregar_candidatos_qualificados()
            st.header("👑 Candidatos Qualificados")
            
        elif tipo_visualizacao == "Pendentes de qualificação":
            df = carregar_candidatos_pendentes()
            st.header("⏳ Pendentes de Qualificação")
            
        else:
            df = carregar_candidatos()
            st.header("📋 Todos os Candidatos")
    
    if df.empty:
        st.warning("⚠️ Nenhum candidato encontrado no banco de dados.")
        st.info("🔄 Certifique-se que existem candidatos cadastrados no Supabase.")
        return
    
    # MÉTRICAS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Candidatos", len(df))
    
    with col2:
        fichas_geradas = len(df[df.get('ficha_emitida', pd.Series([False] * len(df))) == True])
        st.metric("📄 Fichas Geradas", fichas_geradas)
    
    with col3:
        pendentes = len(df) - fichas_geradas
        st.metric("⏳ Pendentes", pendentes)
    
    with col4:
        if 'created_at' in df.columns:
            hoje = datetime.now().date()
            novos_hoje = len(df[pd.to_datetime(df['created_at']).dt.date == hoje])
            st.metric("🆕 Hoje", novos_hoje)
        else:
            st.metric("🆕 Hoje", 0)
    
    # FILTROS NA SIDEBAR
    if 'nome_completo' in df.columns:
        filtro_nome = st.sidebar.text_input("🔍 Buscar por nome", "")
    else:
        filtro_nome = ""
    
    if 'formulario_id' in df.columns:
        funcoes_unicas = ['Todas'] + sorted(df['formulario_id'].dropna().unique().tolist())
        filtro_funcao = st.sidebar.selectbox("💼 Filtrar por função", funcoes_unicas)
    else:
        filtro_funcao = "Todas"
    
    # Filtro por status de ficha
    filtro_status = st.sidebar.radio(
        "📋 Status da ficha",
        ["Todos", "Apenas pendentes", "Apenas com ficha gerada"]
    )
    
    # APLICAR FILTROS
    df_filtrado = df.copy()
    
    # Filtro por nome
    if filtro_nome:
        if 'nome_completo' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['nome_completo'].str.contains(filtro_nome, case=False, na=False)
            ]
    
    # Filtro por função
    if filtro_funcao != "Todas":
        if 'formulario_id' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['formulario_id'] == filtro_funcao]
    
    # Filtro por status
    if filtro_status == "Apenas pendentes":
        df_filtrado = df_filtrado[df_filtrado.get('ficha_emitida', pd.Series([False] * len(df_filtrado))) != True]
    elif filtro_status == "Apenas com ficha gerada":
        df_filtrado = df_filtrado[df_filtrado.get('ficha_emitida', pd.Series([False] * len(df_filtrado))) == True]
    
    # EXIBIR RESULTADOS
    st.header(f"📋 Candidatos ({len(df_filtrado)} encontrados)")
    
    if df_filtrado.empty:
        st.info("🔍 Nenhum candidato encontrado com os filtros aplicados.")
        return
    
    # LISTA DE CANDIDATOS (seu código preservado)
    for idx, candidato in df_filtrado.iterrows():
        with st.expander(
            f"{formatar_funcao(candidato.get('formulario_id', ''))} | "
            f"{candidato.get('nome_completo', 'Nome não informado')} | "
            f"📞 {candidato.get('telefone', 'Tel. não informado')}",
            expanded=False
        ):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Informações básicas (seu código preservado)
                st.write(f"**📧 Email:** {candidato.get('email', 'Não informado')}")
                whatsapp_link = formatar_whatsapp_link(candidato.get('whatsapp'))
                st.markdown(f"**📲 Whatsapp:** {whatsapp_link}", unsafe_allow_html=True)
                st.write(f"**📍 Endereço:** {candidato.get('endereco', 'Não informado')}")
                st.write(f"**👨‍👩‍👧‍👦 Filhos:** {'Sim' if candidato.get('tem_filhos') else 'Não'}")
                st.write(f"**🚗 CNH:** {'Sim' if candidato.get('possui_cnh') else 'Não'}")
                
                if candidato.get('created_at'):
                    data_cadastro = pd.to_datetime(candidato['created_at']).strftime('%d/%m/%Y às %H:%M')
                    st.write(f"**📅 Cadastrado em:** {data_cadastro}")

                # Status de qualificação (seu código preservado)
                if 'data_qualificacao' in candidato:
                    st.success(f"✅ Qualificado em {candidato['data_qualificacao']}")
                    if candidato.get('certificado_numero'):
                        st.info(f"🎓 Certificado: {candidato['certificado_numero']}")
                else:
                    st.warning("⏳ Pendente de qualificação")
                
                # Status da ficha
                if candidato.get('ficha_emitida'):
                    st.success("✅ Ficha já gerada")
                    if candidato.get('data_ficha_gerada'):
                        data_ficha = pd.to_datetime(candidato['data_ficha_gerada']).strftime('%d/%m/%Y às %H:%M')
                        st.write(f"**📄 Ficha gerada em:** {data_ficha}")
                else:
                    st.warning("⏳ Ficha pendente")
            
            with col2:
                # Geração de PDF (seu código preservado)
                nome_arquivo = f"ficha_{candidato.get('nome_completo', 'candidato').replace(' ', '_')}_{candidato.get('id', 'sem_id')}.pdf"
                
                if f"pdf_data_{candidato.get('id')}" not in st.session_state:
                    st.session_state[f"pdf_data_{candidato.get('id')}"] = None
                
                if st.button(f"📄 Gerar Ficha PDF", key=f"pdf_{candidato.get('id')}"):
                    try:
                        with st.spinner("Gerando PDF..."):
                            st.write("📝 Preparando dados do candidato...")
                            
                            resultado = gerar_ficha_candidato_completa(candidato.to_dict())
                            
                            if isinstance(resultado, tuple):
                                pdf_bytes, nome_arquivo = resultado
                            else:
                                pdf_bytes = resultado
                                nome_limpo = candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
                                import re
                                nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
                                data_criacao = datetime.now().strftime('%d%m%Y')
                                nome_arquivo = f"{nome_limpo}-{data_criacao}.pdf"
                            
                            st.session_state[f"pdf_data_{candidato.get('id')}"] = pdf_bytes
                            st.session_state[f"pdf_nome_{candidato.get('id')}"] = nome_arquivo
                            
                            st.success(f"✅ PDF gerado! Tamanho: {len(pdf_bytes)} bytes")
                            st.info("👇 Clique no botão verde abaixo para baixar!")
                            
                            if atualizar_status_ficha(candidato.get('id')):
                                st.success("✅ Status atualizado no banco!")
                                st.cache_data.clear()
                            else:
                                st.info("ℹ️ PDF gerado, mas status não atualizado")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                        st.error(f"🔧 Tipo do erro: {type(e).__name__}")
                        
                        import traceback
                        with st.expander("🔍 Detalhes técnicos do erro"):
                            st.code(traceback.format_exc())

                # Sistema de qualificação (seu código preservado)
                if 'data_qualificacao' not in candidato.index:
                    candidato_id = candidato.get('id')
                    
                    with st.container():
                        st.markdown("---")
                        st.markdown("### 🎓 Qualificar Candidato")
                        
                        with st.form(key=f"qualificacao_form_{candidato_id}", clear_on_submit=False):
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nota = st.slider("Nota do treinamento (0-10)", 0, 10, 7)
                                
                            with col2:
                                instrutor = st.text_input("Nome do instrutor")
                            
                            observacoes = st.text_area("Observações sobre o treinamento", height=100)
                            
                            submitted = st.form_submit_button("✅ QUALIFICAR CANDIDATO", type="primary")
                            
                            if submitted:
                                if not instrutor.strip():
                                    st.error("❌ O nome do instrutor é obrigatório!")
                                else:
                                    with st.spinner("Processando qualificação..."):
                                        sucesso, certificado = qualificar_candidato_simples(candidato_id, nota, observacoes, instrutor)
                                        
                                        if sucesso:
                                            st.success(f"🎉 Candidato qualificado com sucesso!")
                                            st.success(f"🎓 Certificado: {certificado}")
                                            st.balloons()
                                            
                                            import time
                                            time.sleep(2)
                                            
                                            st.cache_data.clear()
                                            st.info("🔄 Recarregando página...")
                                            st.rerun()
                                        else:
                                            st.error("❌ Erro ao qualificar candidato. Tente novamente.")      
                
                # Botão de download (seu código preservado)
                if st.session_state.get(f"pdf_data_{candidato.get('id')}") is not None:
                    pdf_data = st.session_state[f"pdf_data_{candidato.get('id')}"]
                    nome_arquivo = st.session_state.get(f"pdf_nome_{candidato.get('id')}", f"ficha_{candidato.get('id')}.pdf")
                    
                    st.download_button(
                        label="📥 📱 BAIXAR FICHA PDF",
                        data=pdf_data,
                        file_name=nome_arquivo,
                        mime="application/pdf",
                        key=f"download_{candidato.get('id')}",
                        type="primary"
                    )
                    
                    st.success(f"✅ PDF pronto: {nome_arquivo}")

# =====================================
# GESTÃO DE VAGAS (nova funcionalidade)
# =====================================

def gerenciar_vagas():
    """Nova funcionalidade para gestão de vagas"""
    st.header("💼 Gestão de Vagas")
    
    # SIDEBAR - FILTROS
    with st.sidebar:
        st.subheader("🔍 Filtros de Vagas")
        
        filtro_status = st.selectbox(
            "Status da vaga:",
            ["Todas", "ativa", "preenchida", "pausada", "cancelada", "em_andamento"]
        )
        
        filtro_urgencia = st.selectbox(
            "Urgência:",
            ["Todas", "imediato", "ate-30-dias", "flexivel"]
        )
        
        filtro_salario_min = st.number_input("Salário mínimo:", min_value=0, value=0)
    
    # CARREGAR VAGAS
    with st.spinner("Carregando vagas..."):
        df_vagas = carregar_vagas()
    
    if df_vagas.empty:
        st.warning("⚠️ Nenhuma vaga encontrada.")
        return
    
    # APLICAR FILTROS
    df_filtrado = df_vagas.copy()
    
    if filtro_status != "Todas":
        df_filtrado = df_filtrado[df_filtrado.get('status_detalhado', df_filtrado.get('status', '')) == filtro_status]
    
    if filtro_urgencia != "Todas":
        df_filtrado = df_filtrado[df_filtrado.get('inicio_urgente', '') == filtro_urgencia]
    
    if filtro_salario_min > 0:
        df_filtrado = df_filtrado[pd.to_numeric(df_filtrado.get('salario_oferecido', 0), errors='coerce') >= filtro_salario_min]
    
    # MÉTRICAS DE VAGAS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Vagas", len(df_vagas))
    
    with col2:
        vagas_ativas = len(df_vagas[df_vagas.get('status_detalhado', df_vagas.get('status', '')) == 'ativa'])
        st.metric("🟢 Ativas", vagas_ativas)
    
    with col3:
        vagas_preenchidas = len(df_vagas[df_vagas.get('status_detalhado', df_vagas.get('status', '')) == 'preenchida'])
        st.metric("✅ Preenchidas", vagas_preenchidas)
    
    with col4:
        vagas_urgentes = len(df_vagas[df_vagas.get('inicio_urgente', '') == 'imediato'])
        st.metric("🔥 Urgentes", vagas_urgentes)
    
    # LISTA DE VAGAS
    st.subheader(f"📋 Vagas Disponíveis ({len(df_filtrado)} encontradas)")
    
    for idx, vaga in df_filtrado.iterrows():
        with st.expander(
            f"{formatar_funcao_vaga(vaga.get('formulario_id', ''))} | "
            f"{vaga.get('nome', '')} {vaga.get('sobrenome', '')} | "
            f"💰 R$ {vaga.get('salario_oferecido', 'N/A')} | "
            f"📍 {vaga.get('cidade', 'N/A')}",
            expanded=False
        ):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # INFORMAÇÕES DA VAGA
                st.write(f"**📧 Email:** {vaga.get('email', 'Não informado')}")
                st.write(f"**📞 Telefone:** {vaga.get('telefone_principal', 'Não informado')}")
                st.write(f"**🏠 Endereço:** {vaga.get('rua_numero', 'Não informado')}")
                st.write(f"**⏰ Urgência:** {vaga.get('inicio_urgente', 'Não informado')}")
                st.write(f"**📄 Regime:** {vaga.get('regime_trabalho', 'Não informado')}")
                
                # STATUS ATUAL
                status_atual = vaga.get('status_detalhado', vaga.get('status', 'ativa'))
                
                if status_atual == 'ativa':
                    st.success(f"🟢 Status: {status_atual}")
                elif status_atual == 'preenchida':
                    st.info(f"✅ Status: {status_atual}")
                elif status_atual == 'pausada':
                    st.warning(f"⏸️ Status: {status_atual}")
                else:
                    st.error(f"🔴 Status: {status_atual}")
            
            with col2:
                # CONTROLES DE STATUS
                st.subheader("🎛️ Controles")
                
                novo_status = st.selectbox(
                    "Alterar status:",
                    ["ativa", "em_andamento", "preenchida", "pausada", "cancelada"],
                    index=["ativa", "em_andamento", "preenchida", "pausada", "cancelada"].index(status_atual),
                    key=f"status_{vaga.get('id')}"
                )
                
                if st.button(f"💾 Atualizar Status", key=f"update_status_{vaga.get('id')}"):
                    if atualizar_status_vaga(vaga.get('id'), novo_status):
                        st.success("✅ Status atualizado!")
                        # Adicionar observação automática
                        obs_status = f"Status alterado para: {novo_status}"
                        adicionar_observacao_vaga(vaga.get('id'), obs_status, 'status_change')
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar")
                
                # BOTÃO GERAR PDF
                if st.button(f"📄 Gerar Ficha Vaga", key=f"pdf_vaga_{vaga.get('id')}"):
                    try:
                        with st.spinner("Gerando PDF da vaga..."):
                            # Usar sistema de PDF existente adaptado para vagas
                            pdf_bytes, nome_arquivo = gerar_ficha_vaga_completa(vaga.to_dict())
                            
                            st.download_button(
                                label="💾 Download Ficha Vaga",
                                data=pdf_bytes,
                                file_name=nome_arquivo,
                                mime="application/pdf",
                                key=f"download_vaga_{vaga.get('id')}"
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar PDF: {str(e)}")
            
            # SEÇÃO DE OBSERVAÇÕES
            st.subheader("📝 Observações e Histórico")
            
            # ADICIONAR NOVA OBSERVAÇÃO
            with st.form(f"obs_form_{vaga.get('id')}"):
                nova_obs = st.text_area("Nova observação:", placeholder="Ex: Enviado candidato João Silva em 15/09/2025")
                
                if st.form_submit_button("➕ Adicionar Observação"):
                    if nova_obs.strip():
                        if adicionar_observacao_vaga(vaga.get('id'), nova_obs):
                            st.success("✅ Observação adicionada!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao adicionar observação")
                    else:
                        st.warning("⚠️ Digite uma observação válida")
            
            # EXIBIR OBSERVAÇÕES EXISTENTES
            observacoes = carregar_observacoes_vaga(vaga.get('id'))
            
            if observacoes:
                st.write("**📚 Histórico de Observações:**")
                for obs in observacoes:
                    data_obs = pd.to_datetime(obs['data_criacao']).strftime('%d/%m/%Y às %H:%M')
                    tipo_icon = {
                        'geral': '📝',
                        'candidato_enviado': '👤',
                        'status_change': '🔄'
                    }.get(obs.get('tipo_observacao', 'geral'), '📝')
                    
                    st.write(f"{tipo_icon} **{data_obs}** - {obs['observacao']}")
            else:
                st.info("ℹ️ Nenhuma observação registrada para esta vaga.")

# =====================================
# GESTÃO DE RELACIONAMENTOS (nova funcionalidade)
# =====================================

def gerenciar_relacionamentos():
    """Funcionalidade para relacionar candidatos com vagas"""
    st.header("🔗 Relacionar Candidatos com Vagas")
    
    # CARREGAR DADOS
    df_candidatos = carregar_candidatos()
    df_vagas = carregar_vagas()
    
    if df_candidatos.empty or df_vagas.empty:
        st.warning("⚠️ É necessário ter candidatos e vagas cadastrados.")
        return
    
    # FORMULÁRIO DE RELACIONAMENTO
    with st.form("relacionar_candidato_vaga"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidato_selecionado = st.selectbox(
                "👤 Selecionar Candidato:",
                options=df_candidatos['id'].tolist(),
                format_func=lambda x: f"{df_candidatos[df_candidatos['id'] == x]['nome_completo'].iloc[0]} - {formatar_funcao(df_candidatos[df_candidatos['id'] == x]['formulario_id'].iloc[0])}"
            )
        
        with col2:
            vaga_selecionada = st.selectbox(
                "💼 Selecionar Vaga:",
                options=df_vagas['id'].tolist(),
                format_func=lambda x: f"{df_vagas[df_vagas['id'] == x]['nome'].iloc[0]} {df_vagas[df_vagas['id'] == x]['sobrenome'].iloc[0]} - {formatar_funcao_vaga(df_vagas[df_vagas['id'] == x]['formulario_id'].iloc[0])}"
            )
        
        observacao_relacao = st.text_area("📝 Observação sobre o envio:", placeholder="Ex: Candidato enviado via WhatsApp às 14h30")
        
        if st.form_submit_button("🔗 Relacionar Candidato com Vaga"):
            if relacionar_candidato_vaga(candidato_selecionado, vaga_selecionada, observacao_relacao):
                st.success("✅ Candidato relacionado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao relacionar (pode já existir esta relação)")
    
    # MOSTRAR RELACIONAMENTOS EXISTENTES
    st.subheader("📊 Relacionamentos Existentes")
    
    df_relacionamentos = carregar_relacionamentos()
    
    if not df_relacionamentos.empty:
        st.dataframe(
            df_relacionamentos[['nome_completo', 'tipo_candidato', 'nome_proprietario', 'tipo_vaga', 'data_envio', 'status_processo']],
            use_container_width=True
        )
    else:
        st.info("ℹ️ Nenhum relacionamento encontrado.")

    # RODAPÉ
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>R.O RECRUTAMENTO</strong> - Dashboard de Gestão</p>
        <p>🔄 Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y às %H:%M')), unsafe_allow_html=True)

# =====================================
# EXECUTAR APLICAÇÃO
# =====================================

if __name__ == "__main__":
    main()# app/streamlit_app.py - VERSÃO EXPANDIDA COM SISTEMA DE VAGAS
import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Adicionar pasta backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato_completa, gerar_ficha_vaga_completa  # ✅ Import para vagas

# Configurar página
st.set_page_config(
    page_title="R.O Recrutamento - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mantendo o padrão existente
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #a65e2e 0%, #d4a574 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #a65e2e;
        margin: 0.5rem 0;
    }
    
    .candidate-card, .vaga-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: #a65e2e;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: #8b4d22;
        color: white;
    }

    .status-ativa {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-preenchida {
        background: #007bff;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-pausada {
        background: #ffc107;
        color: #000;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-cancelada {
        background: #dc3545;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# FUNÇÕES EXISTENTES DE CANDIDATOS (preservadas)
# =====================================

@st.cache_data(ttl=300)
def carregar_candidatos():
    """Carrega candidatos do Supabase com cache"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('candidatos').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar candidatos: {str(e)}")
        return pd.DataFrame()

def atualizar_status_ficha(candidato_id):
    """Atualiza status de ficha_emitida no banco"""
    try:
        supabase = get_supabase_client()
        
        supabase.table('candidatos').update({
            'ficha_emitida': True,
            'data_ficha_gerada': datetime.now().isoformat()
        }).eq('id', candidato_id).execute()
        
        return True
            
    except Exception as e:
        st.error(f"❌ Erro ao atualizar status: {str(e)}")
        return False

def formatar_funcao(formulario_id):
    """Converte ID da função em nome amigável para candidatos"""
    funcoes = {
        'candi-baba': '👶 Babá',
        'candi-caseiro': '🏠 Caseiro',
        'candi-copeiro': '🍷 Copeiro', 
        'candi-cozinheira': '👨‍🍳 Cozinheira(o)',
        'candi-governanta': '👑 Governanta',
        'candi-arrumadeira': '🧹 Arrumadeira',
        'candi-casal': '👫 Casal'
    }
    return funcoes.get(formulario_id, formulario_id or 'Não especificado')

# =====================================
# NOVAS FUNÇÕES PARA SISTEMA DE VAGAS
# =====================================

@st.cache_data(ttl=300)
def carregar_vagas():
    """Carrega vagas do Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('vagas').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar vagas: {str(e)}")
        return pd.DataFrame()

def carregar_observacoes_vaga(vaga_id):
    """Carrega observações de uma vaga específica"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('vaga_observacoes').select('*').eq('vaga_id', vaga_id).order('data_criacao', desc=True).execute()
        
        if response.data:
            return response.data
        else:
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar observações: {str(e)}")
        return []

def adicionar_observacao_vaga(vaga_id, observacao, tipo='geral'):
    """Adiciona nova observação à vaga"""
    try:
        supabase = get_supabase_client()
        
        dados_observacao = {
            'vaga_id': vaga_id,
            'observacao': observacao,
            'tipo_observacao': tipo
        }
        
        result = supabase.table('vaga_observacoes').insert(dados_observacao).execute()
        
        if result.data:
            return True
        return False
        
    except Exception as e:
        st.error(f"❌ Erro ao adicionar observação: {str(e)}")
        return False

def atualizar_status_vaga(vaga_id, novo_status):
    """Atualiza status da vaga"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('vagas').update({
            'status_detalhado': novo_status,
            'updated_at': datetime.now().isoformat()
        }).eq('id', vaga_id).execute()
        
        return result.data is not None
        
    except Exception as e:
        st.error(f"❌ Erro ao atualizar status: {str(e)}")
        return False

def formatar_funcao_vaga(formulario_id):
    """Converte ID da vaga em nome amigável"""
    funcoes = {
        'vaga-baba': '👶 Vaga Babá',
        'vaga-caseiro': '🏠 Vaga Caseiro',
        'vaga-copeiro': '🍷 Vaga Copeiro', 
        'vaga-cozinheira': '👨‍🍳 Vaga Cozinheira(o)',
        'vaga-governanta': '👑 Vaga Governanta',
        'vaga-arrumadeira': '🧹 Vaga Arrumadeira',
        'vaga-domestica': '🏠 Vaga Doméstica'
    }
    return funcoes.get(formulario_id, formulario_id or 'Vaga não especificada')

def relacionar_candidato_vaga(candidato_id, vaga_id, observacao=""):
    """Relaciona candidato com vaga"""
    try:
        supabase = get_supabase_client()
        
        dados_relacao = {
            'candidato_id': candidato_id,
            'vaga_id': vaga_id,
            'observacoes': observacao
        }
        
        result = supabase.table('candidatos_vagas').insert(dados_relacao).execute()
        
        if result.data:
            # Adicionar observação automática na vaga
            obs_automatica = f"Candidato enviado para esta vaga. {observacao}"
            adicionar_observacao_vaga(vaga_id, obs_automatica, 'candidato_enviado')
            return True
        return False
        
    except Exception as e:
        st.error(f"❌ Erro ao relacionar candidato-vaga: {str(e)}")
        return False

def carregar_relacionamentos():
    """Carrega relacionamentos candidatos-vagas"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('candidatos_vagas_detalhado').select('*').order('data_envio', desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar relacionamentos: {str(e)}")
        return pd.DataFrame()

# =====================================
# FUNÇÃO MAIN COM SISTEMA DE ABAS
# =====================================

def main():
    # CABEÇALHO
    st.markdown("""
    <div class="main-header">
        <h1>🏠 R.O RECRUTAMENTO - Dashboard</h1>
        <p>Gerenciamento Completo de Candidatos e Vagas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SISTEMA DE ABAS
    tab1, tab2, tab3 = st.tabs(["👥 Candidatos", "💼 Vagas", "🔗 Relacionamentos"])
    
    with tab1:
        gerenciar_candidatos()
    
    with tab2:
        gerenciar_vagas()
    
    with tab3:
        gerenciar_relacionamentos()

# =====================================
# GESTÃO DE CANDIDATOS (código existente preservado)
# =====================================

def gerenciar_candidatos():
    """Função com código existente dos candidatos - PRESERVADO TOTALMENTE"""
    
    # SIDEBAR - FILTROS
    st.sidebar.header("🔍 Filtros de Candidatos")

    # Filtro de qualificação
    tipo_visualizacao = st.sidebar.selectbox(
        "Visualizar:",
        [
            "Todos os candidatos",
            "Candidatos qualificados", 
            "Pendentes de qualificação"
        ]
    )

    # Carregamento condicional baseado no filtro
    with st.spinner("Carregando candidatos..."):
        df = carregar_candidatos()
        st.header("📋 Candidatos")
    
    if df.empty:
        st.warning("⚠️ Nenhum candidato encontrado no banco de dados.")
        st.info("🔄 Certifique-se que existem candidatos cadastrados no Supabase.")
        return

    # Filtros adicionais na sidebar
    if not df.empty:
        filtro_funcao = st.sidebar.selectbox(
            "Função:",
            ["Todas"] + list(df['formulario_id'].dropna().unique())
        )
        
        filtro_ficha = st.sidebar.selectbox(
            "Status da ficha:",
            ["Todas", "Emitidas", "Pendentes"]
        )

    # Aplicar filtros
    df_filtrado = df.copy()
    
    if filtro_funcao != "Todas":
        df_filtrado = df_filtrado[df_filtrado['formulario_id'] == filtro_funcao]
    
    if filtro_ficha == "Emitidas":
        df_filtrado = df_filtrado[df_filtrado.get('ficha_emitida', False) == True]
    elif filtro_ficha == "Pendentes":
        df_filtrado = df_filtrado[df_filtrado.get('ficha_emitida', False) != True]

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Candidatos", len(df))
    
    with col2:
        fichas_emitidas = len(df[df.get('ficha_emitida', False) == True])
        st.metric("📄 Fichas Emitidas", fichas_emitidas)
    
    with col3:
        fichas_pendentes = len(df) - fichas_emitidas
        st.metric("⏳ Fichas Pendentes", fichas_pendentes)
    
    with col4:
        if not df.empty:
            novos_esta_semana = len(df[pd.to_datetime(df['created_at']).dt.date >= 
                                    (datetime.now().date() - pd.Timedelta(days=7))])
            st.metric("🆕 Novos (7 dias)", novos_esta_semana)

    # Lista de candidatos
    st.subheader(f"👥 Lista de Candidatos ({len(df_filtrado)} encontrados)")
    
    for idx, candidato in df_filtrado.iterrows():
        with st.expander(
            f"{candidato.get('nome_completo', 'Nome não informado')} | "
            f"{formatar_funcao(candidato.get('formulario_id', ''))} | "
            f"📞 {candidato.get('telefone', 'N/A')} | "
            f"📧 {candidato.get('email', 'N/A')}",
            expanded=False
        ):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**📱 WhatsApp:** {candidato.get('whatsapp', candidato.get('telefone', 'N/A'))}")
                st.write(f"**🏠 Endereço:** {candidato.get('endereco', 'Não informado')}")
                st.write(f"**🎂 Nascimento:** {candidato.get('data_nascimento', 'Não informado')}")
                st.write(f"**👶 Filhos:** {'Sim' if candidato.get('tem_filhos') else 'Não'}")
                st.write(f"**🚗 CNH:** {'Sim' if candidato.get('possui_cnh') else 'Não'}")
                
                # Status da ficha
                if candidato.get('ficha_emitida'):
                    st.success(f"✅ Ficha emitida em: {candidato.get('data_ficha_gerada', 'Data não disponível')}")
                else:
                    st.warning("⏳ Ficha pendente de emissão")
            
            with col2:
                st.subheader("🎛️ Ações")
                
                # Botão gerar ficha
                if st.button(f"📄 Gerar Ficha", key=f"ficha_{candidato.get('id')}"):
                    try:
                        with st.spinner("Gerando ficha..."):
                            pdf_bytes, nome_arquivo = gerar_ficha_candidato_completa(candidato.to_dict())
                            
                            # Atualizar status no banco
                            if atualizar_status_ficha(candidato.get('id')):
                                st.success("✅ Status atualizado no banco!")
                            
                            st.download_button(
                                label="💾 Download Ficha",
                                data=pdf_bytes,
                                file_name=nome_arquivo,
                                mime="application/pdf",
                                key=f"download_{candidato.get('id')}"
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar ficha: {str(e)}")

# =====================================
# GESTÃO DE VAGAS (nova funcionalidade)
# =====================================

def gerenciar_vagas():
    """Nova funcionalidade para gestão de vagas"""
    st.header("💼 Gestão de Vagas")
    
    # SIDEBAR - FILTROS
    with st.sidebar:
        st.subheader("🔍 Filtros de Vagas")
        
        filtro_status = st.selectbox(
            "Status da vaga:",
            ["Todas", "ativa", "preenchida", "pausada", "cancelada", "em_andamento"]
        )
        
        filtro_urgencia = st.selectbox(
            "Urgência:",
            ["Todas", "imediato", "ate-30-dias", "flexivel"]
        )
        
        filtro_salario_min = st.number_input("Salário mínimo:", min_value=0, value=0)
    
    # CARREGAR VAGAS
    with st.spinner("Carregando vagas..."):
        df_vagas = carregar_vagas()
    
    if df_vagas.empty:
        st.warning("⚠️ Nenhuma vaga encontrada.")
        return
    
    # APLICAR FILTROS
    df_filtrado = df_vagas.copy()
    
    if filtro_status != "Todas":
        df_filtrado = df_filtrado[df_filtrado.get('status_detalhado', df_filtrado.get('status', '')) == filtro_status]
    
    if filtro_urgencia != "Todas":
        df_filtrado = df_filtrado[df_filtrado.get('inicio_urgente', '') == filtro_urgencia]
    
    if filtro_salario_min > 0:
        df_filtrado = df_filtrado[pd.to_numeric(df_filtrado.get('salario_oferecido', 0), errors='coerce') >= filtro_salario_min]
    
    # MÉTRICAS DE VAGAS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Vagas", len(df_vagas))
    
    with col2:
        vagas_ativas = len(df_vagas[df_vagas.get('status_detalhado', df_vagas.get('status', '')) == 'ativa'])
        st.metric("🟢 Ativas", vagas_ativas)
    
    with col3:
        vagas_preenchidas = len(df_vagas[df_vagas.get('status_detalhado', df_vagas.get('status', '')) == 'preenchida'])
        st.metric("✅ Preenchidas", vagas_preenchidas)
    
    with col4:
        vagas_urgentes = len(df_vagas[df_vagas.get('inicio_urgente', '') == 'imediato'])
        st.metric("🔥 Urgentes", vagas_urgentes)
    
    # LISTA DE VAGAS
    st.subheader(f"📋 Vagas Disponíveis ({len(df_filtrado)} encontradas)")
    
    for idx, vaga in df_filtrado.iterrows():
        with st.expander(
            f"{formatar_funcao_vaga(vaga.get('formulario_id', ''))} | "
            f"{vaga.get('nome', '')} {vaga.get('sobrenome', '')} | "
            f"💰 R$ {vaga.get('salario_oferecido', 'N/A')} | "
            f"📍 {vaga.get('cidade', 'N/A')}",
            expanded=False
        ):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # INFORMAÇÕES DA VAGA
                st.write(f"**📧 Email:** {vaga.get('email', 'Não informado')}")
                st.write(f"**📞 Telefone:** {vaga.get('telefone_principal', 'Não informado')}")
                st.write(f"**🏠 Endereço:** {vaga.get('rua_numero', 'Não informado')}")
                st.write(f"**⏰ Urgência:** {vaga.get('inicio_urgente', 'Não informado')}")
                st.write(f"**📄 Regime:** {vaga.get('regime_trabalho', 'Não informado')}")
                
                # STATUS ATUAL
                status_atual = vaga.get('status_detalhado', vaga.get('status', 'ativa'))
                
                if status_atual == 'ativa':
                    st.success(f"🟢 Status: {status_atual}")
                elif status_atual == 'preenchida':
                    st.info(f"✅ Status: {status_atual}")
                elif status_atual == 'pausada':
                    st.warning(f"⏸️ Status: {status_atual}")
                else:
                    st.error(f"🔴 Status: {status_atual}")
            
            with col2:
                # CONTROLES DE STATUS
                st.subheader("🎛️ Controles")
                
                novo_status = st.selectbox(
                    "Alterar status:",
                    ["ativa", "em_andamento", "preenchida", "pausada", "cancelada"],
                    index=["ativa", "em_andamento", "preenchida", "pausada", "cancelada"].index(status_atual),
                    key=f"status_{vaga.get('id')}"
                )
                
                if st.button(f"💾 Atualizar Status", key=f"update_status_{vaga.get('id')}"):
                    if atualizar_status_vaga(vaga.get('id'), novo_status):
                        st.success("✅ Status atualizado!")
                        # Adicionar observação automática
                        obs_status = f"Status alterado para: {novo_status}"
                        adicionar_observacao_vaga(vaga.get('id'), obs_status, 'status_change')
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar")
                
                # BOTÃO GERAR PDF
                if st.button(f"📄 Gerar Ficha Vaga", key=f"pdf_vaga_{vaga.get('id')}"):
                    try:
                        with st.spinner("Gerando PDF da vaga..."):
                            # Usar sistema de PDF existente adaptado para vagas
                            pdf_bytes, nome_arquivo = gerar_ficha_vaga_completa(vaga.to_dict())
                            
                            st.download_button(
                                label="💾 Download Ficha Vaga",
                                data=pdf_bytes,
                                file_name=nome_arquivo,
                                mime="application/pdf",
                                key=f"download_vaga_{vaga.get('id')}"
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar PDF: {str(e)}")
            
            # SEÇÃO DE OBSERVAÇÕES
            st.subheader("📝 Observações e Histórico")
            
            # ADICIONAR NOVA OBSERVAÇÃO
            with st.form(f"obs_form_{vaga.get('id')}"):
                nova_obs = st.text_area("Nova observação:", placeholder="Ex: Enviado candidato João Silva em 15/09/2025")
                
                if st.form_submit_button("➕ Adicionar Observação"):
                    if nova_obs.strip():
                        if adicionar_observacao_vaga(vaga.get('id'), nova_obs):
                            st.success("✅ Observação adicionada!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao adicionar observação")
                    else:
                        st.warning("⚠️ Digite uma observação válida")
            
            # EXIBIR OBSERVAÇÕES EXISTENTES
            observacoes = carregar_observacoes_vaga(vaga.get('id'))
            
            if observacoes:
                st.write("**📚 Histórico de Observações:**")
                for obs in observacoes:
                    data_obs = pd.to_datetime(obs['data_criacao']).strftime('%d/%m/%Y às %H:%M')
                    tipo_icon = {
                        'geral': '📝',
                        'candidato_enviado': '👤',
                        'status_change': '🔄'
                    }.get(obs.get('tipo_observacao', 'geral'), '📝')
                    
                    st.write(f"{tipo_icon} **{data_obs}** - {obs['observacao']}")
            else:
                st.info("ℹ️ Nenhuma observação registrada para esta vaga.")

# =====================================
# GESTÃO DE RELACIONAMENTOS (nova funcionalidade)
# =====================================

def gerenciar_relacionamentos():
    """Funcionalidade para relacionar candidatos com vagas"""
    st.header("🔗 Relacionar Candidatos com Vagas")
    
    # CARREGAR DADOS
    df_candidatos = carregar_candidatos()
    df_vagas = carregar_vagas()
    
    if df_candidatos.empty or df_vagas.empty:
        st.warning("⚠️ É necessário ter candidatos e vagas cadastrados.")
        return
    
    # FORMULÁRIO DE RELACIONAMENTO
    with st.form("relacionar_candidato_vaga"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidato_selecionado = st.selectbox(
                "👤 Selecionar Candidato:",
                options=df_candidatos['id'].tolist(),
                format_func=lambda x: f"{df_candidatos[df_candidatos['id'] == x]['nome_completo'].iloc[0]} - {formatar_funcao(df_candidatos[df_candidatos['id'] == x]['formulario_id'].iloc[0])}"
            )
        
        with col2:
            vaga_selecionada = st.selectbox(
                "💼 Selecionar Vaga:",
                options=df_vagas['id'].tolist(),
                format_func=lambda x: f"{df_vagas[df_vagas['id'] == x]['nome'].iloc[0]} {df_vagas[df_vagas['id'] == x]['sobrenome'].iloc[0]} - {formatar_funcao_vaga(df_vagas[df_vagas['id'] == x]['formulario_id'].iloc[0])}"
            )
        
        observacao_relacao = st.text_area("📝 Observação sobre o envio:", placeholder="Ex: Candidato enviado via WhatsApp às 14h30")
        
        if st.form_submit_button("🔗 Relacionar Candidato com Vaga"):
            if relacionar_candidato_vaga(candidato_selecionado, vaga_selecionada, observacao_relacao):
                st.success("✅ Candidato relacionado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao relacionar (pode já existir esta relação)")
    
    # MOSTRAR RELACIONAMENTOS EXISTENTES
    st.subheader("📊 Relacionamentos Existentes")
    
    df_relacionamentos = carregar_relacionamentos()
    
    if not df_relacionamentos.empty:
        st.dataframe(
            df_relacionamentos[['nome_completo', 'tipo_candidato', 'nome_proprietario', 'tipo_vaga', 'data_envio', 'status_processo']],
            use_container_width=True
        )
    else:
        st.info("ℹ️ Nenhum relacionamento encontrado.")

# =====================================
# EXECUTAR APLICAÇÃO
# =====================================

if __name__ == "__main__":
    main()