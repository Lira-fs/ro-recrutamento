# app/streamlit_app.py - VERSÃO CORRIGIDA
import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Adicionar pasta backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato_completa  # ✅ Import correto

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

# 🔥 NOVA FUNÇÃO SIMPLIFICADA (adicione no início do arquivo, após as outras funções)
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
        import datetime
        
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
            'data_qualificacao': datetime.datetime.now().isoformat(),
            'created_at': datetime.datetime.now().isoformat()
        }
        
        # Inserir no banco
        resultado = supabase.table('candidatos_qualificados').insert(dados).execute()
        
        if resultado.data and len(resultado.data) > 0:
            return True, certificado_numero
        else:
            return False, None
            
    except Exception as e:
        # Mostrar erro na interface
        st.error(f"Erro técnico: {str(e)}")
        return False, None

# Adicionar no app/streamlit_app.py

def carregar_candidatos_qualificados():
    """Carrega candidatos qualificados com dados combinados - VERSÃO CORRIGIDA"""
    try:
        supabase = get_supabase_client()
        
        # ✅ USAR API PADRÃO DO SUPABASE (não execute_sql)
        # Primeiro, buscar qualificações
        qualificacoes = supabase.table('candidatos_qualificados').select('*').execute()
        
        if not qualificacoes.data:
            return pd.DataFrame()  # Retorna vazio se não há qualificações
        
        # Buscar candidatos que estão qualificados
        candidatos_ids = [q['candidato_id'] for q in qualificacoes.data]
        
        candidatos = supabase.table('candidatos').select('*').in_('id', candidatos_ids).execute()
        
        if not candidatos.data:
            return pd.DataFrame()
        
        # Combinar dados manualmente
        dados_combinados = []
        for candidato in candidatos.data:
            # Encontrar qualificação correspondente
            qualificacao = next((q for q in qualificacoes.data if q['candidato_id'] == candidato['id']), None)
            
            if qualificacao:
                # Combinar dados
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
    """Carrega candidatos que ainda não foram qualificados - VERSÃO CORRIGIDA"""
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

