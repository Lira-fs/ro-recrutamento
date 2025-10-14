# backend/validators.py
"""
Módulo de validação server-side
Garante integridade dos dados antes de operações no banco
"""

import re
from typing import Tuple, Optional, Any
from supabase_client import get_supabase_client

# =====================================
# VALIDADORES GENÉRICOS
# =====================================

def validar_uuid(valor: str, nome_campo: str = "ID") -> Tuple[bool, str]:
    """
    Valida se string é UUID válido
    
    Args:
        valor: String a validar
        nome_campo: Nome do campo para mensagem de erro
        
    Returns:
        (sucesso, mensagem)
    """
    if not valor or not isinstance(valor, str):
        return False, f"{nome_campo} inválido"
    
    # Regex UUID v4
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    if not re.match(uuid_pattern, valor, re.IGNORECASE):
        return False, f"{nome_campo} não é um UUID válido"
    
    return True, "OK"


def validar_texto(valor: str, min_len: int = 1, max_len: int = 5000, 
                  nome_campo: str = "Texto") -> Tuple[bool, str]:
    """
    Valida campo de texto
    
    Args:
        valor: Texto a validar
        min_len: Tamanho mínimo
        max_len: Tamanho máximo
        nome_campo: Nome do campo
        
    Returns:
        (sucesso, mensagem)
    """
    if valor is None:
        if min_len > 0:
            return False, f"{nome_campo} é obrigatório"
        return True, "OK"
    
    if not isinstance(valor, str):
        return False, f"{nome_campo} deve ser texto"
    
    texto_limpo = valor.strip()
    
    if len(texto_limpo) < min_len:
        return False, f"{nome_campo} muito curto (mín: {min_len})"
    
    if len(texto_limpo) > max_len:
        return False, f"{nome_campo} muito longo (máx: {max_len})"
    
    return True, "OK"


def sanitizar_texto(texto: str, max_len: int = 5000) -> str:
    """
    Remove caracteres perigosos de texto
    
    Args:
        texto: Texto a sanitizar
        max_len: Tamanho máximo
        
    Returns:
        Texto limpo
    """
    if not texto:
        return ""
    
    # Remover tags HTML/XML
    texto_limpo = re.sub(r'<[^>]+>', '', str(texto))
    
    # Remover SQL injection patterns
    texto_limpo = re.sub(r"[';\"\\]", '', texto_limpo)
    
    # Truncar
    texto_limpo = texto_limpo[:max_len]
    
    return texto_limpo.strip()


def validar_enum(valor: str, valores_permitidos: list, 
                 nome_campo: str = "Campo") -> Tuple[bool, str]:
    """
    Valida se valor está em lista permitida
    
    Args:
        valor: Valor a validar
        valores_permitidos: Lista de valores aceitos
        nome_campo: Nome do campo
        
    Returns:
        (sucesso, mensagem)
    """
    if valor not in valores_permitidos:
        return False, f"{nome_campo} inválido. Valores aceitos: {', '.join(valores_permitidos)}"
    
    return True, "OK"


# =====================================
# VALIDADORES DE EXISTÊNCIA
# =====================================

def validar_candidato_existe(candidato_id: str) -> Tuple[bool, str]:
    """
    Valida se candidato existe no banco
    
    Args:
        candidato_id: UUID do candidato
        
    Returns:
        (sucesso, mensagem)
    """
    # Validar formato UUID primeiro
    sucesso, msg = validar_uuid(candidato_id, "Candidato ID")
    if not sucesso:
        return False, msg
    
    try:
        supabase = get_supabase_client()
        resultado = supabase.table('candidatos').select('id').eq('id', candidato_id).execute()
        
        if not resultado.data:
            return False, "Candidato não encontrado no sistema"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Erro ao validar candidato: {str(e)}"


def validar_vaga_existe(vaga_id: str) -> Tuple[bool, str]:
    """
    Valida se vaga existe no banco
    
    Args:
        vaga_id: UUID da vaga
        
    Returns:
        (sucesso, mensagem)
    """
    # Validar formato UUID primeiro
    sucesso, msg = validar_uuid(vaga_id, "Vaga ID")
    if not sucesso:
        return False, msg
    
    try:
        supabase = get_supabase_client()
        resultado = supabase.table('vagas').select('id').eq('id', vaga_id).execute()
        
        if not resultado.data:
            return False, "Vaga não encontrada no sistema"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Erro ao validar vaga: {str(e)}"


# =====================================
# VALIDADORES DE REGRAS DE NEGÓCIO
# =====================================

