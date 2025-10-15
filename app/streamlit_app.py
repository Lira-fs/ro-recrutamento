import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ✅ 1. CARREGAR VARIÁVEIS DE AMBIENTE PRIMEIRO
from dotenv import load_dotenv
load_dotenv()

# ✅ 2. ADICIONAR PASTA BACKEND AO PATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# ✅ 3. AGORA IMPORTAR DO BACKEND (sem "backend." no import)
from google_drive_backup_oauth import (
    criar_backup_automatico,
    listar_backups_disponiveis,
    GoogleDriveBackupOAuth
)

from auth import verificar_autenticacao, exibir_info_usuario_sidebar
from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato_completa, gerar_ficha_vaga_completa

# ✅ 4. IMPORTS DE SEGURANÇA
from validators import (
    validar_relacionamento_candidato_vaga,
    validar_atualizacao_status_vaga,
    validar_observacao_vaga,
    sanitizar_filtro_busca,
    sanitizar_nome
)

from logger import log_erro, log_aviso, log_info, log_sucesso, log_auditoria

# ✅ 5. IMPORTS DE CRIPTOGRAFIA (SEM "backend.")
from encryption import (
    encrypt_candidato, 
    decrypt_candidato, 
    encrypt_vaga, 
    decrypt_vaga,
    decrypt_lista_candidatos, 
    decrypt_lista_vagas
)


# ============================================
# CONFIGURAÇÃO DA PÁGINA (APENAS UMA VEZ!)
# ============================================

st.set_page_config(
    page_title="R.O Recrutamento - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ⭐ VERIFICAÇÃO DE AUTENTICAÇÃO (NOVO)
# ============================================

# CRÍTICO: Esta linha deve vir ANTES de qualquer outro código
name, username, authenticator = verificar_autenticacao()

# Se chegou aqui, usuário está autenticado! ✅

@st.cache_data(ttl=300)
def carregar_dados_vagas_completo():
    """
    Carrega todas as vagas do sistema
    
    Returns:
        DataFrame: Dados das vagas
    """
    try:
        df_vagas = carregar_vagas()
        return df_vagas
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar dados de vagas",
            excecao=e,
            contexto={}
        )
        return pd.DataFrame()
    
# =====================================
# MÓDULO 1: CARREGAR DADOS DE VAGAS
# =====================================

@st.cache_data(ttl=300)
def carregar_dados_vagas_completo():
    """
    Carrega todas as vagas do sistema
    
    Returns:
        DataFrame: Dados das vagas
    """
    try:
        df_vagas = carregar_vagas()
        return df_vagas
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar dados de vagas",
            excecao=e,
            contexto={}
        )
        return pd.DataFrame()


# =====================================
# MÓDULO 2: SIDEBAR COM FILTROS DE VAGAS
# =====================================

def criar_sidebar_filtros_vagas(df):
    """
    Cria sidebar com todos os filtros de vagas
    
    Args:
        df (DataFrame): DataFrame com vagas
        
    Returns:
        dict: Dicionário com valores dos filtros selecionados
    """
    filtros = {}
    
    with st.sidebar:
        st.header("🔍 Filtros de Vagas")
        
        # Filtro por status
        filtros['status'] = st.selectbox(
            "📊 Status:",
            ["Todas", "ativa", "em_andamento", "preenchida", "pausada", "cancelada"],
            key="filtro_status_vaga"
        )
        
        # Filtro por urgência
        filtros['urgente'] = st.checkbox(
            "🚨 Apenas urgentes",
            key="filtro_urgente"
        )
        
        st.markdown("---")
        
        # Filtros avançados
        if not df.empty:
            with st.expander("🔧 Filtros Avançados", expanded=False):
                
                # Filtro por cidade
                if 'cidade' in df.columns:
                    cidades = ['Todas'] + sorted(
                        df['cidade'].dropna().unique().tolist()
                    )
                    filtros['cidade'] = st.selectbox(
                        "🏙️ Cidade:",
                        cidades,
                        key="filtro_cidade_vaga"
                    )
                else:
                    filtros['cidade'] = "Todas"
                
                # Filtro por tipo de vaga
                if 'formulario_id' in df.columns:
                    tipos = ['Todas'] + sorted(
                        df['formulario_id'].dropna().unique().tolist()
                    )
                    filtros['tipo'] = st.selectbox(
                        "💼 Tipo de vaga:",
                        tipos,
                        format_func=lambda x: formatar_funcao_vaga(x) if x != 'Todas' else x,
                        key="filtro_tipo_vaga"
                    )
                else:
                    filtros['tipo'] = "Todas"
                
                # Filtro por faixa salarial
                if 'salario_oferecido' in df.columns:
                    salarios = pd.to_numeric(df['salario_oferecido'], errors='coerce').dropna()
                    if not salarios.empty:
                        salario_min_val = int(salarios.min())
                        salario_max_val = int(salarios.max())
                        
                        if salario_max_val > salario_min_val:
                            filtros['salario_min'], filtros['salario_max'] = st.slider(
                                "💰 Faixa salarial:",
                                min_value=salario_min_val,
                                max_value=salario_max_val,
                                value=(salario_min_val, salario_max_val),
                                step=100,
                                key="filtro_salario_vaga"
                            )
                        else:
                            filtros['salario_min'] = salario_min_val
                            filtros['salario_max'] = salario_max_val
                    else:
                        filtros['salario_min'] = 0
                        filtros['salario_max'] = 0
                else:
                    filtros['salario_min'] = 0
                    filtros['salario_max'] = 0
                
                # Busca global
                filtros['busca'] = st.text_input(
                    "🔎 Busca geral:",
                    placeholder="Nome do proprietário, cidade...",
                    key="busca_global_vaga"
                )
    
    return filtros

def aplicar_filtros_vagas(df, filtros):
    """
    Aplica todos os filtros selecionados no DataFrame de vagas
    
    Args:
        df (DataFrame): DataFrame original
        filtros (dict): Dicionário com filtros
        
    Returns:
        DataFrame: DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    # Filtro por status
    if filtros.get('status') and filtros['status'] != "Todas":
        status_col = df_filtrado.get('status_detalhado', df_filtrado.get('status', ''))
        df_filtrado = df_filtrado[status_col == filtros['status']]
    
    # Filtro por urgência
    if filtros.get('urgente'):
        df_filtrado = df_filtrado[
            df_filtrado.get('inicio_urgente', '') == 'imediato'
        ]
    
    # Filtro por cidade
    if filtros.get('cidade') and filtros['cidade'] != "Todas":
        if 'cidade' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['cidade'] == filtros['cidade']]
    
    # Filtro por tipo de vaga
    if filtros.get('tipo') and filtros['tipo'] != "Todas":
        if 'formulario_id' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['formulario_id'] == filtros['tipo']]
    
    # Filtro por faixa salarial
    if filtros.get('salario_min') and filtros.get('salario_max'):
        if 'salario_oferecido' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                (pd.to_numeric(df_filtrado['salario_oferecido'], errors='coerce') >= filtros['salario_min']) &
                (pd.to_numeric(df_filtrado['salario_oferecido'], errors='coerce') <= filtros['salario_max'])
            ]
    
    # Busca global
    if filtros.get('busca') and filtros['busca'].strip():
        from validators import sanitizar_filtro_busca
        busca_limpa = sanitizar_filtro_busca(filtros['busca'])
        
        if busca_limpa:
            # Criar coluna temporária com nome completo
            if 'nome_completo_proprietario' not in df_filtrado.columns:
                df_filtrado['nome_completo_proprietario'] = (
                    df_filtrado['nome'].fillna('') + ' ' + 
                    df_filtrado['sobrenome'].fillna('')
                ).str.strip()
            
            mascara_busca = (
                df_filtrado['nome_completo_proprietario'].str.contains(
                    busca_limpa, case=False, na=False
                ) |
                df_filtrado['email'].str.contains(
                    busca_limpa, case=False, na=False
                )
            )
            
            if 'cidade' in df_filtrado.columns:
                mascara_busca |= df_filtrado['cidade'].str.contains(
                    busca_limpa, case=False, na=False
                )
            
            df_filtrado = df_filtrado[mascara_busca]
    
    return df_filtrado

def exibir_metricas_vagas(df):
    """
    Exibe métricas das vagas em cards
    
    Args:
        df (DataFrame): DataFrame com vagas
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Vagas", len(df))
    
    with col2:
        vagas_ativas = len(
            df[df.get('status_detalhado', df.get('status', '')) == 'ativa']
        )
        st.metric("🟢 Ativas", vagas_ativas)
    
    with col3:
        vagas_preenchidas = len(
            df[df.get('status_detalhado', df.get('status', '')) == 'preenchida']
        )
        st.metric("✅ Preenchidas", vagas_preenchidas)
    
    with col4:
        vagas_urgentes = len(df[df.get('inicio_urgente', '') == 'imediato'])
        st.metric("🔥 Urgentes", vagas_urgentes)
        
def exibir_card_vaga(vaga, idx):
    """
    Exibe card individual de uma vaga com todas as informações e ações
    
    Args:
        vaga (dict): Dados da vaga
        idx (int): Índice para keys únicas
    """
    vaga_id = vaga.get('id')
    
    # Obter status formatado
    status_atual = vaga.get('status_detalhado', vaga.get('status', 'ativa'))
    status_display, status_color = formatar_status_vaga(status_atual)
    
    # Título do expander
    titulo_expander = (
        f"{formatar_funcao_vaga(vaga.get('formulario_id', ''))} | "
        f"{vaga.get('nome', '')} {vaga.get('sobrenome', '')} | "
        f"💰 R$ {vaga.get('salario_oferecido', 'N/A')} | "
        f"📍 {vaga.get('cidade', 'N/A')} | "
        f"{status_display}"
    )
    
    with st.expander(titulo_expander, expanded=False):
        
        col1, col2 = st.columns([2, 1])
        
        # ===== COLUNA 1: INFORMAÇÕES DA VAGA =====
        with col1:
            st.write(f"**📧 Email:** {vaga.get('email', 'Não informado')}")
            st.write(f"**📞 Telefone:** {vaga.get('telefone_principal', 'Não informado')}")
            st.write(f"**🏠 Endereço:** {vaga.get('rua_numero', 'Não informado')}")
            st.write(f"**⏰ Urgência:** {vaga.get('inicio_urgente', 'Não informado')}")
            st.write(f"**📄 Regime:** {vaga.get('regime_trabalho', 'Não informado')}")
            
            # Data de cadastro
            if vaga.get('created_at'):
                data_cadastro = pd.to_datetime(vaga['created_at']).strftime('%d/%m/%Y às %H:%M')
                st.write(f"**📅 Cadastrada em:** {data_cadastro}")
        
        # ===== COLUNA 2: CONTROLES =====
        with col2:
            st.subheader("🎛️ Controles")
            
            # Selectbox de status
            novo_status = st.selectbox(
                "Alterar status:",
                ["ativa", "em_andamento", "preenchida", "pausada", "cancelada"],
                index=["ativa", "em_andamento", "preenchida", "pausada", "cancelada"].index(status_atual),
                key=f"status_{vaga_id}_{idx}"
            )
            
            # Botão atualizar status
            if st.button(f"💾 Atualizar Status", key=f"update_status_{vaga_id}_{idx}"):
                if atualizar_status_vaga(vaga_id, novo_status):
                    st.success("✅ Status atualizado!")
                    # Adicionar observação automática
                    obs_status = f"Status alterado para: {novo_status}"
                    adicionar_observacao_vaga(vaga_id, obs_status, 'status_change')
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar")
            
            st.markdown("---")
            
            # Botão gerar PDF
            exibir_botao_gerar_pdf_vaga(vaga, idx)
        
        st.markdown("---")
        
        # ===== SEÇÃO DE OBSERVAÇÕES =====
        exibir_secao_observacoes_vaga(vaga, idx)


# =====================================
# MÓDULO 5A: BOTÃO GERAR PDF DE VAGA
# =====================================

def exibir_botao_gerar_pdf_vaga(vaga, idx):
    """
    Exibe botão para gerar PDF da vaga
    
    Args:
        vaga (dict): Dados da vaga
        idx (int): Índice para keys únicas
    """
    vaga_id = vaga.get('id')
    
    if st.button("📄 Gerar Ficha Vaga", key=f"pdf_vaga_{vaga_id}_{idx}", type="primary"):
        try:
            with st.spinner("Gerando PDF da vaga..."):
                # Usar sistema de PDF existente adaptado para vagas
                pdf_bytes, nome_arquivo = gerar_ficha_vaga_completa(vaga)
                
                st.download_button(
                    label="💾 Download Ficha Vaga",
                    data=pdf_bytes,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    key=f"download_vaga_{vaga_id}_{idx}",
                    type="primary",
                    use_container_width=True
                )
                
                st.success("✅ PDF gerado! Clique acima para baixar.")
                
        except Exception as e:
            log_erro(
                mensagem_usuario="Erro ao gerar PDF da vaga",
                excecao=e,
                contexto={
                    'vaga_id': vaga_id,
                    'proprietario': f"{vaga.get('nome', '')} {vaga.get('sobrenome', '')}"
                }
            )

