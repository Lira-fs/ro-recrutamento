# app/streamlit_app_fixed.py - VERSÃO CORRIGIDA
import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Adicionar pasta backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato_completa

# Configurar página
st.set_page_config(
    page_title="R.O Recrutamento - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
    
    .candidate-card {
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
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_candidatos():
    """Carrega candidatos do Supabase com cache"""
    try:
        supabase = get_supabase_client()
        
        # Buscar todos os candidatos
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
        
        # Atualizar status
        supabase.table('candidatos').update({
            'ficha_emitida': True,
            'data_ficha_gerada': datetime.now().isoformat()
        }).eq('id', candidato_id).execute()
        
        return True
            
    except Exception as e:
        st.error(f"❌ Erro ao atualizar status: {str(e)}")
        return False

def formatar_funcao(formulario_id):
    """Converte ID da função em nome amigável"""
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

def main():
    # CABEÇALHO
    st.markdown("""
    <div class="main-header">
        <h1>🏠 R.O RECRUTAMENTO - Dashboard</h1>
        <p>Gerenciamento de Candidatos e Geração de Fichas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SIDEBAR - FILTROS
    st.sidebar.header("🔍 Filtros")
    
    # Carregar dados
    with st.spinner("Carregando candidatos..."):
        df = carregar_candidatos()
    
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
    
    # LISTA DE CANDIDATOS
    for idx, candidato in df_filtrado.iterrows():
        with st.expander(
            f"{formatar_funcao(candidato.get('formulario_id', ''))} | "
            f"{candidato.get('nome_completo', 'Nome não informado')} | "
            f"📞 {candidato.get('telefone', 'Tel. não informado')}",
            expanded=False
        ):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Informações básicas
                st.write(f"**📧 Email:** {candidato.get('email', 'Não informado')}")
                st.write(f"**📍 Endereço:** {candidato.get('endereco', 'Não informado')}")
                st.write(f"**👨‍👩‍👧‍👦 Filhos:** {'Sim' if candidato.get('tem_filhos') else 'Não'}")
                st.write(f"**🚗 CNH:** {'Sim' if candidato.get('possui_cnh') else 'Não'}")
                
                if candidato.get('created_at'):
                    data_cadastro = pd.to_datetime(candidato['created_at']).strftime('%d/%m/%Y às %H:%M')
                    st.write(f"**📅 Cadastrado em:** {data_cadastro}")
                
                # Status da ficha
                if candidato.get('ficha_emitida'):
                    st.success("✅ Ficha já gerada")
                    if candidato.get('data_ficha_gerada'):
                        data_ficha = pd.to_datetime(candidato['data_ficha_gerada']).strftime('%d/%m/%Y às %H:%M')
                        st.write(f"**📄 Ficha gerada em:** {data_ficha}")
                else:
                    st.warning("⏳ Ficha pendente")
            
            with col2:
                # Botão para gerar PDF
                nome_arquivo = f"ficha_{candidato.get('nome_completo', 'candidato').replace(' ', '_')}_{candidato.get('id', 'sem_id')}.pdf"
                
                # Armazenar PDF no session_state
                if f"pdf_data_{candidato.get('id')}" not in st.session_state:
                    st.session_state[f"pdf_data_{candidato.get('id')}"] = None
                
                # Botão para gerar PDF
                if st.button(f"📄 Gerar Ficha PDF", key=f"pdf_{candidato.get('id')}"):
                    try:
                        with st.spinner("Gerando PDF..."):
                            
                            st.write("📝 Preparando dados do candidato...")
                            
                            # USAR A FUNÇÃO QUE FUNCIONA
                            pdf_bytes = gerar_ficha_candidato_completa(candidato.to_dict())
                            
                            # Salvar no session_state
                            st.session_state[f"pdf_data_{candidato.get('id')}"] = pdf_bytes
                            
                            st.success(f"✅ PDF gerado! Tamanho: {len(pdf_bytes)} bytes")
                            st.info("👇 Clique no botão verde abaixo para baixar!")
                            
                            # Atualizar status no banco
                            if atualizar_status_ficha(candidato.get('id')):
                                st.success("✅ Status atualizado no banco!")
                                # Limpar cache para atualizar dados
                                st.cache_data.clear()
                            else:
                                st.info("ℹ️ PDF gerado, mas status não atualizado")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                        st.error(f"🔧 Tipo do erro: {type(e).__name__}")
                        
                        # Mostrar detalhes do erro
                        import traceback
                        st.error("Detalhes técnicos:")
                        st.code(traceback.format_exc())
                
                # Botão de download (sempre visível se PDF foi gerado)
                if st.session_state[f"pdf_data_{candidato.get('id')}"] is not None:
                    pdf_data = st.session_state[f"pdf_data_{candidato.get('id')}"]
                    
                    st.download_button(
                        label="📥 📱 BAIXAR FICHA PDF",
                        data=pdf_data,
                        file_name=nome_arquivo,
                        mime="application/pdf",
                        key=f"download_{candidato.get('id')}",
                        type="primary"  # Botão verde destacado
                    )
                    
                    st.success("✅ PDF pronto para download!")
    
    # RODAPÉ
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>R.O RECRUTAMENTO</strong> - Dashboard de Gestão</p>
        <p>🔄 Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y às %H:%M')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()

    