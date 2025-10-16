# app/lazy_loading_helpers.py
"""
Funções auxiliares para lazy loading em expanders
Versão SIMPLES e PRÁTICA para implementação rápida
"""

import streamlit as st
from typing import Callable, Any


# =====================================
# VERSÃO 1: LAZY LOADING COM SESSION_STATE
# (Mais controle, mas mais complexo)
# =====================================

def expander_com_lazy_loading(
    titulo: str,
    chave_unica: str,
    funcao_carregar: Callable,
    expanded: bool = False
):
    """
    Cria expander com lazy loading usando session_state
    
    Args:
        titulo: Título do expander
        chave_unica: Key única para controlar estado
        funcao_carregar: Função que retorna o conteúdo a ser renderizado
        expanded: Se expander inicia expandido
    
    Exemplo:
        def _carregar_observacoes():
            obs = carregar_observacoes_vaga(vaga_id)
            for o in obs:
                st.write(o['observacao'])
        
        expander_com_lazy_loading(
            "📚 Histórico",
            f"obs_{vaga_id}_{idx}",
            _carregar_observacoes
        )
    """
    key_loaded = f"lazy_loaded_{chave_unica}"
    
    # Inicializar estado
    if key_loaded not in st.session_state:
        st.session_state[key_loaded] = False
    
    with st.expander(titulo, expanded=expanded):
        # Primeira vez: placeholder
        if not st.session_state[key_loaded]:
            st.info("💡 Expandir para carregar conteúdo...")
            st.session_state[key_loaded] = True
        else:
            # Já foi aberto: executar função de carregamento
            funcao_carregar()


# =====================================
# VERSÃO 2: LAZY LOADING SIMPLES
# (Recomendada para lançamento rápido)
# =====================================

def expander_lazy_simples(titulo: str, funcao_conteudo: Callable, expanded: bool = False):
    """
    Versão ULTRA SIMPLES de lazy loading
    Usa apenas st.container() sem session_state
    
    Args:
        titulo: Título do expander
        funcao_conteudo: Função que renderiza o conteúdo
        expanded: Se expander inicia expandido
    
    Exemplo:
        def _renderizar_obs():
            obs = carregar_observacoes_vaga(vaga_id)
            for o in obs:
                st.write(o['observacao'])
        
        expander_lazy_simples("📚 Histórico", _renderizar_obs)
    """
    with st.expander(titulo, expanded=expanded):
        # Container lazy - Streamlit só renderiza quando expander abre
        with st.container():
            funcao_conteudo()


# =====================================
# VERSÃO 3: WRAPPER COM CACHE
# (Para queries pesadas ao banco)
# =====================================

def criar_funcao_cached(funcao_original: Callable, ttl: int = 300):
    """
    Cria versão cached de uma função para usar em lazy loading
    
    Args:
        funcao_original: Função original
        ttl: Tempo de cache em segundos
    
    Returns:
        Função com cache aplicado
    
    Exemplo:
        # Criar versão cached
        carregar_obs_cached = criar_funcao_cached(carregar_observacoes_vaga)
        
        # Usar em expander
        with st.expander("Histórico"):
            with st.container():
                obs = carregar_obs_cached(vaga_id)  # ✅ Lazy + cached
    """
    return st.cache_data(ttl=ttl)(funcao_original)