def exibir_secao_observacoes_vaga(vaga, idx):
    """
    Exibe seção de observações da vaga com formulário e histórico
    
    Args:
        vaga (dict): Dados da vaga
        idx (int): Índice para keys únicas
    """
    vaga_id = vaga.get('id')
    
    st.subheader("📝 Observações e Histórico")
    
    # ===== ADICIONAR NOVA OBSERVAÇÃO =====
    with st.form(f"obs_form_{vaga_id}_{idx}"):
        nova_obs = st.text_area(
            "Nova observação:",
            placeholder="Ex: Enviado candidato João Silva em 15/09/2025",
            key=f"nova_obs_{vaga_id}_{idx}"
        )
        
        submitted = st.form_submit_button("➕ Adicionar Observação")
        
        if submitted:
            if nova_obs.strip():
                if adicionar_observacao_vaga(vaga_id, nova_obs):
                    st.success("✅ Observação adicionada!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Erro ao adicionar observação")
            else:
                st.warning("⚠️ Digite uma observação válida")
    
    # ===== EXIBIR OBSERVAÇÕES EXISTENTES =====
    observacoes = carregar_observacoes_vaga(vaga_id)
    
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
        
def gerenciar_vagas():
    """
    Função orquestradora de gestão de vagas
    MODULARIZADA - Apenas coordena os módulos
    """
    
    st.header("💼 Gestão de Vagas")
    
    # 1. CARREGAR DADOS
    with st.spinner("Carregando vagas..."):
        df_vagas = carregar_dados_vagas_completo()
    
    if df_vagas.empty:
        st.warning("⚠️ Nenhuma vaga encontrada.")
        return
    
    # 2. CRIAR SIDEBAR COM FILTROS
    filtros = criar_sidebar_filtros_vagas(df_vagas)
    
    # 3. EXIBIR MÉTRICAS
    exibir_metricas_vagas(df_vagas)
    
    st.markdown("---")
    
    # 4. APLICAR FILTROS
    df_filtrado = aplicar_filtros_vagas(df_vagas, filtros)
    
    # 5. EXIBIR RESULTADOS
    st.subheader(f"📋 Vagas Disponíveis ({len(df_filtrado)} encontradas)")
    
    if df_filtrado.empty:
        st.info("🔍 Nenhuma vaga encontrada com os filtros aplicados.")
        return
    
    # 6. LISTA DE CARDS
    for idx, vaga in enumerate(df_filtrado.to_dict('records')):
        exibir_card_vaga(vaga, idx)

