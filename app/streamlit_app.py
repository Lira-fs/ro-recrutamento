# app/streamlit_app.py - VERSÃO CORRIGIDA E MELHORADA
import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Adicionar pasta backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato_completa, gerar_ficha_vaga_completa

# =====================================
# CONFIGURAÇÃO DA PÁGINA (APENAS UMA VEZ!)
# =====================================

st.set_page_config(
    page_title="R.O Recrutamento - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# FUNÇÕES DE VAGAS (NOVAS)
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
    """Atualiza status da vaga e sua situação"""
    try:
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
            'status': nova_situacao,  # Atualizar situação também
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
    """Relaciona candidato com vaga permitindo definir status inicial"""
    try:
        supabase = get_supabase_client()
        
        # Criar observação automática baseada no status
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        status_map = {
            'enviado': 'Candidato enviado ao cliente',
            'em_analise': 'Cliente recebeu candidato e está analisando',
            'entrevista_agendada': 'Entrevista foi agendada',
            'aprovado': 'Cliente aprovou o candidato',
            'rejeitado': 'Cliente rejeitou o candidato',
            'contratado': 'Candidato foi contratado',
            'cancelado': 'Processo foi cancelado'
        }
        
        # Construir observação inicial com histórico automático
        observacao_automatica = f"[SISTEMA - {timestamp}] Relacionamento criado com status: {status_inicial.upper().replace('_', ' ')}. {status_map.get(status_inicial, '')}"
        
        if data_entrevista:
            data_formatada = data_entrevista.strftime('%d/%m/%Y às %H:%M')
            observacao_automatica += f"\n[SISTEMA - {timestamp}] Entrevista agendada para: {data_formatada}"
        
        # Combinar observação do usuário com a automática
        observacao_final = observacao.strip() if observacao.strip() else ""
        if observacao_final:
            observacao_completa = f"{observacao_final}\n\n{observacao_automatica}"
        else:
            observacao_completa = observacao_automatica
        
        # Dados para inserir no relacionamento
        dados_relacao = {
            'candidato_id': candidato_id,
            'vaga_id': vaga_id,
            'status_processo': status_inicial,
            'observacoes': observacao_completa
        }
        
        # Adicionar data da entrevista se fornecida
        if data_entrevista:
            dados_relacao['data_entrevista'] = data_entrevista.isoformat()
        
        result = supabase.table('candidatos_vagas').insert(dados_relacao).execute()
        
        if result.data:
            # Adicionar observação automática na vaga
            obs_vaga = f"Candidato relacionado com status '{status_inicial.upper().replace('_', ' ')}'. {observacao.strip()}"
            if data_entrevista:
                obs_vaga += f" Entrevista: {data_entrevista.strftime('%d/%m/%Y às %H:%M')}"
            
            adicionar_observacao_vaga(vaga_id, obs_vaga, 'candidato_enviado')
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

# =====================================
# PÁGINAS/ABAS DO SISTEMA
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
        ],
        key="tipo_visualizacao_candidatos"
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
                whatsapp_link = formatar_whatsapp_link(candidato.get('whatsapp'))
                st.markdown(f"**📲 Whatsapp:** {whatsapp_link}", unsafe_allow_html=True)
                st.write(f"**📍 Endereço:** {candidato.get('endereco', 'Não informado')}")
                st.write(f"**👨‍👩‍👧‍👦 Filhos:** {'Sim' if candidato.get('tem_filhos') else 'Não'}")
                st.write(f"**🚗 CNH:** {'Sim' if candidato.get('possui_cnh') else 'Não'}")
                
                if candidato.get('created_at'):
                    data_cadastro = pd.to_datetime(candidato['created_at']).strftime('%d/%m/%Y às %H:%M')
                    st.write(f"**📅 Cadastrado em:** {data_cadastro}")

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
            
            with col2:
                # Geração de PDF
                nome_arquivo = f"ficha_{candidato.get('nome_completo', 'candidato').replace(' ', '_')}_{candidato.get('id', 'sem_id')}.pdf"
                
                if f"pdf_data_{candidato.get('id')}" not in st.session_state:
                    st.session_state[f"pdf_data_{candidato.get('id')}"] = None
                
                if st.button(f"📄 Gerar Ficha PDF", key=f"pdf_{candidato.get('id')}"):
                    try:
                        with st.spinner("Gerando PDF..."):
                            st.write("🔍 Preparando dados do candidato...")
                            
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

                # Sistema de qualificação
                if 'data_qualificacao' not in candidato.index:
                    candidato_id = candidato.get('id')
                    
                    with st.container():
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
                
                # Botão de download
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