def qualificar_candidato(candidato_id, nota, observacoes, instrutor):
    """Move candidato para tabela de qualificados - VERSÃO COM DEBUG"""
    try:
        st.write(f"🔄 Debug: Iniciando qualificação do candidato {candidato_id}")
        
        supabase = get_supabase_client()
        
        # Buscar dados do candidato
        st.write("📋 Debug: Buscando dados do candidato...")
        candidato_response = supabase.table('candidatos').select('formulario_id').eq('id', candidato_id).execute()
        
        if not candidato_response.data:
            st.error("❌ Debug: Candidato não encontrado!")
            return False, None
        
        tipo_treinamento = candidato_response.data[0].get('formulario_id', 'GERAL')
        st.write(f"✅ Debug: Tipo de treinamento: {tipo_treinamento}")
        
        # Gerar número do certificado
        import uuid
        certificado_numero = f"RO-{tipo_treinamento.upper().replace('CANDI-', '')}-{str(uuid.uuid4())[:8]}"
        st.write(f"🎓 Debug: Certificado gerado: {certificado_numero}")
        
        dados_qualificacao = {
            'candidato_id': candidato_id,
            'nota_treinamento': nota,
            'observacoes_treinamento': observacoes,
            'instrutor_responsavel': instrutor,
            'tipo_treinamento': tipo_treinamento,
            'certificado_numero': certificado_numero,
            'certificado_emitido': True if nota >= 7 else False,
            'data_qualificacao': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        st.write("💾 Debug: Tentando inserir no banco...")
        st.write(f"📊 Debug: Dados a inserir: {dados_qualificacao}")
        
        # Inserir na tabela
        result = supabase.table('candidatos_qualificados').insert(dados_qualificacao).execute()
        
        st.write(f"📤 Debug: Resultado da inserção: {result}")
        
        if result.data:
            st.write("✅ Debug: Inserção bem-sucedida!")
            return True, certificado_numero
        else:
            st.write("❌ Debug: Falha na inserção!")
            return False, None
        
    except Exception as e:
        st.error(f"💥 Debug: Erro na função qualificar_candidato: {str(e)}")
        
        # Mostrar traceback completo
        import traceback
        st.code(traceback.format_exc())
        
        return False, None
    """Move candidato para tabela de qualificados - VERSÃO CORRIGIDA"""
    try:
        supabase = get_supabase_client()
        
        # Buscar dados do candidato
        candidato_response = supabase.table('candidatos').select('formulario_id').eq('id', candidato_id).execute()
        
        if not candidato_response.data:
            st.error("Candidato não encontrado!")
            return False, None
        
        tipo_treinamento = candidato_response.data[0].get('formulario_id', 'GERAL')
        
        # Gerar número do certificado
        import uuid
        certificado_numero = f"RO-{tipo_treinamento.upper().replace('CANDI-', '')}-{str(uuid.uuid4())[:8]}"
        
        dados_qualificacao = {
            'candidato_id': candidato_id,
            'nota_treinamento': nota,
            'observacoes_treinamento': observacoes,
            'instrutor_responsavel': instrutor,
            'tipo_treinamento': tipo_treinamento,
            'certificado_numero': certificado_numero,
            'certificado_emitido': True if nota >= 7 else False,
            'data_qualificacao': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        # Inserir na tabela
        result = supabase.table('candidatos_qualificados').insert(dados_qualificacao).execute()
        
        if result.data:
            return True, certificado_numero
        else:
            return False, None
        
    except Exception as e:
        st.error(f"Erro ao qualificar candidato: {str(e)}")
        return False, None        

# 🔥 ADICIONE ESTA FUNÇÃO após a função formatar_funcao()

def formatar_whatsapp_link(numero_whatsapp):
    """Converte número do WhatsApp em link clicável"""
    if not numero_whatsapp or numero_whatsapp == 'Não informado' or str(numero_whatsapp).lower() == 'nan':
        return "Não informado"
    
    # Limpar o número (remover espaços, parênteses, hífens, etc.)
    numero_limpo = str(numero_whatsapp)
    numero_limpo = ''.join(filter(str.isdigit, numero_limpo))
    
    # Verificar se o número tem pelo menos 10 dígitos
    if len(numero_limpo) < 10:
        return f"📲 {numero_whatsapp} (número inválido)"
    
    # Se não começar com 55 (Brasil), adicionar
    if not numero_limpo.startswith('55'):
        # Se começar com 11, 21, etc. (códigos de área brasileiros), adicionar 55
        if len(numero_limpo) >= 10:
            numero_limpo = '55' + numero_limpo
    
    # Criar link do WhatsApp
    link_whatsapp = f"https://wa.me/{numero_limpo}"
    
    # Formatar número para exibição (com máscara brasileira)
    if len(numero_limpo) == 13:  # 55 + 11 + 9 dígitos
        numero_formatado = f"+{numero_limpo[:2]} ({numero_limpo[2:4]}) {numero_limpo[4:9]}-{numero_limpo[9:]}"
    elif len(numero_limpo) == 12:  # 55 + 11 + 8 dígitos (número antigo)
        numero_formatado = f"+{numero_limpo[:2]} ({numero_limpo[2:4]}) {numero_limpo[4:8]}-{numero_limpo[8:]}"
    else:
        numero_formatado = numero_limpo
    
    return f'<a href="{link_whatsapp}" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">📲 {numero_formatado}</a>'

# 🔥 SUBSTITUA ESTA LINHA no código onde exibe as informações do candidato: 

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

    # 🆕 NOVO FILTRO DE QUALIFICAÇÃO
    tipo_visualizacao = st.sidebar.selectbox(
        "Visualizar:",
        [
            "Todos os candidatos",
            "Candidatos qualificados", 
            "Pendentes de qualificação"
        ]
    )

    # 🔄 CARREGAMENTO CONDICIONAL BASEADO NO FILTRO
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

                # 🆕 MOSTRAR STATUS DE QUALIFICAÇÃO
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
                            
                            # ✅ ATUALIZADO: Função retorna PDF e nome do arquivo
                            resultado = gerar_ficha_candidato_completa(candidato.to_dict())
                            
                            # Verificar se retornou tupla (pdf_bytes, nome_arquivo) ou só pdf_bytes
                            if isinstance(resultado, tuple):
                                pdf_bytes, nome_arquivo = resultado
                            else:
                                pdf_bytes = resultado
                                # Fallback para nome de arquivo se função antiga
                                nome_limpo = candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
                                import re
                                nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
                                data_criacao = datetime.now().strftime('%d%m%Y')
                                nome_arquivo = f"{nome_limpo}-{data_criacao}.pdf"
                            
                            # Salvar no session_state
                            st.session_state[f"pdf_data_{candidato.get('id')}"] = pdf_bytes
                            st.session_state[f"pdf_nome_{candidato.get('id')}"] = nome_arquivo
                            
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
                        with st.expander("🔍 Detalhes técnicos do erro"):
                            st.code(traceback.format_exc())

                # 🆕 BOTÃO QUALIFICAR (apenas para pendentes)
                # 🔥 SUBSTITUA TODO O BLOCO DO BOTÃO QUALIFICAR POR ESTA VERSÃO SIMPLIFICADA

                # 🆕 BOTÃO QUALIFICAR (apenas para pendentes) - VERSÃO SIMPLIFICADA
                if 'data_qualificacao' not in candidato.index:
                    
                    # Chave única para este candidato
                    candidato_id = candidato.get('id')
                    
                    # Container para organizar
                    with st.container():
                        st.markdown("---")
                        st.markdown("### 🎓 Qualificar Candidato")
                        
                        # Formulário simples com chaves únicas
                        with st.form(key=f"qualificacao_form_{candidato_id}", clear_on_submit=False):
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nota = st.slider("Nota do treinamento (0-10)", 0, 10, 7)
                                
                            with col2:
                                instrutor = st.text_input("Nome do instrutor")
                            
                            observacoes = st.text_area("Observações sobre o treinamento", height=100)
                            
                            # Botão submit
                            submitted = st.form_submit_button("✅ QUALIFICAR CANDIDATO", type="primary")
                            
                            if submitted:
                                # Validação básica
                                if not instrutor.strip():
                                    st.error("❌ O nome do instrutor é obrigatório!")
                                else:
                                    # Tentar qualificar
                                    with st.spinner("Processando qualificação..."):
                                        sucesso, certificado = qualificar_candidato_simples(candidato_id, nota, observacoes, instrutor)
                                        
                                        if sucesso:
                                            st.success(f"🎉 Candidato qualificado com sucesso!")
                                            st.success(f"🎓 Certificado: {certificado}")
                                            st.balloons()
                                            
                                            # Aguardar um pouco antes de recarregar
                                            import time
                                            time.sleep(2)
                                            
                                            # Limpar cache
                                            st.cache_data.clear()
                                            
                                            # Mostrar mensagem e recarregar
                                            st.info("🔄 Recarregando página...")
                                            st.rerun()
                                        else:
                                            st.error("❌ Erro ao qualificar candidato. Tente novamente.")      
                
                # Botão de download (sempre visível se PDF foi gerado)
                if st.session_state.get(f"pdf_data_{candidato.get('id')}") is not None:
                    pdf_data = st.session_state[f"pdf_data_{candidato.get('id')}"]
                    nome_arquivo = st.session_state.get(f"pdf_nome_{candidato.get('id')}", f"ficha_{candidato.get('id')}.pdf")
                    
                    st.download_button(
                        label="📥 📱 BAIXAR FICHA PDF",
                        data=pdf_data,
                        file_name=nome_arquivo,  # ✅ NOME DINÂMICO
                        mime="application/pdf",
                        key=f"download_{candidato.get('id')}",
                        type="primary"  # Botão verde destacado
                    )
                    
                    st.success(f"✅ PDF pronto: {nome_arquivo}")
                    
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