# =====================================
# CSS PERSONALIZADO
# =====================================

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
</style>
""", unsafe_allow_html=True)

# =====================================
# FUNÇÕES DE CANDIDATOS (PRESERVADAS 100%)
# =====================================

@st.cache_data(ttl=300)
def carregar_candidatos(
    limite=100, 
    offset=0, 
    filtros=None, 
    retornar_contagem=False
):
    """
    Carrega candidatos do Supabase com paginação e filtros otimizados
    
    Args:
        limite (int): Número máximo de registros a retornar (padrão: 100)
        offset (int): Número de registros a pular para paginação (padrão: 0)
        filtros (dict): Dicionário com filtros opcionais:
            - 'funcao': str - Filtrar por formulario_id
            - 'cidade': str - Filtrar por cidade
            - 'status': str - Filtrar por status_candidato
            - 'busca': str - Busca em nome_completo, email, telefone
        retornar_contagem (bool): Se True, retorna (DataFrame, total_count)
    
    Returns:
        pd.DataFrame ou tuple(pd.DataFrame, int): Dados dos candidatos e opcionalmente contagem total
    """
    try:
        # ✅ SANITIZAR FILTROS PRIMEIRO
        from validators import validar_e_sanitizar_filtros_query
        
        if filtros:
            valido, filtros_limpos, msg = validar_e_sanitizar_filtros_query(filtros)
            if not valido:
                st.error(f"Filtros inválidos: {msg}")
                if retornar_contagem:
                    return pd.DataFrame(), 0
                return pd.DataFrame()
        else:
            filtros_limpos = {}
        
        supabase = get_supabase_client()
        
        # Iniciar query
        if retornar_contagem:
            query = supabase.table('candidatos').select('*', count='exact')
        else:
            query = supabase.table('candidatos').select('*')
        
        # ✅ USAR FILTROS SANITIZADOS
        if filtros_limpos:
            if filtros_limpos.get('funcao') and filtros_limpos['funcao'] != 'Todas':
                query = query.eq('formulario_id', filtros_limpos['funcao'])
            
            if filtros_limpos.get('cidade') and filtros_limpos['cidade'] != 'Todas':
                query = query.eq('cidade', filtros_limpos['cidade'])
            
            if filtros_limpos.get('status') and filtros_limpos['status'] != 'Todos':
                query = query.eq('status_candidato', filtros_limpos['status'])
                        
            # Busca textual (nome, email, telefone)
            # Nota: Supabase não tem busca LIKE em múltiplos campos nativamente
            # Então faremos busca em Python após carregar (ainda otimizado pelo limite)
        
        # APLICAR PAGINAÇÃO (sempre aplica range, mesmo sem filtros)
        query = query.range(offset, offset + limite - 1)
        
        # ORDENAR por data de criação (mais recentes primeiro)
        query = query.order('created_at', desc=True)
        
        # EXECUTAR query
        response = query.execute()
        
        # Criar DataFrame
        if response.data:
            dados_descriptografados = decrypt_lista_candidatos(response.data)
            df = pd.DataFrame(dados_descriptografados)
            
            
            # BUSCA TEXTUAL (se fornecida) - aplicada após query otimizada
            if filtros and filtros.get('busca'):
                busca_termo = filtros['busca'].lower()
                mascara = (
                    df['nome_completo'].str.lower().str.contains(busca_termo, na=False) |
                    df['email'].str.lower().str.contains(busca_termo, na=False)
                )
                # Adicionar telefone se coluna existe
                if 'telefone' in df.columns:
                    mascara |= df['telefone'].astype(str).str.contains(busca_termo, na=False)
                
                df = df[mascara]
        else:
            df = pd.DataFrame()
        
        # RETORNAR com ou sem contagem
        if retornar_contagem:
            total_count = response.count if hasattr(response, 'count') else len(df)
            return df, total_count
        else:
            return df
            
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar candidatos",
            excecao=e,
            contexto={
                'limite': limite,
                'offset': offset,
                'tem_filtros': bool(filtros)
            }
        )
        if retornar_contagem:
            return pd.DataFrame(), 0
        return pd.DataFrame()

def exibir_paginacao(total_registros, registros_por_pagina=100, key_prefix=""):
    """
    Exibe controles de paginação e retorna página atual e offset
    
    Args:
        total_registros (int): Total de registros disponíveis
        registros_por_pagina (int): Quantos registros por página
        key_prefix (str): Prefixo para keys únicos do Streamlit
    
    Returns:
        tuple(int, int): (pagina_atual, offset)
    """
    total_paginas = (total_registros // registros_por_pagina) + (1 if total_registros % registros_por_pagina > 0 else 0)
    
    if total_paginas > 1:
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        
        # Garantir que página atual existe no session_state
        if f"{key_prefix}_pagina_atual" not in st.session_state:
            st.session_state[f"{key_prefix}_pagina_atual"] = 1
        
        pagina_atual = st.session_state[f"{key_prefix}_pagina_atual"]
        
        with col_prev:
            if pagina_atual > 1:
                if st.button("⬅️ Anterior", key=f"{key_prefix}_prev"):
                    st.session_state[f"{key_prefix}_pagina_atual"] -= 1
                    st.rerun()
        
        with col_info:
            st.write(f"**Página {pagina_atual} de {total_paginas}** ({total_registros} total)")
        
        with col_next:
            if pagina_atual < total_paginas:
                if st.button("Próxima ➡️", key=f"{key_prefix}_next"):
                    st.session_state[f"{key_prefix}_pagina_atual"] += 1
                    st.rerun()
        
        offset = (pagina_atual - 1) * registros_por_pagina
        return pagina_atual, offset
    else:
        return 1, 0

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

@st.cache_data(ttl=300)
def carregar_candidatos_qualificados(limite=100, offset=0, retornar_contagem=False):
    """Carrega candidatos qualificados usando dados combinados otimizados"""
    try:
        supabase = get_supabase_client()
        
        # 1. Buscar IDs de candidatos qualificados com paginação
        if retornar_contagem:
            query_qual = supabase.table('candidatos_qualificados').select('*', count='exact')
        else:
            query_qual = supabase.table('candidatos_qualificados').select('*')
        
        query_qual = query_qual.range(offset, offset + limite - 1).order('data_qualificacao', desc=True)
        qualificacoes_response = query_qual.execute()
        
        if not qualificacoes_response.data:
            if retornar_contagem:
                return pd.DataFrame(), 0
            return pd.DataFrame()
        
        # 2. Extrair IDs dos candidatos qualificados
        candidato_ids = [q['candidato_id'] for q in qualificacoes_response.data]
        
        # 3. Buscar dados completos dos candidatos (1 query com IN)
        candidatos_response = supabase.table('candidatos').select('*').in_('id', candidato_ids).execute()
        
        if not candidatos_response.data:
            if retornar_contagem:
                return pd.DataFrame(), qualificacoes_response.count if hasattr(qualificacoes_response, 'count') else 0
            return pd.DataFrame()
        
        # 4. Criar lookup de candidatos por ID
        candidatos_dict = {c['id']: c for c in candidatos_response.data}
        
        # 5. Combinar dados (em memória, rápido)
        dados_combinados = []
        for qualificacao in qualificacoes_response.data:
            candidato_id = qualificacao['candidato_id']
            if candidato_id in candidatos_dict:
                candidato_completo = candidatos_dict[candidato_id].copy()
                candidato_completo.update({
                    'data_qualificacao': qualificacao.get('data_qualificacao'),
                    'nota_treinamento': qualificacao.get('nota_treinamento'),
                    'certificado_emitido': qualificacao.get('certificado_emitido'),
                    'certificado_numero': qualificacao.get('certificado_numero'),
                    'instrutor_responsavel': qualificacao.get('instrutor_responsavel')
                })
                dados_combinados.append(candidato_completo)
        
        dados_descriptografados = decrypt_lista_candidatos(dados_combinados)
        df = pd.DataFrame(dados_descriptografados)
        
        if retornar_contagem:
            total = qualificacoes_response.count if hasattr(qualificacoes_response, 'count') else len(df)
            return df, total
        
        return df
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar candidatos pendentes",
            excecao=e,
            contexto={'limite': limite, 'offset': offset}
        )
        if retornar_contagem:
            return pd.DataFrame(), 0
        return pd.DataFrame()
    
@st.cache_data(ttl=300)
def carregar_candidatos_pendentes(limite=100, offset=0, retornar_contagem=False):
    """Carrega candidatos pendentes usando LEFT JOIN no banco"""
    try:
        supabase = get_supabase_client()
        
        # Query otimizada: LEFT JOIN que retorna apenas candidatos SEM qualificação
        query = """
        SELECT c.*
        FROM candidatos c
        LEFT JOIN candidatos_qualificados q ON c.id = q.candidato_id
        WHERE q.candidato_id IS NULL
        ORDER BY c.created_at DESC
        """
        
        # Supabase não suporta SQL direto via PostgREST nativamente
        # Solução: usar filtro NOT IN com IDs qualificados
        
        # 1. Buscar IDs qualificados (query pequena)
        qualificados = supabase.table('candidatos_qualificados').select('candidato_id').execute()
        ids_qualificados = [q['candidato_id'] for q in qualificados.data] if qualificados.data else []
        
        # 2. Buscar candidatos excluindo IDs qualificados
        if retornar_contagem:
            query = supabase.table('candidatos').select('*', count='exact')
        else:
            query = supabase.table('candidatos').select('*')
        
        # Aplicar filtro NOT IN (se houver qualificados)
        if ids_qualificados:
            query = query.not_.in_('id', ids_qualificados)
        
        # Paginação
        query = query.range(offset, offset + limite - 1).order('created_at', desc=True)
        
        response = query.execute()
        
        if retornar_contagem:
            total = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
            return pd.DataFrame(response.data) if response.data else pd.DataFrame(), total
        
        if response.data:
            dados_descriptografados = decrypt_lista_candidatos(response.data)
            return pd.DataFrame(dados_descriptografados)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar candidatos pendentes: {str(e)}")
        if retornar_contagem:
            return pd.DataFrame(), 0
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
# FUNÇÕES DE MÉTRICAS DE NEGÓCIO
# =====================================

def calcular_metricas_negocio(data_limite):
    """Calcula métricas com queries otimizadas"""
    try:
        supabase = get_supabase_client()
        
        # 1. Total candidatos/vagas no período
        candidatos_periodo = supabase.table('candidatos').select('id', count='exact').gte('created_at', data_limite.isoformat()).execute()
        vagas_periodo = supabase.table('vagas').select('id', count='exact').gte('created_at', data_limite.isoformat()).execute()
        
        # 2. Relacionamentos no período
        relacionamentos_periodo = supabase.table('candidatos_vagas').select('*').gte('data_envio', data_limite.isoformat()).execute()
        total_processos = len(relacionamentos_periodo.data) if relacionamentos_periodo.data else 0
        
        # Contar por status
        contratacoes = len([r for r in relacionamentos_periodo.data if r.get('status_processo') == 'contratado']) if relacionamentos_periodo.data else 0
        rejeicoes = len([r for r in relacionamentos_periodo.data if r.get('status_processo') == 'rejeitado']) if relacionamentos_periodo.data else 0
        
        # 3. Taxa de conversão
        taxa_conversao = (contratacoes / total_processos * 100) if total_processos > 0 else 0
        
        # 4. Tempo médio de processo
        tempos_processo = []
        if relacionamentos_periodo.data:
            for rel in relacionamentos_periodo.data:
                if rel.get('status_processo') in ['contratado', 'rejeitado', 'finalizado']:
                    data_envio = pd.to_datetime(rel.get('data_envio'))
                    data_update = pd.to_datetime(rel.get('updated_at', rel.get('data_envio')))
                    tempo_dias = (data_update - data_envio).days
                    tempos_processo.append(max(1, tempo_dias))
        
        tempo_medio = sum(tempos_processo) / len(tempos_processo) if tempos_processo else 0
        
        # 5. Funções mais demandadas - OTIMIZADO
        funcoes_vagas = {}
        if relacionamentos_periodo.data:
            # CARREGAR TODAS AS VAGAS DE UMA VEZ (1 query apenas)
            vaga_ids = list(set([r.get('vaga_id') for r in relacionamentos_periodo.data if r.get('vaga_id')]))
            
            if vaga_ids:
                vagas_info = supabase.table('vagas').select('id, formulario_id').in_('id', vaga_ids).execute()
                
                # Criar dicionário de lookup {vaga_id: formulario_id}
                vaga_lookup = {v['id']: v['formulario_id'] for v in vagas_info.data} if vagas_info.data else {}
                
                # Contar funções usando lookup (em memória, rápido)
                for rel in relacionamentos_periodo.data:
                    vaga_id = rel.get('vaga_id')
                    if vaga_id and vaga_id in vaga_lookup:
                        funcao = vaga_lookup[vaga_id]
                        funcoes_vagas[funcao] = funcoes_vagas.get(funcao, 0) + 1
        
        # 6. Motivos de rejeição
        motivos_rejeicao = [
            rel.get('observacoes', '') 
            for rel in relacionamentos_periodo.data 
            if rel.get('status_processo') == 'rejeitado' and rel.get('observacoes')
        ] if relacionamentos_periodo.data else []
        
        return {
            'total_candidatos': candidatos_periodo.count,
            'total_vagas': vagas_periodo.count,
            'total_processos': total_processos,
            'contratacoes': contratacoes,
            'rejeicoes': rejeicoes,
            'taxa_conversao': taxa_conversao,
            'tempo_medio': tempo_medio,
            'funcoes_demandadas': dict(sorted(funcoes_vagas.items(), key=lambda x: x[1], reverse=True)[:5]),
            'motivos_rejeicao': motivos_rejeicao
        }
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao calcular métricas de negócio",
            excecao=e,
            contexto={'data_limite': data_limite.isoformat()}
        )
    return {
        'total_candidatos': 0,
        'total_vagas': 0,
        'total_processos': 0,
        'contratacoes': 0,
        'rejeicoes': 0,
        'taxa_conversao': 0,
        'tempo_medio': 0,
        'funcoes_demandadas': {},
        'motivos_rejeicao': []
    }
    
def exibir_dashboard_metricas(metricas, periodo_nome):
    """Exibe dashboard de métricas de negócio"""
    
    st.markdown("---")
    st.header(f"📊 Métricas de Negócio - {periodo_nome}")
    
    # Cards de métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Candidatos",
            metricas['total_candidatos'],
            help="Total de candidatos cadastrados no período"
        )
    
    with col2:
        st.metric(
            "💼 Vagas",
            metricas['total_vagas'],
            help="Total de vagas criadas no período"
        )
    
    with col3:
        st.metric(
            "✅ Taxa Conversão",
            f"{metricas['taxa_conversao']:.1f}%",
            help="Percentual de processos que resultaram em contratação"
        )
    
    with col4:
        st.metric(
            "⏱️ Tempo Médio",
            f"{metricas['tempo_medio']:.0f} dias",
            help="Tempo médio dos processos finalizados"
        )
    
    # Segunda linha de métricas
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "🔄 Processos Ativos",
            metricas['total_processos'],
            help="Total de relacionamentos candidato-vaga no período"
        )
    
    with col6:
        st.metric(
            "🎉 Contratações",
            metricas['contratacoes'],
            help="Total de candidatos contratados"
        )
    
    with col7:
        st.metric(
            "❌ Rejeições",
            metricas['rejeicoes'],
            help="Total de candidatos rejeitados"
        )
    
    with col8:
        processos_pendentes = metricas['total_processos'] - metricas['contratacoes'] - metricas['rejeicoes']
        st.metric(
            "⏳ Em Andamento",
            processos_pendentes,
            help="Processos ainda em andamento"
        )
    
    # Gráficos e análises
    if metricas['total_processos'] > 0:
        st.markdown("---")
        
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            st.subheader("🔝 Top 5 Funções Mais Demandadas")
            if metricas['funcoes_demandadas']:
                funcoes_df = pd.DataFrame([
                    {'Função': formatar_funcao_vaga(k), 'Quantidade': v} 
                    for k, v in metricas['funcoes_demandadas'].items()
                ])
                st.bar_chart(funcoes_df.set_index('Função'), height=300)
            else:
                st.info("📊 Dados insuficientes para gerar gráfico")
        
        with col_grafico2:
            st.subheader("📈 Distribuição de Resultados")
            
            # Gráfico de pizza com resultados
            resultados_data = {
                'Contratados': metricas['contratacoes'],
                'Rejeitados': metricas['rejeicoes'],
                'Em Andamento': processos_pendentes
            }
            
            # Filtrar apenas valores > 0
            resultados_filtrados = {k: v for k, v in resultados_data.items() if v > 0}
            
            if resultados_filtrados:
                resultados_df = pd.DataFrame([
                    {'Status': k, 'Quantidade': v} 
                    for k, v in resultados_filtrados.items()
                ])
                st.bar_chart(resultados_df.set_index('Status'), height=300)
            else:
                st.info("📊 Dados insuficientes para gerar gráfico")
        
        # Análise de motivos de rejeição
        if metricas['motivos_rejeicao']:
            st.subheader("❌ Principais Motivos de Rejeição")
            
            # Analisar palavras-chave nos motivos
            palavras_comuns = {}
            for motivo in metricas['motivos_rejeicao']:
                palavras = motivo.lower().split()
                for palavra in palavras:
                    if len(palavra) > 3:  # Ignorar palavras muito curtas
                        palavra_limpa = palavra.strip('.,!?;:')
                        if palavra_limpa in ['experiência', 'perfil', 'rejeitou', 'solicitou', 'cliente']:
                            palavras_comuns[palavra_limpa] = palavras_comuns.get(palavra_limpa, 0) + 1
            
            if palavras_comuns:
                top_palavras = dict(sorted(palavras_comuns.items(), key=lambda x: x[1], reverse=True)[:5])
                col_palavra1, col_palavra2 = st.columns(2)
                
                with col_palavra1:
                    for palavra, freq in top_palavras.items():
                        st.write(f"🔸 **{palavra.title()}**: {freq}x mencionado")
                
                with col_palavra2:
                    st.write("**💡 Insights:**")
                    if 'experiência' in top_palavras:
                        st.write("• Focar em candidatos com mais experiência")
                    if 'perfil' in top_palavras:
                        st.write("• Melhorar triagem de perfis")
                    if 'cliente' in top_palavras:
                        st.write("• Alinhar melhor expectativas com clientes")
            else:
                st.info("📝 Análise de motivos requer mais dados")
    else:
        st.info("📊 Não há dados suficientes para gerar métricas no período selecionado")

def aplicar_filtros_avancados_candidatos(df_candidatos):
    """Aplica filtros avançados para candidatos de forma organizada"""
    
    # EXPANDER para filtros avançados na sidebar
    with st.sidebar.expander("🔍 Filtros Avançados", expanded=False):
        
        df_filtrado = df_candidatos.copy()
        
        # Filtro por cidade
        if 'cidade' in df_candidatos.columns:
            cidades_disponiveis = sorted(df_candidatos['cidade'].dropna().unique().tolist())
            if cidades_disponiveis:
                filtro_cidade = st.multiselect(
                    "🏙️ Cidade:",
                    cidades_disponiveis,
                    key="filtro_cidade_avancado"
                )
                if filtro_cidade:
                    df_filtrado = df_filtrado[df_filtrado['cidade'].isin(filtro_cidade)]
        
        # Filtro por status do candidato
        if 'status_candidato' in df_candidatos.columns:
            status_candidato = st.selectbox(
                "📋 Status:",
                ["Todos", "disponivel", "em_processo", "contratado", "inativo"],
                key="filtro_status_candidato"
            )
            if status_candidato != "Todos":
                df_filtrado = df_filtrado[df_filtrado['status_candidato'] == status_candidato]
        
        # Filtro por função
        if 'formulario_id' in df_candidatos.columns:
            funcoes_disponiveis = sorted(df_candidatos['formulario_id'].dropna().unique().tolist())
            if funcoes_disponiveis:
                filtro_funcao = st.multiselect(
                    "💼 Função:",
                    funcoes_disponiveis,
                    format_func=lambda x: formatar_funcao(x),
                    key="filtro_funcao_avancado"
                )
                if filtro_funcao:
                    df_filtrado = df_filtrado[df_filtrado['formulario_id'].isin(filtro_funcao)]
        
        # Busca global
        busca_global = st.text_input(
            "🔍 Busca geral:",
            placeholder="Nome, email, cidade...",
            key="busca_global_candidatos"
        )
        
        if busca_global.strip():
            # ✅ SANITIZAR BUSCA
            from validators import sanitizar_filtro_busca
            busca_limpa = sanitizar_filtro_busca(busca_global)
            
            if not busca_limpa:
                st.warning("⚠️ Termo de busca contém caracteres inválidos")
                return df_filtrado
            
            # ✅ USAR BUSCA SANITIZADA
            mascara_busca = (
                df_filtrado['nome_completo'].str.contains(busca_limpa, case=False, na=False) |
                df_filtrado['email'].str.contains(busca_limpa, case=False, na=False)
            )
            
            # Adicionar busca por cidade se disponível
            if 'cidade' in df_filtrado.columns:
                mascara_busca |= df_filtrado['cidade'].str.contains(busca_global, case=False, na=False)
            
            # Adicionar busca por telefone se disponível
            if 'telefone' in df_filtrado.columns:
                mascara_busca |= df_filtrado['telefone'].str.contains(busca_global, case=False, na=False)
                
            df_filtrado = df_filtrado[mascara_busca]
    
    return df_filtrado

def aplicar_filtros_avancados_vagas(df_vagas):
    """Aplica filtros avançados para vagas de forma organizada"""
    
    # EXPANDER para filtros avançados na sidebar
    with st.sidebar.expander("🔍 Filtros Avançados", expanded=False):
        
        df_filtrado = df_vagas.copy()
        
        # Filtro por faixa salarial
        if 'salario_oferecido' in df_vagas.columns:
            salarios = pd.to_numeric(df_vagas['salario_oferecido'], errors='coerce').dropna()
            if not salarios.empty:
                salario_min_val = int(salarios.min())
                salario_max_val = int(salarios.max())
                
                if salario_max_val > salario_min_val:
                    salario_min, salario_max = st.slider(
                        "💰 Faixa salarial:",
                        min_value=salario_min_val,
                        max_value=salario_max_val,
                        value=(salario_min_val, salario_max_val),
                        step=100,
                        key="filtro_salario_avancado"
                    )
                    
                    df_filtrado = df_filtrado[
                        (pd.to_numeric(df_filtrado['salario_oferecido'], errors='coerce') >= salario_min) &
                        (pd.to_numeric(df_filtrado['salario_oferecido'], errors='coerce') <= salario_max)
                    ]
        
        # Filtro por status da vaga
        status_vaga = st.selectbox(
            "📊 Status:",
            ["Todas", "ativa", "em_andamento", "preenchida", "pausada", "cancelada"],
            key="filtro_status_vaga_avancado"
        )
        if status_vaga != "Todas":
            df_filtrado = df_filtrado[
                df_filtrado.get('status_detalhado', df_filtrado.get('status', '')) == status_vaga
            ]
        
        # Filtro por urgência
        filtro_urgencia = st.checkbox(
            "🚨 Apenas urgentes",
            key="filtro_urgencia_avancado"
        )
        if filtro_urgencia:
            df_filtrado = df_filtrado[df_filtrado.get('inicio_urgente', '') == 'imediato']
        
        # Filtro por cidade da vaga
        if 'cidade' in df_vagas.columns:
            cidades_vagas = sorted(df_vagas['cidade'].dropna().unique().tolist())
            if cidades_vagas:
                filtro_cidade_vaga = st.multiselect(
                    "🏙️ Cidade:",
                    cidades_vagas,
                    key="filtro_cidade_vaga"
                )
                if filtro_cidade_vaga:
                    df_filtrado = df_filtrado[df_filtrado['cidade'].isin(filtro_cidade_vaga)]
        
        # Busca global para vagas
        busca_global_vagas = st.text_input(
            "🔍 Busca geral:",
            placeholder="Proprietário, cidade...",
            key="busca_global_vagas"
        )
        
        if busca_global_vagas.strip():
            # ✅ SANITIZAR BUSCA
            from validators import sanitizar_filtro_busca
            busca_limpa = sanitizar_filtro_busca(busca_global_vagas)
            
            if not busca_limpa:
                st.warning("⚠️ Termo de busca contém caracteres inválidos")
                return df_filtrado
            
            # Criar coluna se não existir
            if 'nome_completo_proprietario' not in df_filtrado.columns:
                df_filtrado['nome_completo_proprietario'] = (
                    df_filtrado['nome'].fillna('') + ' ' + df_filtrado['sobrenome'].fillna('')
                ).str.strip()
            
            # ✅ USAR BUSCA SANITIZADA
            mascara_busca = (
                df_filtrado['nome_completo_proprietario'].str.contains(busca_limpa, case=False, na=False) |
                df_filtrado['email'].str.contains(busca_limpa, case=False, na=False)
            )
            
            # Adicionar busca por cidade se disponível
            if 'cidade' in df_filtrado.columns:
                mascara_busca |= df_filtrado['cidade'].str.contains(busca_global_vagas, case=False, na=False)
                
            df_filtrado = df_filtrado[mascara_busca]
    
    return df_filtrado

def expirar_relacionamentos_antigos():
    """Função para verificar e expirar relacionamentos antigos (90+ dias)"""
    try:
        supabase = get_supabase_client()
        
        # Data limite: 90 dias atrás
        data_limite = (datetime.now() - timedelta(days=90)).isoformat()
        
        # Buscar relacionamentos antigos que ainda estão ativos
        relacionamentos_antigos = supabase.table('candidatos_vagas').select('*').lt('data_envio', data_limite).not_.in_('status_processo', ['finalizado', 'expirado', 'contratado']).execute()
        
        if relacionamentos_antigos.data:
            count_expirados = 0
            
            for rel in relacionamentos_antigos.data:
                # Marcar como expirado
                resultado = supabase.table('candidatos_vagas').update({
                    'status_processo': 'expirado',
                    'observacoes': f"{rel.get('observacoes', '')}\n\n[SISTEMA - {datetime.now().strftime('%d/%m/%Y %H:%M')}] Relacionamento expirado automaticamente após 90 dias",
                    'updated_at': datetime.now().isoformat()
                }).eq('id', rel['id']).execute()
                
                if resultado.data:
                    count_expirados += 1
                    
                    # Liberar status do candidato (volta para disponível)
                    supabase.table('candidatos').update({
                        'status_candidato': 'disponivel'
                    }).eq('id', rel['candidato_id']).execute()
                    
                    # Verificar se vaga deve voltar para ativa
                    outros_relacionamentos = supabase.table('candidatos_vagas').select('id').eq('vaga_id', rel['vaga_id']).not_.in_('status_processo', ['finalizado', 'expirado', 'rejeitado', 'cancelado']).execute()
                    
                    if not outros_relacionamentos.data:
                        # Nenhum relacionamento ativo restante, vaga volta para ativa
                        supabase.table('vagas').update({
                            'status_detalhado': 'ativa'
                        }).eq('id', rel['vaga_id']).execute()
            
            if count_expirados > 0:
                st.info(f"🔄 {count_expirados} relacionamentos antigos foram expirados automaticamente")
                
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao expirar relacionamentos antigos",
            excecao=e,
            contexto={'data_limite': data_limite}
        )

def validar_limite_candidatos_vaga(vaga_id):
    """Valida se vaga já atingiu limite máximo de 5 candidatos ativos"""
    try:
        supabase = get_supabase_client()
        
        # Contar relacionamentos ativos para esta vaga
        relacionamentos_ativos = supabase.table('candidatos_vagas').select('id', count='exact').eq('vaga_id', vaga_id).not_.in_('status_processo', ['finalizado', 'expirado', 'rejeitado', 'cancelado']).execute()
        
        return relacionamentos_ativos.count < 5, relacionamentos_ativos.count
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao validar limite de candidatos por vaga",
            excecao=e,
            contexto={'vaga_id': vaga_id}
        )
    return False, 0

def verificar_relacionamento_existente(candidato_id, vaga_id):
    """Verifica se já existe relacionamento entre candidato e vaga"""
    try:
        supabase = get_supabase_client()
        
        relacionamento_existente = supabase.table('candidatos_vagas').select('id', 'status_processo').eq('candidato_id', candidato_id).eq('vaga_id', vaga_id).execute()
        
        if relacionamento_existente.data:
            # Relacionamento existe - verificar se está ativo
            status = relacionamento_existente.data[0].get('status_processo')
            if status not in ['finalizado', 'expirado']:
                return True, status
        
        return False, None
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao verificar relacionamento existente",
            excecao=e,
            contexto={'candidato_id': candidato_id, 'vaga_id': vaga_id}
        )
    return True, "erro"

def atualizar_status_automatico(candidato_id, vaga_id, acao='criar'):
    """Atualiza status automático de candidatos e vagas"""
    try:
        supabase = get_supabase_client()
        
        if acao == 'criar':
            # Ao criar relacionamento
            # Candidato fica "em_processo"
            supabase.table('candidatos').update({
                'status_candidato': 'em_processo'
            }).eq('id', candidato_id).execute()
            
            # Vaga fica "em_andamento"
            supabase.table('vagas').update({
                'status_detalhado': 'em_andamento'
            }).eq('id', vaga_id).execute()
            
        elif acao == 'finalizar':
            # Ao finalizar relacionamento
            # Candidato volta para "disponivel" (exceto se foi contratado)
            supabase.table('candidatos').update({
                'status_candidato': 'disponivel'
            }).eq('id', candidato_id).execute()
            
            # Verificar se vaga deve voltar para "ativa"
            outros_relacionamentos = supabase.table('candidatos_vagas').select('id').eq('vaga_id', vaga_id).not_.in_('status_processo', ['finalizado', 'expirado', 'rejeitado', 'cancelado']).execute()
            
            if not outros_relacionamentos.data:
                # Nenhum relacionamento ativo restante
                supabase.table('vagas').update({
                    'status_detalhado': 'ativa'
                }).eq('id', vaga_id).execute()
        
        return True
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao atualizar status automático",
            excecao=e,
            contexto={'candidato_id': candidato_id, 'vaga_id': vaga_id, 'acao': acao}
        )
    return False

def finalizar_relacionamento(relacionamento_id, resultado_final, motivo=""):
    """Finaliza um relacionamento e libera status de candidato/vaga"""
    try:
        supabase = get_supabase_client()
        
        # Buscar dados do relacionamento
        relacionamento = supabase.table('candidatos_vagas').select('*').eq('id', relacionamento_id).execute()
        
        if not relacionamento.data:
            return False, "Relacionamento não encontrado"
        
        rel = relacionamento.data[0]
        
        # Construir observação de finalização
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        observacao_finalizacao = f"\n\n[SISTEMA - {timestamp}] Relacionamento finalizado. Resultado: {resultado_final.upper()}"
        
        if motivo.strip():
            observacao_finalizacao += f". Motivo: {motivo}"
        
        observacao_atual = rel.get('observacoes', '')
        observacao_completa = f"{observacao_atual}{observacao_finalizacao}"
        
        # Status final baseado no resultado
        status_final_map = {
            'contratado': 'contratado',
            'rejeitado': 'rejeitado',
            'cancelado': 'cancelado',
            'desistiu': 'finalizado',
            'outro': 'finalizado'
        }
        
        status_final = status_final_map.get(resultado_final, 'finalizado')
        
        # Atualizar relacionamento
        resultado_update = supabase.table('candidatos_vagas').update({
            'status_processo': status_final,
            'observacoes': observacao_completa,
            'updated_at': datetime.now().isoformat()
        }).eq('id', relacionamento_id).execute()
        
        if resultado_update.data:
            
            log_auditoria(
        acao='finalizar_relacionamento',
        usuario=username if 'username' in globals() else 'sistema',
        dados={
            'relacionamento_id': relacionamento_id,
            'resultado_final': resultado_final,
            'motivo': motivo[:100] if motivo else 'N/A',
            'timestamp': datetime.now().isoformat()
        }
        )
            
            # Atualizar status automático apenas se NÃO foi contratado
            if resultado_final != 'contratado':
                atualizar_status_automatico(rel['candidato_id'], rel['vaga_id'], 'finalizar')
            else:
                # Se foi contratado, candidato fica "contratado" e vaga "preenchida"
                supabase.table('candidatos').update({
                    'status_candidato': 'contratado'
                }).eq('id', rel['candidato_id']).execute()
                
                supabase.table('vagas').update({
                    'status_detalhado': 'preenchida'
                }).eq('id', rel['vaga_id']).execute()
            
            return True, "Relacionamento finalizado com sucesso"
        
        return False, "Erro ao finalizar relacionamento"
        
    except Exception as e:
        return False, f"Erro técnico: {str(e)}"

@st.cache_data(ttl=300)
def carregar_vagas(
    limite=100,
    offset=0,
    filtros=None,
    retornar_contagem=False
):
    """
    Carrega vagas do Supabase com paginação e filtros otimizados
    
    Args:
        limite (int): Número máximo de registros a retornar (padrão: 100)
        offset (int): Número de registros a pular para paginação (padrão: 0)
        filtros (dict): Dicionário com filtros opcionais:
            - 'status': str - Filtrar por status_detalhado
            - 'urgencia': str - Filtrar por inicio_urgente
            - 'cidade': str - Filtrar por cidade
            - 'salario_min': float - Salário mínimo
            - 'salario_max': float - Salário máximo
        retornar_contagem (bool): Se True, retorna (DataFrame, total_count)
    
    Returns:
        pd.DataFrame ou tuple(pd.DataFrame, int): Dados das vagas e opcionalmente contagem total
    """
    try:
        supabase = get_supabase_client()
        
        # Iniciar query com contagem se solicitado
        if retornar_contagem:
            query = supabase.table('vagas').select('*', count='exact')
        else:
            query = supabase.table('vagas').select('*')
        
        # APLICAR FILTROS
        if filtros:
            # Filtro por status
            if filtros.get('status') and filtros['status'] != 'Todas':
                query = query.eq('status_detalhado', filtros['status'])
            
            # Filtro por urgência
            if filtros.get('urgencia') and filtros['urgencia'] != 'Todas':
                query = query.eq('inicio_urgente', filtros['urgencia'])
            
            # Filtro por cidade
            if filtros.get('cidade') and filtros['cidade'] != 'Todas':
                query = query.eq('cidade', filtros['cidade'])
            
            # Filtro por faixa salarial
            if filtros.get('salario_min') and filtros['salario_min'] > 0:
                query = query.gte('salario_oferecido', filtros['salario_min'])
            
            if filtros.get('salario_max') and filtros['salario_max'] > 0:
                query = query.lte('salario_oferecido', filtros['salario_max'])
        
        # APLICAR PAGINAÇÃO
        query = query.range(offset, offset + limite - 1)
        
        # ORDENAR por data de criação
        query = query.order('created_at', desc=True)
        
        # EXECUTAR query
        response = query.execute()
        
        # Criar DataFrame
        if response.data:
            dados_descriptografados = decrypt_lista_vagas(response.data)
            df = pd.DataFrame(dados_descriptografados)
        else:
            df = pd.DataFrame()
        
        # RETORNAR com ou sem contagem
        if retornar_contagem:
            total_count = response.count if hasattr(response, 'count') else len(df)
            return df, total_count
        else:
            return df
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar vagas: {str(e)}")
        if retornar_contagem:
            return pd.DataFrame(), 0
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
    """Adiciona observação com validação server-side"""
    try:
        # ✅ VALIDAR E SANITIZAR
        from validators import validar_observacao_vaga, validar_enum
        
        sucesso, mensagem, observacao_limpa = validar_observacao_vaga(vaga_id, observacao)
        if not sucesso:
            return False
        
        # Validar tipo
        tipos_permitidos = ['geral', 'candidato_enviado', 'status_change']
        sucesso, _ = validar_enum(tipo, tipos_permitidos, "Tipo de observação")
        if not sucesso:
            tipo = 'geral'  # Fallback seguro
        
        supabase = get_supabase_client()
        
        dados_observacao = {
            'vaga_id': vaga_id,
            'observacao': observacao_limpa,
            'tipo_observacao': tipo
        }
        
        result = supabase.table('vaga_observacoes').insert(dados_observacao).execute()
        
        return result.data is not None
        
    except Exception as e:
        return False
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
    """Atualiza status da vaga com validação server-side"""
    try:
        # ✅ VALIDAR PRIMEIRO
        from validators import validar_atualizacao_status_vaga
        
        sucesso, mensagem = validar_atualizacao_status_vaga(vaga_id, novo_status)
        if not sucesso:
            return False
        
        supabase = get_supabase_client()
        
        # Mapear status para situação
        status_to_situacao = {
            'ativa': 'ativa',
            'em_andamento': 'ativa', 
            'preenchida': 'preenchida',
            'pausada': 'pausada',
            'cancelada': 'cancelada'
        }
        
        nova_situacao = status_to_situacao.get(novo_status, 'ativa')
        
        result = supabase.table('vagas').update({
            'status_detalhado': novo_status,
            'status': nova_situacao,
            'updated_at': datetime.now().isoformat()
        }).eq('id', vaga_id).execute()
        
        if result.data is not None:
            log_auditoria(
                acao='atualizar_status_vaga',
                usuario=username if 'username' in globals() else 'sistema',
                dados={
                    'vaga_id': vaga_id,
                    'status_antigo': '?',  # Poderia buscar antes
                    'status_novo': novo_status,
                    'timestamp': datetime.now().isoformat()
                }
            )
            return True
        return False
        
    except Exception as e:
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

def formatar_status_vaga(status):
    """Retorna ícone e cor para o status da vaga"""
    status_map = {
        'ativa': {'icon': '🟢', 'color': '#28a745', 'text': 'ATIVA'},
        'em_andamento': {'icon': '🔄', 'color': '#17a2b8', 'text': 'EM ANDAMENTO'},
        'preenchida': {'icon': '✅', 'color': '#007bff', 'text': 'PREENCHIDA'},
        'pausada': {'icon': '⏸️', 'color': '#ffc107', 'text': 'PAUSADA'},
        'cancelada': {'icon': '❌', 'color': '#dc3545', 'text': 'CANCELADA'}
    }
    
    info = status_map.get(status, {'icon': '❓', 'color': '#6c757d', 'text': status.upper()})
    return f"{info['icon']} {info['text']}", info['color']

def relacionar_candidato_vaga_com_status(candidato_id, vaga_id, observacao="", status_inicial="enviado", data_entrevista=None):
    """Relaciona candidato com vaga com validação server-side"""
    try:
        # ✅ VALIDAÇÃO SERVER-SIDE COMPLETA
        sucesso, mensagem, dados_validados = validar_relacionamento_candidato_vaga(
            candidato_id=candidato_id,
            vaga_id=vaga_id,
            status_processo=status_inicial,
            observacao=observacao
        )
        
        # Se validação falhar, retornar erro
        if not sucesso:
            return False, f"❌ Validação falhou: {mensagem}"
        
        # ✅ DADOS JÁ ESTÃO LIMPOS E VALIDADOS
        supabase = get_supabase_client()
        
        # Construir observação com histórico
        from datetime import datetime
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        observacao_automatica = f"[SISTEMA - {timestamp}] Relacionamento criado com status: {status_inicial.upper()}"
        
        if dados_validados['observacoes']:
            dados_validados['observacoes'] = f"{dados_validados['observacoes']}\n\n{observacao_automatica}"
        else:
            dados_validados['observacoes'] = observacao_automatica
        
        # Adicionar data de entrevista se fornecida
        if data_entrevista:
            dados_validados['data_entrevista'] = data_entrevista.isoformat()
        
        # ✅ INSERIR DADOS VALIDADOS
        result = supabase.table('candidatos_vagas').insert(dados_validados).execute()
        
        if result.data:
            # Atualizar status automático
            atualizar_status_automatico(candidato_id, vaga_id, 'criar')
            
            # Adicionar observação na vaga
            from validators import sanitizar_texto
            obs_limpa = sanitizar_texto(f"Candidato relacionado. {observacao}")
            adicionar_observacao_vaga(vaga_id, obs_limpa, 'candidato_enviado')
            
            return True, "✅ Relacionamento criado com sucesso!"
        
        return False, "❌ Erro ao criar relacionamento"
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao criar relacionamento candidato-vaga",
            excecao=e,
            contexto={
                'candidato_id': candidato_id,
                'vaga_id': vaga_id,
                'status': status_inicial
            }
        )
    
    if result.data:
    # ✅ LOG DE AUDITORIA
        log_auditoria(
            acao='criar_relacionamento',
            usuario=username if 'username' in globals() else 'sistema',
            dados={
                'candidato_id': candidato_id,
                'vaga_id': vaga_id,
                'status_inicial': status_inicial,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        log_sucesso(
            acao="Relacionamento criado",
            usuario=username if 'username' in globals() else 'sistema',
            detalhes={'candidato': candidato_id[:8], 'vaga': vaga_id[:8]}
    )
    
    # ... resto do código
    
    return False, "❌ Erro ao criar relacionamento. Contate o administrador."
    
@st.cache_data(ttl=300)
def carregar_relacionamentos(limite=100, offset=0, filtros=None, retornar_contagem=False):
    """Carrega relacionamentos com paginação e filtros"""
    try:
        supabase = get_supabase_client()
        
        # Query com contagem opcional
        if retornar_contagem:
            query = supabase.table('candidatos_vagas_detalhado').select('*', count='exact')
        else:
            query = supabase.table('candidatos_vagas_detalhado').select('*')
        
        # APLICAR FILTROS
        if filtros:
            # Filtro por status
            if filtros.get('status') and filtros['status'] != 'Todos':
                query = query.eq('status_processo', filtros['status'])
            
            # Filtro por período (últimos 90 dias por padrão)
            if filtros.get('dias_recentes'):
                data_limite = (datetime.now() - timedelta(days=filtros['dias_recentes'])).isoformat()
                query = query.gte('data_envio', data_limite)
        else:
            # Padrão: últimos 90 dias se não houver filtro
            data_limite = (datetime.now() - timedelta(days=90)).isoformat()
            query = query.gte('data_envio', data_limite)
        
        # PAGINAÇÃO
        query = query.range(offset, offset + limite - 1)
        
        # ORDENAR por data mais recente
        query = query.order('data_envio', desc=True)
        
        # EXECUTAR
        response = query.execute()
        
        if retornar_contagem:
            total = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
            return pd.DataFrame(response.data) if response.data else pd.DataFrame(), total
        
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar relacionamentos",
            excecao=e,
            contexto={'limite': limite, 'offset': offset}
        )
    if retornar_contagem:
        return pd.DataFrame(), 0
    return pd.DataFrame()

def atualizar_relacionamento(relacionamento_id, novo_candidato_id=None, nova_observacao=None, novo_status=None, data_entrevista=None, reiniciar_prazo=False):
    """Atualiza relacionamento com histórico automático"""
    try:
        supabase = get_supabase_client()
        
        dados_atualizacao = {}
        historico_mudancas = []
        
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        if novo_candidato_id:
            dados_atualizacao['candidato_id'] = novo_candidato_id
            historico_mudancas.append(f"[SISTEMA - {timestamp}] Candidato alterado")
            
            if reiniciar_prazo:
                dados_atualizacao['data_envio'] = datetime.now().isoformat()
                historico_mudancas.append(f"[SISTEMA - {timestamp}] Prazo de 90 dias reiniciado devido à troca de candidato")
        
        if novo_status:
            dados_atualizacao['status_processo'] = novo_status
            historico_mudancas.append(f"[SISTEMA - {timestamp}] Status alterado para: {novo_status.upper().replace('_', ' ')}")
            
        if data_entrevista:
            dados_atualizacao['data_entrevista'] = data_entrevista.isoformat()
            data_formatada = data_entrevista.strftime('%d/%m/%Y às %H:%M')
            historico_mudancas.append(f"[SISTEMA - {timestamp}] Entrevista agendada para: {data_formatada}")
        
        # Construir observação final com histórico
        observacao_final = nova_observacao or ""
        if historico_mudancas:
            historico_texto = "\n".join(historico_mudancas)
            observacao_final = f"{observacao_final}\n\n{historico_texto}" if observacao_final else historico_texto
        
        if observacao_final:
            dados_atualizacao['observacoes'] = observacao_final
        
        dados_atualizacao['updated_at'] = datetime.now().isoformat()
        
        result = supabase.table('candidatos_vagas').update(dados_atualizacao).eq('id', relacionamento_id).execute()
        
        return result.data is not None
        
    except Exception as e:
        st.error(f"❌ Erro ao atualizar relacionamento: {str(e)}")
        return False

def excluir_relacionamento(relacionamento_id):
    """Exclui um relacionamento"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('candidatos_vagas').delete().eq('id', relacionamento_id).execute()
        
        return result.data is not None
        
    except Exception as e:
        st.error(f"❌ Erro ao excluir relacionamento: {str(e)}")
        return False
    
