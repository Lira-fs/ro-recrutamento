# backend/logger.py
"""
Sistema de logging estruturado
Grava erros técnicos em arquivo, exibe mensagens amigáveis para usuários
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import streamlit as st

# =====================================
# CONFIGURAÇÃO DO LOGGER
# =====================================

# Criar pasta de logs se não existir
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Nome do arquivo de log (rotaciona diariamente)
LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# Configurar logger
logger = logging.getLogger("ro_recrutamento")
logger.setLevel(logging.DEBUG)

# Handler para arquivo (grava tudo)
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Formato detalhado para arquivo
file_format = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_format)

# Handler para console (apenas INFO+)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)

# Adicionar handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# =====================================
# MODO DEBUG
# =====================================

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


# =====================================
# FUNÇÕES DE LOGGING
# =====================================

def log_erro(mensagem_usuario: str, excecao: Exception, contexto: dict = None):
    """
    Registra erro com detalhes técnicos no arquivo
    Exibe mensagem amigável para usuário
    
    Args:
        mensagem_usuario: Mensagem exibida na interface
        excecao: Exception capturada
        contexto: Dict com informações adicionais
    """
    import traceback
    
    # Construir mensagem técnica para arquivo
    contexto_str = ""
    if contexto:
        contexto_str = " | ".join([f"{k}={v}" for k, v in contexto.items()])
    
    # Gravar no arquivo com stack trace completo
    logger.error(
        f"{mensagem_usuario} | Contexto: {contexto_str} | "
        f"Exceção: {type(excecao).__name__}: {str(excecao)} | "
        f"Traceback: {traceback.format_exc()}"
    )
    
    # Exibir para usuário
    if DEBUG_MODE:
        # Modo desenvolvimento: mostrar detalhes
        st.error(f"❌ {mensagem_usuario}")
        with st.expander("🔍 Detalhes Técnicos (DEBUG MODE)"):
            st.code(traceback.format_exc())
    else:
        # Modo produção: mensagem genérica
        st.error(f"❌ {mensagem_usuario}")
        st.info("💡 Se o problema persistir, contate o administrador.")


def log_aviso(mensagem: str, contexto: dict = None):
    """
    Registra aviso
    
    Args:
        mensagem: Mensagem de aviso
        contexto: Dict com informações adicionais
    """
    contexto_str = ""
    if contexto:
        contexto_str = " | ".join([f"{k}={v}" for k, v in contexto.items()])
    
    logger.warning(f"{mensagem} | Contexto: {contexto_str}")


def log_info(mensagem: str, contexto: dict = None):
    """
    Registra informação
    
    Args:
        mensagem: Mensagem informativa
        contexto: Dict com informações adicionais
    """
    contexto_str = ""
    if contexto:
        contexto_str = " | ".join([f"{k}={v}" for k, v in contexto.items()])
    
    logger.info(f"{mensagem} | Contexto: {contexto_str}")


def log_sucesso(acao: str, usuario: str = "Sistema", detalhes: dict = None):
    """
    Registra ação bem-sucedida (auditoria)
    
    Args:
        acao: Ação realizada
        usuario: Quem realizou
        detalhes: Detalhes adicionais
    """
    detalhes_str = ""
    if detalhes:
        detalhes_str = " | ".join([f"{k}={v}" for k, v in detalhes.items()])
    
    logger.info(f"SUCESSO: {acao} | Usuário: {usuario} | Detalhes: {detalhes_str}")


def log_auditoria(acao: str, usuario: str, dados: dict):
    """
    Registra ação crítica para auditoria
    
    Args:
        acao: Tipo de ação (criar_relacionamento, atualizar_status, etc)
        usuario: Username
        dados: Dados da operação
    """
    import json
    
    logger.info(
        f"AUDITORIA: {acao} | "
        f"Usuário: {usuario} | "
        f"Timestamp: {datetime.now().isoformat()} | "
        f"Dados: {json.dumps(dados, ensure_ascii=False)}"
    )


# =====================================
# DECORADOR PARA TRATAMENTO AUTOMÁTICO
# =====================================

def tratar_erros(mensagem_usuario: str = "Erro ao processar operação"):
    """
    Decorador para tratamento automático de erros
    
    Usage:
        @tratar_erros("Erro ao carregar candidatos")
        def carregar_candidatos():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_erro(
                    mensagem_usuario=mensagem_usuario,
                    excecao=e,
                    contexto={
                        'funcao': func.__name__,
                        'args': str(args)[:100],
                        'kwargs': str(kwargs)[:100]
                    }
                )
                return None
        return wrapper
    return decorator