# backend/auth.py
"""
Sistema de Autenticação para R.O Recrutamento
Protege acesso ao dashboard com login seguro
"""

import os
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
from datetime import timedelta

# Carregar variáveis de ambiente
load_dotenv()

def carregar_credenciais_env():
    """
    Carrega credenciais de usuários do arquivo .env
    
    Returns:
        dict: Dicionário com credenciais no formato do streamlit-authenticator
    """
    
    # Estrutura de credenciais
    credentials = {
        'usernames': {}
    }
    
    # Carregar usuários do .env
    usuarios = []
    i = 1
    while True:
        nome = os.getenv(f'AUTH_USER{i}_NAME')
        username = os.getenv(f'AUTH_USER{i}_USERNAME')
        email = os.getenv(f'AUTH_USER{i}_EMAIL')
        password_hash = os.getenv(f'AUTH_USER{i}_PASSWORD_HASH')
        
        if not all([nome, username, email, password_hash]):
            break
        
        credentials['usernames'][username] = {
            'name': nome,
            'email': email,
            'password': password_hash
        }
        
        i += 1
    
    if not credentials['usernames']:
        raise ValueError(
            "❌ Nenhum usuário configurado no .env!\n"
            "Execute: python generate_passwords.py"
        )
    
    return credentials

def configurar_autenticacao():
    """
    Configura e retorna o objeto de autenticação
    
    Returns:
        stauth.Authenticate: Objeto de autenticação configurado
    """
    
    # Carregar credenciais
    credentials = carregar_credenciais_env()
    
    # Configurações de cookie
    cookie_name = os.getenv('AUTH_COOKIE_NAME', 'ro_recrutamento_auth')
    cookie_key = os.getenv('AUTH_COOKIE_KEY', 'ro_secret_key_default')
    cookie_expiry_days = int(os.getenv('AUTH_COOKIE_EXPIRY_DAYS', '30'))
    
    # Criar objeto de autenticação - VERSÃO ATUALIZADA
    try:
        # Tentar versão nova (>= 0.3.0)
        authenticator = stauth.Authenticate(
            credentials=credentials,
            cookie_name=cookie_name,
            cookie_key=cookie_key,
            cookie_expiry_days=cookie_expiry_days
        )
    except TypeError:
        # Fallback para versão antiga (< 0.3.0)
        authenticator = stauth.Authenticate(
            credentials,
            cookie_name,
            cookie_key,
            cookie_expiry_days
        )
    
    return authenticator