# ============================================
# FUNÇÕES DE BACKUP
# ============================================

def gerenciar_backups():
    """Nova aba para gerenciar backups do sistema"""
    
    st.header("💾 Sistema de Backup - Google Drive")
    
    # Informações do sistema
    with st.expander("ℹ️ Sobre o Sistema de Backup", expanded=False):
        st.markdown("""
        ### 🎯 Funcionalidades
        - **Backup Automático**: Todos os dados do Supabase salvos no Google Drive
        - **Compressão ZIP**: Backups comprimidos para economizar espaço
        - **Retenção Inteligente**: Mantém apenas os backups mais recentes
        - **Restauração Fácil**: Restaure dados com um clique
        
        ### 📊 Dados Incluídos no Backup
        - ✅ Candidatos
        - ✅ Candidatos Qualificados
        - ✅ Vagas
        - ✅ Observações de Vagas
        - ✅ Relacionamentos Candidato-Vaga
        
        ### 🔒 Segurança
        - Conexão criptografada com Google Drive
        - Service Account com permissões limitadas
        - Dados armazenados em pasta privada
        """)
    
    st.markdown("---")
    
    # ===== SEÇÃO 1: CRIAR NOVO BACKUP =====
    st.subheader("🆕 Criar Novo Backup")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info("💡 O backup incluirá todas as tabelas do sistema e será salvo automaticamente no Google Drive")
    
    with col2:
        compress = st.checkbox("🗜️ Comprimir (ZIP)", value=True, key="compress_backup")
    
    with col3:
        if st.button("▶️ Criar Backup", type="primary", use_container_width=True):
            with st.spinner("⏳ Criando backup..."):
                try:
                    sucesso, file_id = criar_backup_automatico()
                    
                    if sucesso:
                        st.success(f"✅ Backup criado com sucesso!")
                        st.info(f"🆔 File ID: `{file_id}`")
                        st.balloons()
                        
                        # Atualizar lista
                        st.rerun()
                    else:
                        st.error("❌ Falha ao criar backup. Verifique os logs.")
                        
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    st.markdown("---")
    
    # ===== SEÇÃO 2: BACKUPS DISPONÍVEIS =====
    st.subheader("📋 Backups Disponíveis")
    
    with st.spinner("🔄 Carregando lista de backups..."):
        try:
            backups = listar_backups_disponiveis()
            
            if not backups:
                st.warning("⚠️ Nenhum backup encontrado. Crie o primeiro backup acima!")
            else:
                st.success(f"✅ {len(backups)} backup(s) disponível(is)")
                
                # Exibir em cards
                for idx, backup in enumerate(backups):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                        
                        with col1:
                            st.write(f"**📦 {backup['name']}**")
                        
                        with col2:
                            # Formatar data
                            from datetime import datetime
                            try:
                                data_obj = datetime.fromisoformat(backup['created'].replace('Z', '+00:00'))
                                data_formatada = data_obj.strftime('%d/%m/%Y %H:%M')
                            except:
                                data_formatada = backup['created']
                            
                            st.write(f"🕐 {data_formatada}")
                        
                        with col3:
                            st.write(f"💾 {backup['size_mb']} MB")
                        
                        with col4:
                            # Botão de download
                            if st.button("⬇️", key=f"download_{idx}", help="Baixar backup"):
                                st.info("💡 Função de download será implementada")
                        
                        st.markdown("---")
                
        except Exception as e:
            st.error(f"❌ Erro ao listar backups: {str(e)}")
    
    st.markdown("---")
    
    # ===== SEÇÃO 3: RESTAURAÇÃO =====
    st.subheader("♻️ Restaurar Backup")
    
    with st.expander("⚠️ ATENÇÃO - Restauração de Dados", expanded=False):
        st.warning("""
        ### ⚠️ Importante
        A restauração irá **SOBRESCREVER** os dados atuais do banco de dados.
        
        **Recomendações:**
        1. Crie um backup dos dados atuais antes de restaurar
        2. Verifique qual backup deseja restaurar
        3. Entre em contato com o suporte se tiver dúvidas
        
        **Esta ação não pode ser desfeita!**
        """)
        
        # Seleção de backup para restaurar
        if backups:
            backup_options = {
                backup['name']: backup['id'] 
                for backup in backups
            }
            
            backup_selecionado = st.selectbox(
                "Selecione o backup para restaurar:",
                options=list(backup_options.keys()),
                key="select_backup_restore"
            )
            
            # Opções de restauração
            st.write("**Tabelas a restaurar:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                restore_candidatos = st.checkbox("✅ Candidatos", value=True)
                restore_qualificados = st.checkbox("✅ Candidatos Qualificados", value=True)
                restore_vagas = st.checkbox("✅ Vagas", value=True)
            
            with col2:
                restore_observacoes = st.checkbox("✅ Observações de Vagas", value=True)
                restore_relacionamentos = st.checkbox("✅ Relacionamentos", value=True)
            
            st.markdown("---")
            
            # Confirmação dupla
            confirmar1 = st.checkbox("⚠️ Entendo que esta ação sobrescreverá os dados atuais", key="confirm1")
            confirmar2 = st.checkbox("⚠️ Tenho certeza que quero restaurar este backup", key="confirm2")
            
            if confirmar1 and confirmar2:
                if st.button("♻️ RESTAURAR BACKUP", type="secondary", use_container_width=True):
                    
                    # Coletar tabelas selecionadas
                    tabelas = []
                    if restore_candidatos:
                        tabelas.append('candidatos')
                    if restore_qualificados:
                        tabelas.append('candidatos_qualificados')
                    if restore_vagas:
                        tabelas.append('vagas')
                    if restore_observacoes:
                        tabelas.append('vaga_observacoes')
                    if restore_relacionamentos:
                        tabelas.append('candidatos_vagas')
                    
                    if not tabelas:
                        st.error("❌ Selecione pelo menos uma tabela para restaurar!")
                    else:
                        with st.spinner("⏳ Restaurando backup... Isso pode levar alguns minutos..."):
                            try:
                                from dotenv import load_dotenv
                                load_dotenv()
                                
                                service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
                                folder_id = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
                                
                                backup_manager = GoogleDriveBackup(
                                    service_account_file=service_account_file,
                                    folder_id=folder_id
                                )
                                
                                file_id = backup_options[backup_selecionado]
                                
                                sucesso = backup_manager.restore_backup(
                                    file_id=file_id,
                                    tables=tabelas
                                )
                                
                                if sucesso:
                                    st.success("✅ Backup restaurado com sucesso!")
                                    st.info("🔄 Recarregue a página para ver os dados restaurados")
                                    st.balloons()
                                else:
                                    st.error("❌ Falha na restauração. Verifique os logs.")
                                    
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
            else:
                st.info("👆 Marque as duas confirmações acima para habilitar a restauração")
    
    st.markdown("---")
    
    # ===== SEÇÃO 4: CONFIGURAÇÕES =====
    st.subheader("⚙️ Configurações de Backup")
    
    with st.expander("🔧 Configurações Avançadas", expanded=False):
        
        from dotenv import load_dotenv
        load_dotenv()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📁 Pasta do Google Drive:**")
            folder_id = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID', 'não configurado')
            st.code(folder_id)
            
            st.write("**📊 Retenção de Backups:**")
            max_retention = os.getenv('BACKUP_MAX_RETENTION', '30')
            st.info(f"Mantém os {max_retention} backups mais recentes")
        
        with col2:
            st.write("**🔐 Service Account:**")
            service_account = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'não configurado')
            st.code(service_account)
            
            st.write("**⏰ Backup Automático:**")
            auto_backup = os.getenv('BACKUP_AUTO_START', 'false')
            if auto_backup.lower() == 'true':
                st.success("✅ Ativado")
            else:
                st.warning("⚠️ Desativado")
        
        st.markdown("---")
        
        st.write("**💡 Dicas:**")
        st.markdown("""
        - Configure as variáveis no arquivo `.env`
        - Teste a conexão criando um backup manual
        - Backups automáticos rodam em segundo plano
        - Use compressão ZIP para economizar espaço
        """)