def validar_relacionamento_candidato_vaga(
    candidato_id: str,
    vaga_id: str,
    status_processo: str,
    observacao: Optional[str] = None
) -> Tuple[bool, str, dict]:
    """
    Valida COMPLETA de relacionamento candidato-vaga
    
    Args:
        candidato_id: UUID do candidato
        vaga_id: UUID da vaga
        status_processo: Status inicial
        observacao: Observação opcional
        
    Returns:
        (sucesso, mensagem, dados_validados)
    """
    # 1. VALIDAR CANDIDATO
    sucesso, msg = validar_candidato_existe(candidato_id)
    if not sucesso:
        return False, msg, {}
    
    # 2. VALIDAR VAGA
    sucesso, msg = validar_vaga_existe(vaga_id)
    if not sucesso:
        return False, msg, {}
    
    # 3. VALIDAR STATUS
    status_permitidos = [
        'enviado', 'em_analise', 'entrevista_agendada', 
        'aprovado', 'rejeitado', 'contratado', 'cancelado'
    ]
    sucesso, msg = validar_enum(status_processo, status_permitidos, "Status")
    if not sucesso:
        return False, msg, {}
    
    # 4. VALIDAR OBSERVAÇÃO (se fornecida)
    observacao_limpa = ""
    if observacao:
        sucesso, msg = validar_texto(observacao, min_len=0, max_len=5000, nome_campo="Observação")
        if not sucesso:
            return False, msg, {}
        observacao_limpa = sanitizar_texto(observacao)
    
    # 5. VALIDAR SE JÁ EXISTE RELACIONAMENTO
    try:
        supabase = get_supabase_client()
        existe = supabase.table('candidatos_vagas').select('id').eq('candidato_id', candidato_id).eq('vaga_id', vaga_id).execute()
        
        if existe.data:
            return False, "Relacionamento já existe entre este candidato e vaga", {}
    except Exception as e:
        return False, f"Erro ao verificar relacionamento: {str(e)}", {}
    
    # 6. VALIDAR LIMITE DE CANDIDATOS POR VAGA (máx 5)
    try:
        ativos = supabase.table('candidatos_vagas').select('id', count='exact').eq('vaga_id', vaga_id).not_.in_('status_processo', ['finalizado', 'expirado', 'rejeitado', 'cancelado']).execute()
        
        if ativos.count >= 5:
            return False, f"Vaga já possui o máximo de 5 candidatos ativos (atual: {ativos.count})", {}
    except Exception as e:
        return False, f"Erro ao validar limite: {str(e)}", {}
    
    # ✅ TUDO VÁLIDO - Retornar dados limpos
    dados_validados = {
        'candidato_id': candidato_id,
        'vaga_id': vaga_id,
        'status_processo': status_processo,
        'observacoes': observacao_limpa
    }
    
    return True, "Validação OK", dados_validados


def validar_atualizacao_status_vaga(vaga_id: str, novo_status: str) -> Tuple[bool, str]:
    """
    Valida atualização de status de vaga
    
    Args:
        vaga_id: UUID da vaga
        novo_status: Novo status
        
    Returns:
        (sucesso, mensagem)
    """
    # 1. VALIDAR VAGA
    sucesso, msg = validar_vaga_existe(vaga_id)
    if not sucesso:
        return False, msg
    
    # 2. VALIDAR STATUS
    status_permitidos = ['ativa', 'em_andamento', 'preenchida', 'pausada', 'cancelada']
    sucesso, msg = validar_enum(novo_status, status_permitidos, "Status da vaga")
    if not sucesso:
        return False, msg
    
    return True, "OK"


def validar_observacao_vaga(vaga_id: str, observacao: str) -> Tuple[bool, str, str]:
    """
    Valida adição de observação em vaga
    
    Args:
        vaga_id: UUID da vaga
        observacao: Texto da observação
        
    Returns:
        (sucesso, mensagem, observacao_limpa)
    """
    # 1. VALIDAR VAGA
    sucesso, msg = validar_vaga_existe(vaga_id)
    if not sucesso:
        return False, msg, ""
    
    # 2. VALIDAR OBSERVAÇÃO
    sucesso, msg = validar_texto(observacao, min_len=1, max_len=2000, nome_campo="Observação")
    if not sucesso:
        return False, msg, ""
    
    # 3. SANITIZAR
    observacao_limpa = sanitizar_texto(observacao, max_len=2000)
    
    return True, "OK", observacao_limpa

# =====================================
# SANITIZADORES ESPECIALIZADOS
# =====================================

def sanitizar_filtro_busca(texto: str) -> str:
    """
    Sanitiza input de campos de busca/filtro
    Remove caracteres SQL perigosos
    
    Args:
        texto: Texto de busca do usuário
        
    Returns:
        Texto limpo e seguro
    """
    if not texto:
        return ""
    
    texto = str(texto).strip()
    
    # Remover caracteres SQL perigosos
    caracteres_perigosos = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 
                           'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'SCRIPT']
    
    texto_lower = texto.lower()
    for perigo in caracteres_perigosos:
        if perigo.lower() in texto_lower:
            # Remover completamente strings perigosas
            texto = re.sub(re.escape(perigo), '', texto, flags=re.IGNORECASE)
    
    # Remover aspas e backslashes
    texto = texto.replace("'", "").replace('"', "").replace("\\", "")
    
    # Limitar tamanho
    texto = texto[:200]
    
    return texto.strip()