def gerenciar_vagas():
    """Nova funcionalidade para gestão de vagas"""
    st.header("💼 Gestão de Vagas")
    
    # SIDEBAR - FILTROS
    with st.sidebar:
        st.subheader("🔍 Filtros de Vagas")
        
        filtro_status = st.selectbox(
            "Status da vaga:",
            ["Todas", "ativa", "preenchida", "pausada", "cancelada", "em_andamento"],
            key="filtro_status_vagas"
        )
        
        filtro_urgencia = st.selectbox(
            "Urgência:",
            ["Todas", "imediato", "ate-30-dias", "flexivel"],
            key="filtro_urgencia_vagas"
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
        # OBTER STATUS FORMATADO
        status_atual = vaga.get('status_detalhado', vaga.get('status', 'ativa'))
        status_display, status_color = formatar_status_vaga(status_atual)
        
        with st.expander(
            f"{formatar_funcao_vaga(vaga.get('formulario_id', ''))} | "
            f"{vaga.get('nome', '')} {vaga.get('sobrenome', '')} | "
            f"💰 R$ {vaga.get('salario_oferecido', 'N/A')} | "
            f"📍 {vaga.get('cidade', 'N/A')} | "
            f"{status_display}",
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

def gerenciar_relacionamentos():
    """Gestão de relacionamentos com interface melhorada"""
    st.header("🔗 Relacionar Candidatos com Vagas")
    
    # CARREGAR DADOS
    df_candidatos = carregar_candidatos()
    df_vagas = carregar_vagas()
    
    if df_candidatos.empty or df_vagas.empty:
        st.warning("⚠️ É necessário ter candidatos e vagas cadastrados.")
        return
    
    # FORMULÁRIO DE RELACIONAMENTO
    st.subheader("➕ Criar Novo Relacionamento")
    
    with st.form("relacionar_candidato_vaga"):
        # SEÇÃO DE BUSCA DE CANDIDATOS
        st.markdown("#### 👤 Selecionar Candidato")
        
        col_busca_cand, col_filtro_cand = st.columns([2, 1])
        
        with col_busca_cand:
            busca_candidato = st.text_input(
                "🔍 Buscar candidato por nome:",
                placeholder="Digite nome do candidato...",
                key="busca_candidato_relacionamento"
            )
        
        with col_filtro_cand:
            filtro_funcao_candidato = st.selectbox(
                "Filtrar por função:",
                ["Todas"] + sorted(df_candidatos['formulario_id'].dropna().unique().tolist()),
                key="filtro_funcao_candidato"
            )
        
        # FILTRAR CANDIDATOS BASEADO NA BUSCA
        df_candidatos_filtrados = df_candidatos.copy()
        
        if busca_candidato.strip():
            df_candidatos_filtrados = df_candidatos_filtrados[
                df_candidatos_filtrados['nome_completo'].str.contains(busca_candidato, case=False, na=False)
            ]
        
        if filtro_funcao_candidato != "Todas":
            df_candidatos_filtrados = df_candidatos_filtrados[
                df_candidatos_filtrados['formulario_id'] == filtro_funcao_candidato
            ]
        
        if df_candidatos_filtrados.empty:
            st.warning("⚠️ Nenhum candidato encontrado com os filtros aplicados. Ajuste a busca.")
            candidato_selecionado = None
        else:
            st.info(f"📊 Encontrados {len(df_candidatos_filtrados)} candidatos")
            candidato_selecionado = st.selectbox(
                f"Escolher candidato ({len(df_candidatos_filtrados)} opções):",
                options=df_candidatos_filtrados['id'].tolist(),
                format_func=lambda x: f"{df_candidatos_filtrados[df_candidatos_filtrados['id'] == x]['nome_completo'].iloc[0]} - {formatar_funcao(df_candidatos_filtrados[df_candidatos_filtrados['id'] == x]['formulario_id'].iloc[0])}",
                key="select_candidato_filtrado"
            )
        
        st.markdown("---")
        
        # SEÇÃO DE BUSCA DE VAGAS
        st.markdown("#### 💼 Selecionar Vaga")
        
        col_busca_vaga, col_filtro_vaga = st.columns([2, 1])
        
        with col_busca_vaga:
            busca_vaga = st.text_input(
                "🔍 Buscar vaga por proprietário:",
                placeholder="Digite nome do proprietário...",
                key="busca_vaga_relacionamento"
            )
        
        with col_filtro_vaga:
            filtro_tipo_vaga = st.selectbox(
                "Filtrar por tipo:",
                ["Todas"] + sorted(df_vagas['formulario_id'].dropna().unique().tolist()),
                key="filtro_tipo_vaga"
            )
        
        # FILTRAR VAGAS BASEADO NA BUSCA
        df_vagas_filtradas = df_vagas.copy()
        
        if busca_vaga.strip():
            # Criar coluna nome_completo_proprietario se não existir
            if 'nome_completo_proprietario' not in df_vagas_filtradas.columns:
                df_vagas_filtradas['nome_completo_proprietario'] = df_vagas_filtradas['nome'].fillna('') + ' ' + df_vagas_filtradas['sobrenome'].fillna('')
            
            df_vagas_filtradas = df_vagas_filtradas[
                df_vagas_filtradas['nome_completo_proprietario'].str.contains(busca_vaga, case=False, na=False)
            ]
        
        if filtro_tipo_vaga != "Todas":
            df_vagas_filtradas = df_vagas_filtradas[
                df_vagas_filtradas['formulario_id'] == filtro_tipo_vaga
            ]
        
        # Filtrar apenas vagas ativas por padrão
        df_vagas_filtradas = df_vagas_filtradas[
            df_vagas_filtradas.get('status_detalhado', df_vagas_filtradas.get('status', 'ativa')).isin(['ativa', 'em_andamento'])
        ]
        
        if df_vagas_filtradas.empty:
            st.warning("⚠️ Nenhuma vaga ativa encontrada com os filtros aplicados. Ajuste a busca.")
            vaga_selecionada = None
        else:
            st.info(f"📊 Encontradas {len(df_vagas_filtradas)} vagas ativas")
            vaga_selecionada = st.selectbox(
                f"Escolher vaga ({len(df_vagas_filtradas)} opções):",
                options=df_vagas_filtradas['id'].tolist(),
                format_func=lambda x: f"{df_vagas_filtradas[df_vagas_filtradas['id'] == x]['nome'].iloc[0]} {df_vagas_filtradas[df_vagas_filtradas['id'] == x]['sobrenome'].iloc[0]} - {formatar_funcao_vaga(df_vagas_filtradas[df_vagas_filtradas['id'] == x]['formulario_id'].iloc[0])} - R$ {df_vagas_filtradas[df_vagas_filtradas['id'] == x]['salario_oferecido'].iloc[0]}",
                key="select_vaga_filtrada"
            )
        
        st.markdown("---")
        
        # RESTO DO FORMULÁRIO (status, entrevista, etc.)
        # NOVO: Campo para definir status inicial
        col_status1, col_status2 = st.columns(2)
        
        with col_status1:
            status_inicial = st.selectbox(
                "📋 Status inicial do relacionamento:",
                ["enviado", "em_analise", "entrevista_agendada", "aprovado", "rejeitado", "contratado", "cancelado"],
                index=0,  # Padrão é "enviado"
                key="status_inicial_relacionamento"
            )
        
        with col_status2:
            st.write("**Legenda dos Status:**")
            st.caption("• **Enviado:** Candidato foi enviado ao cliente")
            st.caption("• **Em Análise:** Cliente está analisando o candidato")
            st.caption("• **Entrevista Agendada:** Entrevista marcada")
            st.caption("• **Aprovado:** Cliente aprovou o candidato")
            st.caption("• **Contratado:** Candidato foi contratado")
        
        # CAMPOS ESPECIAIS PARA ENTREVISTA
        data_entrevista_inicial = None
        if status_inicial == "entrevista_agendada":
            st.markdown("---")
            st.write("**📅 Dados da Entrevista (obrigatório para status 'entrevista_agendada'):**")
            
            col_data_inicial, col_hora_inicial = st.columns(2)
            
            with col_data_inicial:
                data_ent_inicial = st.date_input(
                    "Data da entrevista:",
                    value=datetime.now().date(),
                    key="data_entrevista_inicial"
                )
            
            with col_hora_inicial:
                hora_ent_inicial = st.time_input(
                    "Hora da entrevista:",
                    value=datetime.now().replace(second=0, microsecond=0).time(),
                    key="hora_entrevista_inicial"
                )
            
            data_entrevista_inicial = datetime.combine(data_ent_inicial, hora_ent_inicial)
            st.success(f"✅ Entrevista será criada para: **{data_entrevista_inicial.strftime('%d/%m/%Y às %H:%M')}**")
        
        observacao_inicial = st.text_area(
            "📝 Observação inicial:",
            placeholder="Ex: Candidato enviado via WhatsApp às 14h30. Cliente solicitou entrevista presencial.",
            height=80
        )
        
        # VALIDAÇÃO E SUBMISSÃO
        if st.form_submit_button("🔗 Criar Relacionamento", type="primary"):
            if candidato_selecionado is None:
                st.error("❌ Selecione um candidato válido!")
            elif vaga_selecionada is None:
                st.error("❌ Selecione uma vaga válida!")
            elif status_inicial == "entrevista_agendada" and not data_entrevista_inicial:
                st.error("❌ Para criar relacionamento com status 'entrevista_agendada', é obrigatório definir data e hora!")
            else:
                if relacionar_candidato_vaga_com_status(candidato_selecionado, vaga_selecionada, observacao_inicial, status_inicial, data_entrevista_inicial):
                    st.success("✅ Relacionamento criado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao criar relacionamento (pode já existir)")
    
    st.markdown("---")
    
    # MOSTRAR RELACIONAMENTOS EXISTENTES
    st.subheader("📊 Relacionamentos Existentes")
    
    df_relacionamentos = carregar_relacionamentos()
    
    if not df_relacionamentos.empty:
        # INTERFACE MELHORADA COM STREAMLIT NATIVO
        for idx, rel in df_relacionamentos.iterrows():
            # CALCULAR MÉTRICAS DE TEMPO
            data_envio = pd.to_datetime(rel.get('data_envio'))
            data_criacao = pd.to_datetime(rel.get('created_at', rel.get('data_envio')))
            
            # Normalizar timezone
            if data_envio.tz is not None:
                hoje = pd.Timestamp.now(tz='UTC').tz_convert(data_envio.tz)
            else:
                hoje = pd.Timestamp.now().tz_localize(None)
                data_envio = data_envio.tz_localize(None) if data_envio.tz is not None else data_envio
                data_criacao = data_criacao.tz_localize(None) if data_criacao.tz is not None else data_criacao
            
            dias_passados = (hoje - data_envio).days
            tres_meses = data_envio + pd.Timedelta(days=90)
            dias_restantes = (tres_meses - hoje).days
            
            status_atual = rel.get('status_processo', 'enviado')
            
            # CONTAINER PRINCIPAL
            with st.container():
                # HEADER COM STATUS
                col_status, col_prazo = st.columns([2, 1])
                
                with col_status:
                    if status_atual == 'enviado':
                        st.info("📤 **CANDIDATO ENVIADO**")
                    elif status_atual == 'em_analise':
                        st.warning("🔍 **EM ANÁLISE PELO CLIENTE**")
                    elif status_atual == 'entrevista_agendada':
                        st.success("📅 **ENTREVISTA AGENDADA**")
                    elif status_atual == 'aprovado':
                        st.success("✅ **CANDIDATO APROVADO**")
                    elif status_atual == 'contratado':
                        st.success("🎉 **CANDIDATO CONTRATADO**")
                    elif status_atual == 'rejeitado':
                        st.error("❌ **CANDIDATO REJEITADO**")
                    elif status_atual == 'cancelado':
                        st.error("ℹ️ **PROCESSO CANCELADO**")
                
                with col_prazo:
                    if dias_restantes <= 0:
                        st.error(f"🚨 Vencido há {abs(dias_restantes)} dias")
                    elif dias_restantes <= 15:
                        st.error(f"⚠️ {dias_restantes} dias restantes (CRÍTICO)")
                    elif dias_restantes <= 30:
                        st.warning(f"⏳ {dias_restantes} dias restantes")
                    else:
                        st.success(f"✅ {dias_restantes} dias restantes")
                
                # DESTAQUE PARA ENTREVISTA AGENDADA
                if status_atual == 'entrevista_agendada' and rel.get('data_entrevista'):
                    data_entrevista = pd.to_datetime(rel.get('data_entrevista'))
                    if data_entrevista.tz is not None:
                        data_entrevista = data_entrevista.tz_convert(hoje.tz if hoje.tz else 'UTC')
                    else:
                        data_entrevista = data_entrevista.tz_localize(None)
                    
                    dias_ate_entrevista = (data_entrevista - hoje).days
                    
                    if dias_ate_entrevista == 0:
                        st.error(f"🚨 **ENTREVISTA É HOJE às {data_entrevista.strftime('%H:%M')}!**")
                    elif dias_ate_entrevista == 1:
                        st.warning(f"⚠️ **ENTREVISTA É AMANHÃ às {data_entrevista.strftime('%H:%M')}!**")
                    elif dias_ate_entrevista > 0:
                        st.info(f"📅 **Entrevista em {dias_ate_entrevista} dias:** {data_entrevista.strftime('%d/%m/%Y às %H:%M')}")
                    else:
                        st.error(f"⚠️ **Entrevista atrasada há {abs(dias_ate_entrevista)} dias!**")
                
                # INFORMAÇÕES ORGANIZADAS
                col_pessoas, col_datas, col_prazo_detalhado = st.columns([2, 2, 1])
                
                with col_pessoas:
                    st.markdown("**👥 PESSOAS ENVOLVIDAS**")
                    st.write(f"👤 **Candidato:** {rel.get('nome_completo', 'N/A')}")
                    st.write(f"🏷️ **Função:** {formatar_funcao(rel.get('tipo_candidato', ''))}")
                    st.write(f"🏠 **Proprietário:** {rel.get('nome_proprietario', 'N/A')}")
                    st.write(f"🎯 **Vaga:** {formatar_funcao_vaga(rel.get('tipo_vaga', ''))}")
                
                with col_datas:
                    st.markdown("**📅 CRONOLOGIA DETALHADA**")
                    st.write(f"📅 **Relacionamento criado:** {data_criacao.strftime('%d/%m/%Y às %H:%M')}")
                    st.write(f"📤 **Candidato enviado:** {data_envio.strftime('%d/%m/%Y às %H:%M')}")
                    st.write(f"⏱️ **Tempo ativo:** {dias_passados} dias")
                    
                    if rel.get('updated_at'):
                        ultima_atualizacao = pd.to_datetime(rel.get('updated_at'))
                        if ultima_atualizacao.tz is not None:
                            ultima_atualizacao = ultima_atualizacao.tz_convert(hoje.tz if hoje.tz else 'UTC')
                        else:
                            ultima_atualizacao = ultima_atualizacao.tz_localize(None)
                        st.write(f"🔄 **Última modificação:** {ultima_atualizacao.strftime('%d/%m/%Y às %H:%M')}")
                
                with col_prazo_detalhado:
                    st.markdown("**⏰ PRAZO 90 DIAS**")
                    if dias_restantes <= 0:
                        st.error(f"🚨 **Vencido**\n{abs(dias_restantes)} dias")
                    elif dias_restantes <= 15:
                        st.error(f"⚠️ **Crítico**\n{dias_restantes} dias")
                    elif dias_restantes <= 30:
                        st.warning(f"⏳ **Atenção**\n{dias_restantes} dias")
                    else:
                        st.success(f"✅ **Normal**\n{dias_restantes} dias")
                    
                    # BARRA DE PROGRESSO
                    progresso = max(0, min(100, (90 - dias_passados) / 90 * 100))
                    st.progress(progresso / 100)
                    st.caption(f"{progresso:.0f}% do prazo restante")
                
                # OBSERVAÇÕES (SE EXISTIREM)
                if rel.get('observacoes') and rel.get('observacoes').strip():
                    with st.expander("💬 Ver Histórico Completo", expanded=False):
                        # Dividir e colorir observações por tipo
                        observacoes_linhas = rel.get('observacoes').split('\n')
                        for linha in observacoes_linhas:
                            linha = linha.strip()
                            if linha:
                                if '[SISTEMA -' in linha:
                                    st.info(f"🤖 {linha}")
                                elif 'TROCA DE CANDIDATO' in linha or 'Candidato alterado' in linha:
                                    st.warning(f"🔄 {linha}")
                                elif 'Status alterado' in linha:
                                    st.info(f"📋 {linha}")
                                elif 'Entrevista agendada' in linha:
                                    st.success(f"📅 {linha}")
                                else:
                                    st.write(f"💬 {linha}")
                
                # PAINEL DE CONTROLE
                with st.expander("⚙️ Painel de Controle", expanded=False):
                    tab_obs, tab_status, tab_troca, tab_excluir = st.tabs(
                        ["📝 Observações", "🔄 Alterar Status", "🔀 Trocar Candidato", "🗑️ Excluir"]
                    )
                    
                    # ABA OBSERVAÇÕES
                    with tab_obs:
                        st.write("**Adicionar nova observação:**")
                        nova_obs = st.text_area(
                            "Observação:",
                            placeholder="Ex: Cliente solicitou envio do currículo por email",
                            height=80,
                            key=f"obs_{rel.get('id')}"
                        )
                        
                        if st.button("💾 Adicionar", key=f"add_obs_{rel.get('id')}", type="primary"):
                            if nova_obs.strip():
                                observacao_atual = rel.get('observacoes', '')
                                if observacao_atual:
                                    observacao_completa = f"{observacao_atual}\n\n{nova_obs.strip()}"
                                else:
                                    observacao_completa = nova_obs.strip()
                                
                                if atualizar_relacionamento(
                                    rel.get('id'),
                                    nova_observacao=observacao_completa
                                ):
                                    st.success("✅ Observação adicionada!")
                                    st.cache_data.clear()
                                    st.rerun()
                            else:
                                st.error("❌ Digite uma observação")
                    
                    # ABA STATUS
                    with tab_status:
                        col_atual, col_novo = st.columns(2)
                        
                        with col_atual:
                            st.write("**Status Atual:**")
                            st.write(f"📋 {status_atual.upper().replace('_', ' ')}")
                        
                        with col_novo:
                            novo_status = st.selectbox(
                                "Alterar para:",
                                ["enviado", "em_analise", "entrevista_agendada", "aprovado", "rejeitado", "contratado", "cancelado"],
                                key=f"status_{rel.get('id')}"
                            )
                        
                        # CAMPO ESPECIAL PARA ENTREVISTA
                        data_entrevista_nova = None
                        if novo_status == "entrevista_agendada":
                            st.markdown("---")
                            st.write("**📅 Dados da Entrevista:**")
                            
                            col_data, col_hora = st.columns(2)
                            with col_data:
                                data_ent = st.date_input(
                                    "Data:",
                                    value=datetime.now().date(),
                                    key=f"data_ent_{rel.get('id')}"
                                )
                            
                            with col_hora:
                                hora_ent = st.time_input(
                                    "Hora:",
                                    value=datetime.now().replace(second=0, microsecond=0).time(),
                                    key=f"hora_ent_{rel.get('id')}"
                                )
                            
                            data_entrevista_nova = datetime.combine(data_ent, hora_ent)
                            st.info(f"✅ Entrevista será agendada para: **{data_entrevista_nova.strftime('%d/%m/%Y às %H:%M')}**")
                        
                        if st.button("🔄 Confirmar Alteração", key=f"update_status_{rel.get('id')}", type="primary"):
                            if atualizar_relacionamento(
                                rel.get('id'),
                                novo_status=novo_status,
                                data_entrevista=data_entrevista_nova
                            ):
                                st.success("✅ Status atualizado com histórico!")
                                st.cache_data.clear()
                                st.rerun()
                    
                    # ABA TROCA
                    with tab_troca:
                        st.warning("⚠️ **ATENÇÃO:** Trocar candidato **reinicia** a contagem de 90 dias!")
                        
                        candidato_atual = rel.get('nome_completo', 'N/A')
                        st.info(f"**Candidato atual:** {candidato_atual}")
                        
                        if not df_candidatos.empty:
                            novo_candidato_id = st.selectbox(
                                "Novo candidato:",
                                options=df_candidatos['id'].tolist(),
                                format_func=lambda x: f"{df_candidatos[df_candidatos['id'] == x]['nome_completo'].iloc[0]} ({formatar_funcao(df_candidatos[df_candidatos['id'] == x]['formulario_id'].iloc[0])})",
                                key=f"novo_cand_{rel.get('id')}"
                            )
                            
                            motivo_troca = st.text_area(
                                "Motivo da troca:",
                                placeholder="Ex: Cliente rejeitou perfil. Solicitou candidato com mais experiência em cozinha.",
                                key=f"motivo_troca_{rel.get('id')}"
                            )
                            
                            if st.button("🔀 Confirmar Troca", key=f"trocar_{rel.get('id')}", type="secondary"):
                                if motivo_troca.strip():
                                    novo_candidato_nome = df_candidatos[df_candidatos['id'] == novo_candidato_id]['nome_completo'].iloc[0]
                                    
                                    # Adicionar motivo às observações junto com o histórico automático
                                    observacao_atual = rel.get('observacoes', '')
                                    observacao_com_motivo = f"{observacao_atual}\n\nMOTIVO DA TROCA: {motivo_troca.strip()}"
                                    
                                    if atualizar_relacionamento(
                                        rel.get('id'),
                                        novo_candidato_id=novo_candidato_id,
                                        nova_observacao=observacao_com_motivo,
                                        reiniciar_prazo=True
                                    ):
                                        st.success("✅ Candidato trocado! Prazo reiniciado para 90 dias.")
                                        st.cache_data.clear()
                                        st.rerun()
                                else:
                                    st.error("❌ Informe o motivo da troca")
                        else:
                            st.error("❌ Nenhum candidato disponível")
                    
                    # ABA EXCLUIR
                    with tab_excluir:
                        st.error("⚠️ **AÇÃO PERMANENTE E IRREVERSÍVEL!**")
                        st.write("Use apenas se o relacionamento foi criado por engano.")
                        
                        motivo_exclusao = st.text_area(
                            "Motivo da exclusão:",
                            placeholder="Ex: Relacionamento duplicado criado por engano",
                            key=f"motivo_excl_{rel.get('id')}"
                        )
                        
                        confirmar = st.checkbox(
                            "Confirmo que desejo excluir permanentemente",
                            key=f"confirm_{rel.get('id')}"
                        )
                        
                        if st.button("🗑️ EXCLUIR RELACIONAMENTO", key=f"excluir_{rel.get('id')}", type="secondary"):
                            if confirmar and motivo_exclusao.strip():
                                if excluir_relacionamento(rel.get('id')):
                                    st.success("✅ Relacionamento excluído!")
                                    st.cache_data.clear()
                                    st.rerun()
                            else:
                                st.error("❌ Confirme a exclusão e informe o motivo")

                st.markdown("---")
            
        # ESTATÍSTICAS DOS RELACIONAMENTOS
        st.subheader("📈 Estatísticas dos Relacionamentos")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total", len(df_relacionamentos))
        
        with col2:
            criticos = 0
            for idx, r in df_relacionamentos.iterrows():
                try:
                    data_envio = pd.to_datetime(r.get('data_envio'))
                    if data_envio.tz is not None:
                        hoje_calc = pd.Timestamp.now(tz='UTC').tz_convert(data_envio.tz)
                    else:
                        hoje_calc = pd.Timestamp.now().tz_localize(None)
                        data_envio = data_envio.tz_localize(None) if data_envio.tz is not None else data_envio
                    
                    if (hoje_calc - data_envio).days >= 75:
                        criticos += 1
                except:
                    pass
            st.metric("🚨 Críticos", criticos)
        
        with col3:
            vencidos = 0
            for idx, r in df_relacionamentos.iterrows():
                try:
                    data_envio = pd.to_datetime(r.get('data_envio'))
                    if data_envio.tz is not None:
                        hoje_calc = pd.Timestamp.now(tz='UTC').tz_convert(data_envio.tz)
                    else:
                        hoje_calc = pd.Timestamp.now().tz_localize(None)
                        data_envio = data_envio.tz_localize(None) if data_envio.tz is not None else data_envio
                    
                    if (hoje_calc - data_envio).days >= 90:
                        vencidos += 1
                except:
                    pass
            st.metric("⏰ Vencidos", vencidos)
        
        with col4:
            ativos = 0
            for idx, r in df_relacionamentos.iterrows():
                try:
                    data_envio = pd.to_datetime(r.get('data_envio'))
                    if data_envio.tz is not None:
                        hoje_calc = pd.Timestamp.now(tz='UTC').tz_convert(data_envio.tz)
                    else:
                        hoje_calc = pd.Timestamp.now().tz_localize(None)
                        data_envio = data_envio.tz_localize(None) if data_envio.tz is not None else data_envio
                    
                    if (hoje_calc - data_envio).days < 90:
                        ativos += 1
                except:
                    pass
            st.metric("✅ Ativos", ativos)
            
    else:
        st.info("ℹ️ Nenhum relacionamento encontrado.")

# =====================================
# FUNÇÃO PRINCIPAL
# =====================================

def main():
    """Função principal com sistema de abas"""
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