#===================================
# PÁGINAS/ABAS DO SISTEMA
# =====================================

def carregar_dados_candidatos_por_tipo(tipo_visualizacao):
    """
    Carrega candidatos baseado no tipo de visualização selecionado
    
    Args:
        tipo_visualizacao (str): Tipo de candidatos a carregar
        
    Returns:
        tuple: (DataFrame, título_header)
    """
    try:
        if tipo_visualizacao == "Candidatos qualificados":
            df = carregar_candidatos_qualificados()
            titulo = "👑 Candidatos Qualificados"
            
        elif tipo_visualizacao == "Pendentes de qualificação":
            df = carregar_candidatos_pendentes()
            titulo = "⏳ Pendentes de Qualificação"
            
        else:
            df = carregar_candidatos()
            titulo = "📋 Todos os Candidatos"
        
        return df, titulo
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar dados de candidatos",
            excecao=e,
            contexto={'tipo_visualizacao': tipo_visualizacao}
        )
        return pd.DataFrame(), "📋 Candidatos"
    
def criar_sidebar_filtros_candidatos(df):
    """
    Cria sidebar com todos os filtros de candidatos
    
    Args:
        df (DataFrame): DataFrame com candidatos
        
    Returns:
        dict: Dicionário com valores dos filtros selecionados
    """
    filtros = {}
    
    with st.sidebar:
        st.header("🔍 Filtros de Candidatos")
        
        # Filtro de qualificação
        filtros['tipo_visualizacao'] = st.selectbox(
            "Visualizar:",
            [
                "Todos os candidatos",
                "Candidatos qualificados", 
                "Pendentes de qualificação"
            ],
            key="tipo_visualizacao_candidatos"
        )
        
        st.markdown("---")
        
        # Filtro por nome
        if 'nome_completo' in df.columns:
            filtros['nome'] = st.text_input(
                "🔎 Buscar por nome", 
                "",
                placeholder="Digite o nome...",
                key="filtro_nome_candidato"
            )
        else:
            filtros['nome'] = ""
        
        # Filtro por função
        if 'formulario_id' in df.columns:
            funcoes_unicas = ['Todas'] + sorted(
                df['formulario_id'].dropna().unique().tolist()
            )
            filtros['funcao'] = st.selectbox(
                "💼 Filtrar por função", 
                funcoes_unicas,
                key="filtro_funcao_candidato"
            )
        else:
            filtros['funcao'] = "Todas"
        
        # Filtro por status de ficha
        filtros['status_ficha'] = st.radio(
            "📋 Status da ficha",
            ["Todos", "Apenas pendentes", "Apenas com ficha gerada"],
            key="filtro_status_ficha"
        )
        
        st.markdown("---")
        
        # Filtros avançados (se houver dados)
        if not df.empty:
            with st.expander("🔧 Filtros Avançados", expanded=False):
                
                # Filtro por cidade
                if 'cidade' in df.columns:
                    cidades = ['Todas'] + sorted(
                        df['cidade'].dropna().unique().tolist()
                    )
                    filtros['cidade'] = st.selectbox(
                        "🏙️ Cidade:",
                        cidades,
                        key="filtro_cidade_candidato"
                    )
                else:
                    filtros['cidade'] = "Todas"
                
                # Filtro por status do candidato
                if 'status_candidato' in df.columns:
                    status_opcoes = ['Todos'] + sorted(
                        df['status_candidato'].dropna().unique().tolist()
                    )
                    filtros['status_candidato'] = st.selectbox(
                        "📊 Status:",
                        status_opcoes,
                        key="filtro_status_candidato"
                    )
                else:
                    filtros['status_candidato'] = "Todos"
    
    return filtros