def sanitizar_email(email: str) -> Tuple[bool, str]:
    """
    Valida e sanitiza email
    
    Args:
        email: Email a validar
        
    Returns:
        (é_valido, email_limpo)
    """
    if not email:
        return False, ""
    
    email = str(email).strip().lower()
    
    # Regex simples de email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, ""
    
    # Limitar tamanho
    email = email[:100]
    
    return True, email


def sanitizar_telefone(telefone: str) -> str:
    """
    Sanitiza telefone (mantém apenas números)
    
    Args:
        telefone: Telefone a limpar
        
    Returns:
        Apenas dígitos
    """
    if not telefone:
        return ""
    
    # Manter apenas números
    apenas_numeros = re.sub(r'\D', '', str(telefone))
    
    # Validar tamanho (Brasil: 10-11 dígitos)
    if len(apenas_numeros) < 10 or len(apenas_numeros) > 11:
        return ""
    
    return apenas_numeros


def sanitizar_nome(nome: str) -> str:
    """
    Sanitiza nome de pessoa
    Remove números e caracteres especiais
    
    Args:
        nome: Nome a limpar
        
    Returns:
        Nome sanitizado
    """
    if not nome:
        return ""
    
    nome = str(nome).strip()
    
    # Permitir apenas letras, espaços, acentos e hífens
    nome = re.sub(r'[^a-zA-ZÀ-ÿ\s\-]', '', nome)
    
    # Remover espaços múltiplos
    nome = re.sub(r'\s+', ' ', nome)
    
    # Limitar tamanho
    nome = nome[:100]
    
    return nome.strip()


def sanitizar_observacao(obs: str) -> str:
    """
    Sanitiza observações/comentários
    Mais permissivo que outros, mas remove scripts
    
    Args:
        obs: Observação a limpar
        
    Returns:
        Observação sanitizada
    """
    if not obs:
        return ""
    
    obs = str(obs).strip()
    
    # Remover tags HTML/JS
    obs = re.sub(r'<script[^>]*>.*?</script>', '', obs, flags=re.IGNORECASE | re.DOTALL)
    obs = re.sub(r'<[^>]+>', '', obs)
    
    # Remover URLs suspeitas (javascript:, data:)
    obs = re.sub(r'(javascript|data|vbscript):', '', obs, flags=re.IGNORECASE)
    
    # Remover SQL injection patterns comuns
    obs = re.sub(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b)", '', obs, flags=re.IGNORECASE)
    
    # Limitar tamanho
    obs = obs[:5000]
    
    return obs.strip()


def sanitizar_dict_filtros(filtros: dict) -> dict:
    """
    Sanitiza dicionário completo de filtros
    
    Args:
        filtros: Dict com filtros do usuário
        
    Returns:
        Dict com valores sanitizados
    """
    if not filtros or not isinstance(filtros, dict):
        return {}
    
    filtros_limpos = {}
    
    for chave, valor in filtros.items():
        # Chave também precisa ser segura
        chave_limpa = sanitizar_filtro_busca(str(chave))
        
        if isinstance(valor, str):
            # Sanitizar string
            valor_limpo = sanitizar_filtro_busca(valor)
        elif isinstance(valor, (int, float)):
            # Números são seguros
            valor_limpo = valor
        elif isinstance(valor, bool):
            # Booleanos são seguros
            valor_limpo = valor
        elif isinstance(valor, list):
            # Sanitizar lista
            valor_limpo = [sanitizar_filtro_busca(str(v)) for v in valor if v]
        else:
            # Outros tipos: converter para string e sanitizar
            valor_limpo = sanitizar_filtro_busca(str(valor))
        
        filtros_limpos[chave_limpa] = valor_limpo
    
    return filtros_limpos


def validar_e_sanitizar_filtros_query(filtros: dict) -> Tuple[bool, dict, str]:
    """
    Validação completa de filtros para queries
    
    Args:
        filtros: Filtros originais
        
    Returns:
        (válido, filtros_limpos, mensagem_erro)
    """
    if not filtros:
        return True, {}, "OK"
    
    # Sanitizar
    filtros_limpos = sanitizar_dict_filtros(filtros)
    
    # Validar campos permitidos
    campos_permitidos = [
        'funcao', 'cidade', 'status', 'busca', 
        'status_detalhado', 'urgencia', 'salario_min', 'salario_max',
        'dias_recentes', 'formulario_id', 'nome', 'email'
    ]
    
    for chave in filtros_limpos.keys():
        if chave not in campos_permitidos:
            return False, {}, f"Campo de filtro não permitido: {chave}"
    
    return True, filtros_limpos, "OK"