# app/clean_cache.py
"""
Módulo de gerenciamento de cache do Streamlit
Funções para invalidação inteligente de cache
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Adicionar backend ao path para importar logger
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from logger import log_info, log_aviso


# =====================================
# INVALIDAÇÃO ESPECÍFICA DE CACHE
# =====================================

def invalidar_cache_candidatos():
    """
    Invalida apenas cache relacionado a candidatos
    Usar após: criar/editar/excluir candidato
    """
    try:
        # Importar funções do streamlit_app
        from streamlit_app import (
            carregar_candidatos,
            carregar_candidatos_qualificados,
            carregar_candidatos_pendentes
        )
        
        # Limpar cache das funções
        carregar_candidatos.clear()
        carregar_candidatos_qualificados.clear()
        carregar_candidatos_pendentes.clear()
        
        log_info("✅ Cache de candidatos invalidado")
        return True
        
    except Exception as e:
        log_aviso(f"⚠️ Erro ao invalidar cache de candidatos: {str(e)}")
        return False


def invalidar_cache_vagas():
    """
    Invalida apenas cache relacionado a vagas
    Usar após: criar/editar/excluir vaga, adicionar observação
    """
    try:
        # Importar funções do streamlit_app
        from streamlit_app import (
            carregar_vagas,
            carregar_dados_vagas_completo
        )
        
        # Limpar cache das funções
        carregar_vagas.clear()
        carregar_dados_vagas_completo.clear()
        
        log_info("✅ Cache de vagas invalidado")
        return True
        
    except Exception as e:
        log_aviso(f"⚠️ Erro ao invalidar cache de vagas: {str(e)}")
        return False


def invalidar_cache_relacionamentos():
    """
    Invalida cache de relacionamentos candidato-vaga
    Usar após: criar/editar/excluir relacionamento
    """
    try:
        # Importar função do streamlit_app
        from streamlit_app import carregar_relacionamentos
        
        # Limpar cache
        carregar_relacionamentos.clear()
        
        log_info("✅ Cache de relacionamentos invalidado")
        return True
        
    except Exception as e:
        log_aviso(f"⚠️ Erro ao invalidar cache de relacionamentos: {str(e)}")
        return False


def invalidar_cache_apos_relacionamento():
    """
    Invalida todos os caches relacionados após operação em relacionamento
    Usar após: criar/editar/excluir relacionamento
    
    Invalida:
    - Relacionamentos (óbvio)
    - Candidatos (status muda)
    - Vagas (status muda)
    """
    invalidar_cache_relacionamentos()
    invalidar_cache_candidatos()
    invalidar_cache_vagas()
    log_info("✅ Cache completo de relacionamentos invalidado")


def invalidar_cache_completo():
    """
    Invalida TODO o cache do Streamlit
    ⚠️ USAR APENAS EM CASOS EXTREMOS (backup, migração, etc)
    """
    st.cache_data.clear()
    log_info("🔄 Cache completo do sistema invalidado")


# =====================================
# ATALHOS PARA OPERAÇÕES COMUNS
# =====================================

def cache_apos_criar_candidato():
    """Invalida cache após criar candidato"""
    invalidar_cache_candidatos()


def cache_apos_editar_candidato():
    """Invalida cache após editar candidato"""
    invalidar_cache_candidatos()


def cache_apos_criar_vaga():
    """Invalida cache após criar vaga"""
    invalidar_cache_vagas()


def cache_apos_editar_vaga():
    """Invalida cache após editar vaga"""
    invalidar_cache_vagas()


def cache_apos_adicionar_observacao_vaga():
    """Invalida cache após adicionar observação em vaga"""
    invalidar_cache_vagas()


def cache_apos_criar_relacionamento():
    """Invalida cache após criar relacionamento"""
    invalidar_cache_apos_relacionamento()


def cache_apos_editar_relacionamento():
    """Invalida cache após editar relacionamento"""
    invalidar_cache_apos_relacionamento()


def cache_apos_excluir_relacionamento():
    """Invalida cache após excluir relacionamento"""
    invalidar_cache_apos_relacionamento()


# =====================================
# PARA OPERAÇÕES QUE NÃO PRECISAM INVALIDAR
# =====================================

def cache_apos_gerar_pdf():
    """
    NÃO invalida cache após gerar PDF
    PDF não modifica dados, apenas lê
    """
    log_info("📄 PDF gerado - cache mantido (operação de leitura)")
    pass  # Não faz nada propositalmente


def cache_apos_download():
    """
    NÃO invalida cache após download
    Download não modifica dados
    """
    log_info("⬇️ Download realizado - cache mantido (operação de leitura)")
    pass  # Não faz nada propositalmente

# =====================================
# GERENCIAMENTO DE SESSION STATE
# =====================================

def limpar_session_state_antigo():
    """
    Remove chaves antigas do session_state para evitar acúmulo
    Mantém apenas chaves essenciais
    """
    # Chaves que NUNCA devem ser removidas
    chaves_essenciais = {
        'authentication_status',
        'name',
        'username',
        'logout',
        'password',
        # Chaves de paginação (manter estado da navegação)
        'pagina_atual_candidatos',
        'pagina_atual_vagas',
        'pagina_atual_relacionamentos',
    }
    
    # Contador de limpezas (para não executar toda hora)
    if 'ultima_limpeza' not in st.session_state:
        st.session_state['ultima_limpeza'] = datetime.now()
        return
    
    # Limpar apenas a cada 5 minutos
    tempo_desde_limpeza = (datetime.now() - st.session_state['ultima_limpeza']).seconds
    if tempo_desde_limpeza < 300:  # 5 minutos
        return
    
    # Contar chaves antes
    total_antes = len(st.session_state.keys())
    
    # Remover chaves que não são essenciais e são antigas
    chaves_para_remover = []
    for chave in list(st.session_state.keys()):
        # Manter chaves essenciais
        if chave in chaves_essenciais:
            continue
        
        # Manter chaves que começam com certos prefixos (filtros ativos)
        if any(chave.startswith(prefix) for prefix in ['filtro_', 'busca_']):
            continue
        
        # Remover o resto
        chaves_para_remover.append(chave)
    
    # Executar remoção
    for chave in chaves_para_remover:
        try:
            del st.session_state[chave]
        except:
            pass
    
    # Atualizar timestamp
    st.session_state['ultima_limpeza'] = datetime.now()
    
    # Log (apenas em debug)
    total_depois = len(st.session_state.keys())
    removidas = total_antes - total_depois
    if removidas > 0:
        log_info(f"Limpeza session_state: {removidas} chaves removidas ({total_antes} → {total_depois})")
    """
    Remove chaves antigas do session_state para evitar acúmulo
    Mantém apenas chaves essenciais
    """
    # Chaves que NUNCA devem ser removidas
    chaves_essenciais = {
        'authentication_status',
        'name',
        'username',
        'logout',
        'password',
        # Chaves de paginação (manter estado da navegação)
        'pagina_atual_candidatos',
        'pagina_atual_vagas',
        'pagina_atual_relacionamentos',
    }
    
    # Contador de limpezas (para não executar toda hora)
    if 'ultima_limpeza' not in st.session_state:
        st.session_state['ultima_limpeza'] = datetime.now()
        return
    
    # Limpar apenas a cada 5 minutos
    tempo_desde_limpeza = (datetime.now() - st.session_state['ultima_limpeza']).seconds
    if tempo_desde_limpeza < 300:  # 5 minutos
        return
    
    # Contar chaves antes
    total_antes = len(st.session_state.keys())
    
    # Remover chaves que não são essenciais e são antigas
    chaves_para_remover = []
    for chave in list(st.session_state.keys()):
        # Manter chaves essenciais
        if chave in chaves_essenciais:
            continue
        
        # Manter chaves que começam com certos prefixos (filtros ativos)
        if any(chave.startswith(prefix) for prefix in ['filtro_', 'busca_']):
            continue
        
        # Remover o resto
        chaves_para_remover.append(chave)
    
    # Executar remoção
    for chave in chaves_para_remover:
        try:
            del st.session_state[chave]
        except:
            pass
    
    # Atualizar timestamp
    st.session_state['ultima_limpeza'] = datetime.now()
    
    # Log (apenas em debug)
    total_depois = len(st.session_state.keys())
    removidas = total_antes - total_depois
    if removidas > 0:
        log_info(f"Limpeza session_state: {removidas} chaves removidas ({total_antes} → {total_depois})")
    """
    NÃO invalida cache após download
    Download não modifica dados
    """
    log_info("⬇️ Download realizado - cache mantido (operação de leitura)")
    pass  # Não faz nada propositalmente