def aplicar_filtros_candidatos(df, filtros):
    """
    Aplica todos os filtros selecionados no DataFrame
    
    Args:
        df (DataFrame): DataFrame original
        filtros (dict): Dicionário com filtros
        
    Returns:
        DataFrame: DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    # Filtro por nome
    if filtros.get('nome') and filtros['nome'].strip():
        from validators import sanitizar_filtro_busca
        busca_limpa = sanitizar_filtro_busca(filtros['nome'])
        
        if busca_limpa and 'nome_completo' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['nome_completo'].str.contains(
                    busca_limpa, case=False, na=False
                )
            ]
    
    # Filtro por função
    if filtros.get('funcao') and filtros['funcao'] != "Todas":
        if 'formulario_id' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['formulario_id'] == filtros['funcao']
            ]
    
    # Filtro por status de ficha
    if filtros.get('status_ficha'):
        if filtros['status_ficha'] == "Apenas pendentes":
            df_filtrado = df_filtrado[
                df_filtrado.get('ficha_emitida', pd.Series([False] * len(df_filtrado))) != True
            ]
        elif filtros['status_ficha'] == "Apenas com ficha gerada":
            df_filtrado = df_filtrado[
                df_filtrado.get('ficha_emitida', pd.Series([False] * len(df_filtrado))) == True
            ]
    
    # Filtro por cidade (avançado)
    if filtros.get('cidade') and filtros['cidade'] != "Todas":
        if 'cidade' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['cidade'] == filtros['cidade']
            ]
    
    # Filtro por status do candidato (avançado)
    if filtros.get('status_candidato') and filtros['status_candidato'] != "Todos":
        if 'status_candidato' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['status_candidato'] == filtros['status_candidato']
            ]
    
    return df_filtrado

def exibir_metricas_candidatos(df):
    """
    Exibe métricas dos candidatos em cards
    
    Args:
        df (DataFrame): DataFrame com candidatos
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Candidatos", len(df))
    
    with col2:
        fichas_geradas = len(
            df[df.get('ficha_emitida', pd.Series([False] * len(df))) == True]
        )
        st.metric("📄 Fichas Geradas", fichas_geradas)
    
    with col3:
        pendentes = len(df) - fichas_geradas
        st.metric("⏳ Pendentes", pendentes)
    
    with col4:
        if 'created_at' in df.columns:
            hoje = datetime.now().date()
            novos_hoje = len(
                df[pd.to_datetime(df['created_at']).dt.date == hoje]
            )
            st.metric("🆕 Hoje", novos_hoje)
        else:
            st.metric("🆕 Hoje", 0)
            
def exibir_card_candidato(candidato, idx):
    """
    Exibe card individual de um candidato com todas as ações
    
    Args:
        candidato (dict): Dados do candidato
        idx (int): Índice para keys únicas
    """
    candidato_id = candidato.get('id')
    unique_key = f"{candidato_id}_{idx}"
    
    # Título do expander
    titulo_expander = (
        f"{formatar_funcao(candidato.get('formulario_id', ''))} | "
        f"{candidato.get('nome_completo', 'Nome não informado')} | "
        f"📞 {candidato.get('telefone', 'Tel. não informado')}"
    )
    
    with st.expander(titulo_expander, expanded=False):
        
        col1, col2 = st.columns([2, 1])
        
        # ===== COLUNA 1: INFORMAÇÕES =====
        with col1:
            # Informações básicas
            st.write(f"**📧 Email:** {candidato.get('email', 'Não informado')}")
            
            whatsapp_link = formatar_whatsapp_link(candidato.get('whatsapp'))
            st.markdown(f"**📲 Whatsapp:** {whatsapp_link}", unsafe_allow_html=True)
            
            st.write(f"**📍 Endereço:** {candidato.get('endereco', 'Não informado')}")
            st.write(f"**👨‍👩‍👧‍👦 Filhos:** {'Sim' if candidato.get('tem_filhos') else 'Não'}")
            st.write(f"**🚗 CNH:** {'Sim' if candidato.get('possui_cnh') else 'Não'}")
            
            # Data de cadastro
            if candidato.get('created_at'):
                data_cadastro = pd.to_datetime(candidato['created_at']).strftime('%d/%m/%Y às %H:%M')
                st.write(f"**📅 Cadastrado em:** {data_cadastro}")
            
            st.markdown("---")
            
            # Status de qualificação
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
        
        # ===== COLUNA 2: AÇÕES =====
        with col2:
            st.subheader("🎛️ Ações")
            
            # Botão gerar PDF
            exibir_botao_gerar_pdf(candidato, idx)
            
            st.markdown("---")
            
            # Sistema de qualificação (se não qualificado)
            if 'data_qualificacao' not in candidato:
                exibir_formulario_qualificacao(candidato, idx)