def exibir_tela_login():
    """
    Exibe tela de login personalizada
    
    Returns:
        tuple: (nome_usuario, status_autenticacao, username, authenticator)
    """
    
    # CSS personalizado para tela de login
    st.markdown("""
    <style>
        /* Esconder menu e footer do Streamlit na tela de login */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Centralizar conteúdo */
        .block-container {
            padding-top: 5rem;
            padding-bottom: 5rem;
        }
        
        /* Estilo do card de login */
        .login-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 400px;
            margin: 0 auto;
        }
        
        /* Logo e header */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-logo {
            width: 120px;
            margin-bottom: 1rem;
        }
        
        .login-title {
            color: #a65e2e;
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }
        
        .login-subtitle {
            color: #666;
            font-size: 1rem;
            margin: 0.5rem 0 0 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header da página de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-header">
            <h1 class="login-title">🏠 R.O Recrutamento</h1>
            <p class="login-subtitle">Sistema de Gestão de Candidatos e Vagas</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Configurar autenticação
    authenticator = configurar_autenticacao()
    
    # Exibir formulário de login - VERSÃO COMPATÍVEL
    try:
        # Tentar API nova (>= 0.3.0) - retorna dict
        result = authenticator.login(
            location='main',
            fields={
                'Form name': 'Login',
                'Username': 'Usuário',
                'Password': 'Senha',
                'Login': 'Entrar'
            }
        )
        
        # Se retornou dict, extrair valores
        if isinstance(result, dict):
            name = result.get('name')
            authentication_status = result.get('authentication_status')
            username = result.get('username')
        else:
            # Resultado é None ou tupla
            name = None
            authentication_status = None
            username = None
            
    except TypeError:
        # API antiga (< 0.3.0) - retorna tupla
        try:
            name, authentication_status, username = authenticator.login('main')
        except:
            # Última tentativa - sem parâmetros
            name, authentication_status, username = authenticator.login()
    
    # Tentar pegar do session_state se não conseguiu do retorno
    if name is None and 'name' in st.session_state:
        name = st.session_state.get('name')
        authentication_status = st.session_state.get('authentication_status')
        username = st.session_state.get('username')
    
    return name, authentication_status, username, authenticator

def verificar_autenticacao():
    """
    Verifica se usuário está autenticado
    Redireciona para login se não estiver
    
    Returns:
        tuple: (nome_usuario, username, authenticator) se autenticado, None caso contrário
    """
    
    # Exibir tela de login
    name, authentication_status, username, authenticator = exibir_tela_login()
    
    # Verificar status de autenticação
    if authentication_status == False:
        st.error('❌ Usuário ou senha incorretos')
        st.stop()
    
    elif authentication_status == None:
        st.warning('👋 Por favor, insira seu usuário e senha')
        st.info("""
        **Primeiro acesso?**
        
        Entre em contato com o administrador do sistema para obter suas credenciais.
        """)
        st.stop()
    
    # Se chegou aqui, está autenticado
    return name, username, authenticator

def exibir_info_usuario_sidebar(name, username, authenticator):
    """
    Exibe informações do usuário na sidebar com botão de logout
    ✅ CORRIGIDO: Usa st.sidebar.elemento + Botão manual com key única
    
    Args:
        name: Nome do usuário
        username: Username
        authenticator: Objeto de autenticação
    """
    
    # ✅ Separador
    st.sidebar.markdown("---")
    
    # ✅ Info do usuário (card)
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #a65e2e 0%, #d4a574 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    ">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>
        <div style="font-weight: bold; font-size: 1.1rem;">{name}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">@{username}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ✅ Botão de logout manual (sempre funciona)
    if st.sidebar.button('🚪 Sair', key=f'logout_{username}_sidebar', use_container_width=True):
        # Limpar cookies do authenticator se possível
        try:
            authenticator.cookie_manager.delete(authenticator.cookie_name)
        except:
            pass
        
        # Limpar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Forçar reload completo
        st.rerun()
    
    # ✅ Separador final
    st.sidebar.markdown("---")
    
# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def usuario_tem_permissao(username, permissao):
    """
    Verifica se usuário tem determinada permissão
    
    Args:
        username: Username do usuário
        permissao: Nome da permissão
        
    Returns:
        bool: True se tem permissão
    """
    
    # Por enquanto, todos os usuários têm todas as permissões
    # Futuramente pode implementar sistema de roles/permissões
    return True

def registrar_atividade(username, acao, detalhes=""):
    """
    Registra atividade do usuário (para auditoria futura)
    
    Args:
        username: Username do usuário
        acao: Ação realizada
        detalhes: Detalhes adicionais
    """
    
    # Implementar futuramente: salvar em tabela de auditoria no Supabase
    pass

def obter_preferencias_usuario(username):
    """
    Obtém preferências salvas do usuário
    
    Args:
        username: Username do usuário
        
    Returns:
        dict: Preferências do usuário
    """
    
    # Implementar futuramente: carregar do Supabase
    return {
        'tema': 'claro',
        'itens_por_pagina': 20,
        'notificacoes': True
    }

# ============================================
# TESTES
# ============================================

if __name__ == "__main__":
    print("🧪 Testando módulo de autenticação...")
    
    try:
        credenciais = carregar_credenciais_env()
        print(f"✅ Credenciais carregadas: {len(credenciais['usernames'])} usuário(s)")
        
        for username, dados in credenciais['usernames'].items():
            print(f"   👤 {dados['name']} (@{username}) - {dados['email']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")