def exibir_botao_gerar_pdf(candidato, idx):
    """
    Exibe botão para gerar PDF do candidato
    
    Args:
        candidato (dict): Dados do candidato
        idx (int): Índice para keys únicas
    """
    candidato_id = candidato.get('id')
    btn_gen_key = f"pdf_gen_{candidato_id}_{idx}"
    
    if st.button("📄 Gerar e Baixar Ficha PDF", key=btn_gen_key, type="primary"):
        try:
            with st.spinner("📄 Gerando PDF..."):
                # Gerar PDF
                resultado = gerar_ficha_candidato_completa(candidato)
                
                if isinstance(resultado, tuple):
                    pdf_bytes, nome_arquivo = resultado
                else:
                    pdf_bytes = resultado
                    nome_limpo = candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
                    import re
                    nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
                    nome_arquivo = f"{nome_limpo}-{datetime.now().strftime('%d%m%Y')}.pdf"
                
                # Atualizar status no banco ANTES do download
                atualizar_status_ficha(candidato_id)
                
                # Download direto
                st.download_button(
                    label="💾 CLIQUE PARA BAIXAR O PDF",
                    data=pdf_bytes,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    key=f"download_{candidato_id}_{idx}",
                    type="primary",
                    use_container_width=True
                )
                
                st.success("✅ PDF gerado com sucesso! Clique no botão acima para baixar.")
                st.info("💡 Dica: O download iniciará automaticamente ao clicar.")
                
        except Exception as e:
            log_erro(
                mensagem_usuario="Erro ao gerar PDF do candidato",
                excecao=e,
                contexto={
                    'candidato_id': candidato_id,
                    'nome': candidato.get('nome_completo', 'N/A')
                }
            )


def exibir_formulario_qualificacao(candidato, idx):
    """
    Exibe formulário de qualificação de candidato
    
    Args:
        candidato (dict): Dados do candidato
        idx (int): Índice para keys únicas
    """
    candidato_id = candidato.get('id')
    
    st.markdown("### 🎓 Qualificar Candidato")
    
    with st.form(key=f"qualificacao_form_{candidato_id}_{idx}", clear_on_submit=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            nota = st.slider(
                "Nota do treinamento (0-10)", 
                0, 10, 7,
                key=f"nota_{candidato_id}_{idx}"
            )
        
        with col2:
            instrutor = st.text_input(
                "Nome do instrutor",
                key=f"instrutor_{candidato_id}_{idx}"
            )
        
        observacoes = st.text_area(
            "Observações sobre o treinamento", 
            height=100,
            key=f"obs_qual_{candidato_id}_{idx}"
        )
        
        submitted = st.form_submit_button(
            "✅ QUALIFICAR CANDIDATO", 
            type="primary"
        )
        
        if submitted:
            if not instrutor.strip():
                st.error("❌ O nome do instrutor é obrigatório!")
            else:
                with st.spinner("Processando qualificação..."):
                    sucesso, certificado = qualificar_candidato_simples(
                        candidato_id, nota, observacoes, instrutor
                    )
                    
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

def gerenciar_candidatos():
    """
    Função orquestradora de gestão de candidatos
    MODULARIZADA - Apenas coordena os módulos
    """
    
    # 1. CRIAR SIDEBAR COM FILTROS (ANTES DE TUDO!)
    # Carregar dados iniciais para popular filtros
    df_inicial = carregar_candidatos()
    
    if df_inicial.empty:
        st.warning("⚠️ Nenhum candidato encontrado no banco de dados.")
        st.info("📄 Certifique-se que existem candidatos cadastrados no Supabase.")
        return
    
    filtros = criar_sidebar_filtros_candidatos(df_inicial)
    
    # 2. CARREGAR DADOS BASEADO NO TIPO SELECIONADO
    with st.spinner("Carregando candidatos..."):
        df, titulo = carregar_dados_candidatos_por_tipo(filtros['tipo_visualizacao'])
    
    # Exibir título
    st.header(titulo)
    
    if df.empty:
        st.warning("⚠️ Nenhum candidato encontrado para este tipo de visualização.")
        return
    
    # 3. EXIBIR MÉTRICAS
    exibir_metricas_candidatos(df)
    
    st.markdown("---")
    
    # 4. APLICAR FILTROS
    df_filtrado = aplicar_filtros_candidatos(df, filtros)
    
    # 5. PAGINAÇÃO
    df_paginado, total = carregar_candidatos(limite=100, offset=0, retornar_contagem=True)
    
    pagina_atual, offset = exibir_paginacao(
        total_registros=total,
        registros_por_pagina=100,
        key_prefix="candidatos"
    )
    
    if offset > 0:
        df_filtrado = carregar_candidatos(limite=100, offset=offset)
        df_filtrado = aplicar_filtros_candidatos(df_filtrado, filtros)
    
    # 6. EXIBIR RESULTADOS
    st.subheader(f"📋 Candidatos ({len(df_filtrado)} encontrados)")
    
    if df_filtrado.empty:
        st.info("🔍 Nenhum candidato encontrado com os filtros aplicados.")
        return
    
    # 7. LISTA DE CARDS
    for idx, candidato in enumerate(df_filtrado.to_dict('records')):
        exibir_card_candidato(candidato, idx)

@st.cache_data(ttl=300)
def carregar_dados_relacionamentos():
    """
    Carrega todos os dados necessários para gestão de relacionamentos
    
    Returns:
        tuple: (df_candidatos, df_vagas, df_relacionamentos, total_count)
    """
    try:
        df_candidatos = carregar_candidatos()
        df_vagas = carregar_vagas()
        df_relacionamentos, total = carregar_relacionamentos(
            limite=100,
            offset=0,
            retornar_contagem=True
        )
        
        return df_candidatos, df_vagas, df_relacionamentos, total
        
    except Exception as e:
        log_erro(
            mensagem_usuario="Erro ao carregar dados de relacionamentos",
            excecao=e,
            contexto={}
        )
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0
    
def criar_formulario_novo_relacionamento(df_candidatos, df_vagas):
    """
    Exibe formulário para criar novo relacionamento candidato-vaga
    ✅ CORRIGIDO: Keys únicas e submit button adicionado
    
    Args:
        df_candidatos: DataFrame com candidatos
        df_vagas: DataFrame com vagas
        
    Returns:
        bool: True se relacionamento foi criado
    """
    st.subheader("➕ Criar Novo Relacionamento")
    
    if df_candidatos.empty or df_vagas.empty:
        st.warning("⚠️ É necessário ter candidatos e vagas cadastrados.")
        return False
    
    with st.form("form_novo_relacionamento", clear_on_submit=True):
        
        # ===== SEÇÃO 1: CANDIDATO =====
        st.markdown("#### 👤 Selecionar Candidato")
        
        col_busca_cand, col_filtro_cand = st.columns([2, 1])
        
        with col_busca_cand:
            busca_candidato = st.text_input(
                "🔎 Buscar por nome:",
                placeholder="Digite nome do candidato...",
                key="busca_candidato_rel"  # ✅ KEY ÚNICA
            )
        
        with col_filtro_cand:
            funcoes_candidatos = ["Todas"] + sorted(
                df_candidatos['formulario_id'].dropna().unique().tolist()
            )
            filtro_funcao = st.selectbox(
                "Filtrar por função:",
                funcoes_candidatos,
                key="filtro_funcao_candidato_rel"  # ✅ KEY ÚNICA
            )
        
        # Filtrar candidatos
        df_cand_filtrado = df_candidatos.copy()
        
        if busca_candidato.strip():
            from validators import sanitizar_nome
            busca_limpa = sanitizar_nome(busca_candidato)
            if busca_limpa:
                df_cand_filtrado = df_cand_filtrado[
                    df_cand_filtrado['nome_completo'].str.contains(
                        busca_limpa, case=False, na=False
                    )
                ]
        
        if filtro_funcao != "Todas":
            df_cand_filtrado = df_cand_filtrado[
                df_cand_filtrado['formulario_id'] == filtro_funcao
            ]
        
        # Selectbox de candidatos
        if df_cand_filtrado.empty:
            st.warning("⚠️ Nenhum candidato encontrado. Ajuste os filtros.")
            candidato_id = None
        else:
            st.info(f"📊 {len(df_cand_filtrado)} candidatos encontrados")
            candidato_id = st.selectbox(
                "Escolher candidato:",
                options=df_cand_filtrado['id'].tolist(),
                format_func=lambda x: (
                    f"{df_cand_filtrado[df_cand_filtrado['id'] == x]['nome_completo'].iloc[0]} - "
                    f"{formatar_funcao(df_cand_filtrado[df_cand_filtrado['id'] == x]['formulario_id'].iloc[0])}"
                ),
                key="select_candidato_rel"  # ✅ KEY ÚNICA
            )
        
        st.markdown("---")
        
        # ===== SEÇÃO 2: VAGA =====
        st.markdown("#### 💼 Selecionar Vaga")
        
        col_busca_vaga, col_filtro_vaga = st.columns([2, 1])
        
        with col_busca_vaga:
            busca_vaga = st.text_input(
                "🔎 Buscar por proprietário:",
                placeholder="Digite nome do proprietário...",
                key="busca_vaga_rel"  # ✅ KEY ÚNICA
            )
        
        with col_filtro_vaga:
            tipos_vagas = ["Todas"] + sorted(
                df_vagas['formulario_id'].dropna().unique().tolist()
            )
            filtro_tipo_vaga = st.selectbox(
                "Filtrar por tipo:",
                tipos_vagas,
                key="filtro_tipo_vaga_rel"  # ✅ KEY ÚNICA
            )
        
        # Filtrar vagas
        df_vagas_filtrado = df_vagas.copy()
        
        if busca_vaga.strip():
            from validators import sanitizar_nome
            busca_limpa_vaga = sanitizar_nome(busca_vaga)
            if busca_limpa_vaga:
                # Criar coluna temporária
                df_vagas_filtrado['nome_completo_prop'] = (
                    df_vagas_filtrado['nome'].fillna('') + ' ' + 
                    df_vagas_filtrado['sobrenome'].fillna('')
                ).str.strip()
                
                df_vagas_filtrado = df_vagas_filtrado[
                    df_vagas_filtrado['nome_completo_prop'].str.contains(
                        busca_limpa_vaga, case=False, na=False
                    )
                ]
        
        if filtro_tipo_vaga != "Todas":
            df_vagas_filtrado = df_vagas_filtrado[
                df_vagas_filtrado['formulario_id'] == filtro_tipo_vaga
            ]
        
        # Apenas vagas ativas
        df_vagas_filtrado = df_vagas_filtrado[
            df_vagas_filtrado.get('status_detalhado', 'ativa').isin(['ativa', 'em_andamento'])
        ]
        
        # Selectbox de vagas
        if df_vagas_filtrado.empty:
            st.warning("⚠️ Nenhuma vaga ativa encontrada. Ajuste os filtros.")
            vaga_id = None
        else:
            st.info(f"📊 {len(df_vagas_filtrado)} vagas encontradas")
            vaga_id = st.selectbox(
                "Escolher vaga:",
                options=df_vagas_filtrado['id'].tolist(),
                format_func=lambda x: (
                    f"{df_vagas_filtrado[df_vagas_filtrado['id'] == x]['nome'].iloc[0]} "
                    f"{df_vagas_filtrado[df_vagas_filtrado['id'] == x]['sobrenome'].iloc[0]} - "
                    f"{formatar_funcao_vaga(df_vagas_filtrado[df_vagas_filtrado['id'] == x]['formulario_id'].iloc[0])} - "
                    f"R$ {df_vagas_filtrado[df_vagas_filtrado['id'] == x]['salario_oferecido'].iloc[0]}"
                ),
                key="select_vaga_rel"  # ✅ KEY ÚNICA
            )
        
        st.markdown("---")
        
        # ===== SEÇÃO 3: DETALHES =====
        st.markdown("#### 📋 Detalhes do Relacionamento")
        
        col_status, col_obs = st.columns([1, 2])
        
        with col_status:
            status_inicial = st.selectbox(
                "Status inicial:",
                ["enviado", "em_analise", "entrevista_agendada", "aprovado"],
                key="status_inicial_rel"  # ✅ KEY ÚNICA
            )
        
        with col_obs:
            observacao = st.text_area(
                "Observação inicial:",
                placeholder="Ex: Candidato enviado via WhatsApp às 14h30",
                height=100,
                key="observacao_inicial_rel"  # ✅ KEY ÚNICA
            )
        
        # Campo especial para entrevista
        data_entrevista = None
        if status_inicial == "entrevista_agendada":
            st.markdown("**📅 Dados da Entrevista:**")
            col_data, col_hora = st.columns(2)
            
            with col_data:
                data_ent = st.date_input(
                    "Data:",
                    value=datetime.now().date(),
                    key="data_entrevista_rel"  # ✅ KEY ÚNICA
                )
            
            with col_hora:
                hora_ent = st.time_input(
                    "Hora:",
                    value=datetime.now().replace(second=0, microsecond=0).time(),
                    key="hora_entrevista_rel"  # ✅ KEY ÚNICA
                )
            
            data_entrevista = datetime.combine(data_ent, hora_ent)
            st.success(f"✅ Entrevista: {data_entrevista.strftime('%d/%m/%Y às %H:%M')}")
        
        # ===== ✅ BOTÃO DE SUBMIT (CORRIGIDO) =====
        submitted = st.form_submit_button(
            "🔗 Criar Relacionamento",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not candidato_id:
                st.error("❌ Selecione um candidato válido!")
                return False
            
            if not vaga_id:
                st.error("❌ Selecione uma vaga válida!")
                return False
            
            if status_inicial == "entrevista_agendada" and not data_entrevista:
                st.error("❌ Defina data e hora da entrevista!")
                return False
            
            # Criar relacionamento
            with st.spinner("🔄 Criando relacionamento..."):
                sucesso, mensagem = relacionar_candidato_vaga_com_status(
                    candidato_id=candidato_id,
                    vaga_id=vaga_id,
                    observacao=observacao,
                    status_inicial=status_inicial,
                    data_entrevista=data_entrevista
                )
                
                if sucesso:
                    st.success(mensagem)
                    st.balloons()
                    return True
                else:
                    st.error(mensagem)
                    return False
    
    return False

def exibir_card_relacionamento(rel, idx):
    """
    Exibe card individual de um relacionamento
    
    Args:
        rel: Dict com dados do relacionamento
        idx: Índice para keys únicas
    """
    # Calcular datas
    data_envio = pd.to_datetime(rel.get('data_envio'))
    hoje = pd.Timestamp.now(tz='UTC')
    
    # Normalizar timezone
    if data_envio.tz is None:
        data_envio = data_envio.tz_localize(None)
        hoje = hoje.tz_localize(None)
    else:
        hoje = hoje.tz_convert(data_envio.tz)
    
    dias_passados = (hoje - data_envio).days
    dias_restantes = 90 - dias_passados
    status_atual = rel.get('status_processo', 'enviado')
    
    # Container do card
    with st.container():
        # ===== HEADER =====
        col_status, col_prazo = st.columns([2, 1])
        
        with col_status:
            status_icons = {
                'enviado': '📤',
                'em_analise': '🔍',
                'entrevista_agendada': '📅',
                'aprovado': '✅',
                'contratado': '🎉',
                'rejeitado': '❌',
                'cancelado': 'ℹ️'
            }
            icon = status_icons.get(status_atual, '📋')
            st.markdown(f"### {icon} {status_atual.upper().replace('_', ' ')}")
        
        with col_prazo:
            if dias_restantes <= 0:
                st.error(f"🚨 Vencido há {abs(dias_restantes)} dias")
            elif dias_restantes <= 15:
                st.error(f"⚠️ {dias_restantes} dias restantes")
            elif dias_restantes <= 30:
                st.warning(f"⏳ {dias_restantes} dias restantes")
            else:
                st.success(f"✅ {dias_restantes} dias restantes")
        
        # ===== INFORMAÇÕES =====
        col_pessoas, col_datas = st.columns(2)
        
        with col_pessoas:
            st.markdown("**👥 Pessoas**")
            st.write(f"👤 {rel.get('nome_completo', 'N/A')}")
            st.write(f"🏷️ {formatar_funcao(rel.get('tipo_candidato', ''))}")
            st.write(f"🏠 {rel.get('nome_proprietario', 'N/A')}")
            st.write(f"🎯 {formatar_funcao_vaga(rel.get('tipo_vaga', ''))}")
        
        with col_datas:
            st.markdown("**📅 Cronologia**")
            st.write(f"📤 {data_envio.strftime('%d/%m/%Y %H:%M')}")
            st.write(f"⏱️ {dias_passados} dias ativo")
            
            # Barra de progresso
            progresso = max(0, min(100, dias_restantes / 90 * 100))
            st.progress(progresso / 100)
            st.caption(f"{progresso:.0f}% do prazo")
        
        # ===== OBSERVAÇÕES =====
        if rel.get('observacoes'):
            with st.expander("💬 Histórico", expanded=False):
                for linha in rel.get('observacoes').split('\n'):
                    if linha.strip():
                        st.caption(linha.strip())
        
        # ===== PAINEL DE CONTROLE =====
        exibir_painel_controle_relacionamento(rel, idx)
        
        st.markdown("---")
        
def exibir_painel_controle_relacionamento(rel, idx):
    """
    Exibe painel de ações para um relacionamento
    
    Args:
        rel: Dict com dados do relacionamento
        idx: Índice para keys únicas
    """
    with st.expander("⚙️ Ações", expanded=False):
        
        tab1, tab2, tab3 = st.tabs(["📝 Observação", "📋 Status", "🏁 Finalizar"])
        
        # ===== TAB 1: OBSERVAÇÃO =====
        with tab1:
            nova_obs = st.text_area(
                "Nova observação:",
                height=80,
                key=f"obs_{rel.get('id')}_{idx}"
            )
            
            if st.button("💾 Adicionar", key=f"add_obs_{idx}"):
                if nova_obs.strip():
                    obs_atual = rel.get('observacoes', '')
                    obs_completa = f"{obs_atual}\n\n{nova_obs.strip()}" if obs_atual else nova_obs.strip()
                    
                    if atualizar_relacionamento(rel.get('id'), nova_observacao=obs_completa):
                        st.success("✅ Observação adicionada!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.error("❌ Digite uma observação")
        
        # ===== TAB 2: STATUS =====
        with tab2:
            novo_status = st.selectbox(
                "Alterar status para:",
                ["enviado", "em_analise", "entrevista_agendada", "aprovado", "rejeitado", "contratado"],
                key=f"status_{idx}"
            )
            
            if st.button("🔄 Atualizar", key=f"update_status_{idx}"):
                if atualizar_relacionamento(rel.get('id'), novo_status=novo_status):
                    st.success("✅ Status atualizado!")
                    st.cache_data.clear()
                    st.rerun()
        
        # ===== TAB 3: FINALIZAR =====
        with tab3:
            resultado = st.selectbox(
                "Resultado final:",
                ["contratado", "rejeitado", "cancelado"],
                key=f"resultado_{idx}"
            )
            
            motivo = st.text_area(
                "Motivo:",
                height=60,
                key=f"motivo_{idx}"
            )
            
            if st.button("🏁 Finalizar", key=f"finalizar_{idx}"):
                if motivo.strip():
                    sucesso, msg = finalizar_relacionamento(rel.get('id'), resultado, motivo)
                    if sucesso:
                        st.success(msg)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Informe o motivo")
                    
def exibir_estatisticas_relacionamentos(df_relacionamentos):
    """
    Exibe métricas dos relacionamentos
    
    Args:
        df_relacionamentos: DataFrame com relacionamentos
    """
    st.subheader("📈 Estatísticas")
    
    if df_relacionamentos.empty:
        st.info("📊 Nenhum relacionamento para exibir estatísticas")
        return
    
    # Calcular métricas
    df_temp = df_relacionamentos.copy()
    df_temp['data_envio'] = pd.to_datetime(df_temp['data_envio'], errors='coerce')
    hoje = pd.Timestamp.now(tz='UTC').tz_localize(None)
    df_temp['data_envio'] = df_temp['data_envio'].dt.tz_localize(None)
    df_temp['dias_passados'] = (hoje - df_temp['data_envio']).dt.days
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total", len(df_relacionamentos))
    
    with col2:
        criticos = len(df_temp[df_temp['dias_passados'] >= 75])
        st.metric("🚨 Críticos", criticos)
    
    with col3:
        vencidos = len(df_temp[df_temp['dias_passados'] >= 90])
        st.metric("⏰ Vencidos", vencidos)
    
    with col4:
        ativos = len(df_temp[df_temp['dias_passados'] < 90])
        st.metric("✅ Ativos", ativos)
        
def gerenciar_relacionamentos():
    """
    Gestão de relacionamentos candidato-vaga
    FUNÇÃO ORQUESTRADORA - Apenas coordena os módulos
    """
    st.header("🔗 Relacionar Candidatos com Vagas")
    
    # 1. CARREGAR DADOS
    df_candidatos, df_vagas, df_relacionamentos, total = carregar_dados_relacionamentos()
    
    # 2. FORMULÁRIO DE CRIAÇÃO
    criou_novo = criar_formulario_novo_relacionamento(df_candidatos, df_vagas)
    
    if criou_novo:
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # 3. RELACIONAMENTOS EXISTENTES
    st.subheader("📊 Relacionamentos Existentes")
    
    if df_relacionamentos.empty:
        st.info("ℹ️ Nenhum relacionamento cadastrado ainda")
        return
    
    # 4. ESTATÍSTICAS
    exibir_estatisticas_relacionamentos(df_relacionamentos)
    
    st.markdown("---")
    
    # 5. PAGINAÇÃO
    pagina_atual, offset = exibir_paginacao(
        total_registros=total,
        registros_por_pagina=100,
        key_prefix="relacionamentos"
    )
    
    if offset > 0:
        df_relacionamentos = carregar_relacionamentos(limite=100, offset=offset)
    
    # 6. LISTA DE CARDS
    for idx, rel in enumerate(df_relacionamentos.to_dict('records')):
        exibir_card_relacionamento(rel, idx)

def gerenciar_metricas():
    """Nova aba dedicada às métricas de negócio"""
    st.header("📊 Métricas de Negócio")
    
    # Seletor de período
    col_periodo, col_espaco = st.columns([1, 2])
    
    with col_periodo:
        periodo_analise = st.selectbox(
            "📅 Período de análise:",
            ["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"],
            key="periodo_metricas_aba"
        )
    
    # Converter período para data limite
    data_limite_map = {
        "Último mês": datetime.now() - timedelta(days=30),
        "Últimos 3 meses": datetime.now() - timedelta(days=90),
        "Últimos 6 meses": datetime.now() - timedelta(days=180),
        "Último ano": datetime.now() - timedelta(days=365)
    }
    data_limite = data_limite_map[periodo_analise]
    
    # Calcular e exibir métricas
    with st.spinner("📊 Calculando métricas de negócio..."):
        metricas = calcular_metricas_negocio(data_limite)
        exibir_dashboard_metricas(metricas, periodo_analise)

# =====================================
# FUNÇÃO PRINCIPAL
# =====================================

def main():
    """
    Função principal com sistema de abas
    ✅ CORRIGIDO: Sidebar aparece sempre
    """
    # CABEÇALHO
    st.markdown(f"""
    <div class="main-header">
        <h1>🏠 R.O Recrutamento - Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
            Bem-vindo(a), {name}!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ✅ SIDEBAR GLOBAL (SEMPRE APARECE)
    with st.sidebar:
        st.title("📊 Menu Principal")
        
        # ⭐ Exibir info do usuário
        exibir_info_usuario_sidebar(name, username, authenticator)
        
        st.markdown("---")
        
        # Informações do sistema
        st.caption("**Sistema:**")
        st.caption("R.O Recrutamento v2.0")
        st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    
    # ✅ EXECUTAR EXPIRAÇÃO AUTOMÁTICA
    with st.spinner("🔄 Verificando relacionamentos antigos..."):
        expirar_relacionamentos_antigos()
    
    # SISTEMA DE ABAS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Candidatos", 
        "💼 Vagas", 
        "🔗 Relacionamentos", 
        "📊 Métricas", 
        "💾 Backups"
    ])
    
    with tab1:
        gerenciar_candidatos()
    
    with tab2:
        gerenciar_vagas()
    
    with tab3:
        gerenciar_relacionamentos()
    
    with tab4:
        gerenciar_metricas()
        
    with tab5:
        gerenciar_backups()

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
    main()