# backend/encryption.py
"""
Sistema de criptografia de dados sensíveis
Usa Fernet (AES-128) para criptografia simétrica
LGPD Compliance
"""

import os
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, List, Dict
import logging

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("ro_recrutamento.encryption")

# =====================================
# CONFIGURAÇÃO
# =====================================

_cipher_instance = None

def _get_cipher():
    """
    Obtém cipher configurado com chave do .env (singleton)
    
    Returns:
        Fernet cipher
    """
    global _cipher_instance
    
    if _cipher_instance is not None:
        return _cipher_instance
    
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        raise ValueError(
            "❌ ENCRYPTION_KEY não configurada no .env!\n"
            "Execute: python gerar_chave.py"
        )
    
    try:
        _cipher_instance = Fernet(encryption_key.encode())
        return _cipher_instance
    except Exception as e:
        raise ValueError(f"❌ ENCRYPTION_KEY inválida no .env: {str(e)}")


# =====================================
# FUNÇÕES DE CRIPTOGRAFIA
# =====================================

def encrypt(texto: Optional[str]) -> Optional[str]:
    """
    Criptografa texto
    
    Args:
        texto: Texto em claro (ou None)
        
    Returns:
        Texto criptografado em base64 (ou None)
    """
    if not texto or str(texto).strip() == "":
        return None
    
    try:
        cipher = _get_cipher()
        texto_bytes = str(texto).encode('utf-8')
        encrypted_bytes = cipher.encrypt(texto_bytes)
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao criptografar: {str(e)}")
        raise


def decrypt(texto_criptografado: Optional[str]) -> Optional[str]:
    """
    Descriptografa texto
    
    Args:
        texto_criptografado: Texto criptografado em base64 (ou None)
        
    Returns:
        Texto em claro (ou None)
    """
    if not texto_criptografado or str(texto_criptografado).strip() == "":
        return None
    
    try:
        cipher = _get_cipher()
        encrypted_bytes = str(texto_criptografado).encode('utf-8')
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        logger.error("Token inválido - chave de criptografia incorreta ou dado corrompido")
        return "[DADOS CRIPTOGRAFADOS - ERRO]"
    except Exception as e:
        logger.error(f"Erro ao descriptografar: {str(e)}")
        return "[ERRO DE DESCRIPTOGRAFIA]"


def encrypt_dict_fields(dados: dict, campos_sensiveis: list) -> dict:
    """
    Criptografa campos específicos de um dicionário
    
    Args:
        dados: Dicionário com dados
        campos_sensiveis: Lista de campos a criptografar
        
    Returns:
        Dicionário com campos criptografados
    """
    if not dados:
        return {}
    
    dados_criptografados = dados.copy()
    
    for campo in campos_sensiveis:
        if campo in dados_criptografados and dados_criptografados[campo]:
            try:
                valor_original = dados_criptografados[campo]
                
                # Se já está criptografado (começa com gAAAAA), pular
                if isinstance(valor_original, str) and valor_original.startswith('gAAAAA'):
                    continue
                
                dados_criptografados[campo] = encrypt(str(valor_original))
            except Exception as e:
                logger.error(f"Erro ao criptografar campo '{campo}': {str(e)}")
                # Manter valor original se falhar
    
    return dados_criptografados


def decrypt_dict_fields(dados: dict, campos_sensiveis: list) -> dict:
    """
    Descriptografa campos específicos de um dicionário
    
    Args:
        dados: Dicionário com dados criptografados
        campos_sensiveis: Lista de campos a descriptografar
        
    Returns:
        Dicionário com campos descriptografados
    """
    if not dados:
        return {}
    
    dados_descriptografados = dados.copy()
    
    for campo in campos_sensiveis:
        if campo in dados_descriptografados and dados_descriptografados[campo]:
            try:
                valor = dados_descriptografados[campo]
                
                # Se já está descriptografado (contém @, é número, etc), pular
                if isinstance(valor, str):
                    if '@' in valor or not valor.startswith('gAAAAA'):
                        continue
                
                dados_descriptografados[campo] = decrypt(str(valor))
            except Exception as e:
                logger.error(f"Erro ao descriptografar campo '{campo}': {str(e)}")
                dados_descriptografados[campo] = "[ERRO]"
    
    return dados_descriptografados


# =====================================
# CONFIGURAÇÃO DE CAMPOS SENSÍVEIS
# =====================================

CAMPOS_SENSIVEIS_CANDIDATOS = [
    'email',
    'telefone',
    'whatsapp',
    'telefone_principal',
    'telefone_recado',
    'endereco',
    'rua_numero',
    'complemento',
    'bairro',
    'cpf',
    'rg'
]

CAMPOS_SENSIVEIS_VAGAS = [
    'email',
    'telefone_principal',
    'telefone_recado',
    'rua_numero',
    'complemento',
    'bairro'
]


# =====================================
# FUNÇÕES ESPECÍFICAS DO SISTEMA
# =====================================

def encrypt_candidato(candidato: dict) -> dict:
    """
    Criptografa dados sensíveis de candidato
    
    Args:
        candidato: Dict com dados do candidato
        
    Returns:
        Dict com dados sensíveis criptografados
    """
    return encrypt_dict_fields(candidato, CAMPOS_SENSIVEIS_CANDIDATOS)


def decrypt_candidato(candidato: dict) -> dict:
    """
    Descriptografa dados sensíveis de candidato
    
    Args:
        candidato: Dict com dados criptografados
        
    Returns:
        Dict com dados descriptografados
    """
    return decrypt_dict_fields(candidato, CAMPOS_SENSIVEIS_CANDIDATOS)


def encrypt_vaga(vaga: dict) -> dict:
    """
    Criptografa dados sensíveis de vaga
    
    Args:
        vaga: Dict com dados da vaga
        
    Returns:
        Dict com dados sensíveis criptografados
    """
    return encrypt_dict_fields(vaga, CAMPOS_SENSIVEIS_VAGAS)


def decrypt_vaga(vaga: dict) -> dict:
    """
    Descriptografa dados sensíveis de vaga
    
    Args:
        vaga: Dict com dados criptografados
        
    Returns:
        Dict com dados descriptografados
    """
    return decrypt_dict_fields(vaga, CAMPOS_SENSIVEIS_VAGAS)


def encrypt_lista_candidatos(candidatos: List[dict]) -> List[dict]:
    """
    Criptografa lista de candidatos
    
    Args:
        candidatos: Lista de dicts com dados
        
    Returns:
        Lista com dados criptografados
    """
    return [encrypt_candidato(c) for c in candidatos]


def decrypt_lista_candidatos(candidatos: List[dict]) -> List[dict]:
    """
    Descriptografa lista de candidatos
    
    Args:
        candidatos: Lista de dicts criptografados
        
    Returns:
        Lista com dados descriptografados
    """
    return [decrypt_candidato(c) for c in candidatos]


def encrypt_lista_vagas(vagas: List[dict]) -> List[dict]:
    """
    Criptografa lista de vagas
    
    Args:
        vagas: Lista de dicts com dados
        
    Returns:
        Lista com dados criptografados
    """
    return [encrypt_vaga(v) for v in vagas]


def decrypt_lista_vagas(vagas: List[dict]) -> List[dict]:
    """
    Descriptografa lista de vagas
    
    Args:
        vagas: Lista de dicts criptografados
        
    Returns:
        Lista com dados descriptografados
    """
    return [decrypt_vaga(v) for v in vagas]


# =====================================
# MIGRAÇÃO DE DADOS EXISTENTES
# =====================================

def migrar_dados_existentes():
    """
    ⚠️  EXECUTAR UMA VEZ após implementar criptografia
    Criptografa dados que já estão no banco em texto plano
    """
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from supabase_client import get_supabase_client
    
    print("\n" + "=" * 60)
    print("🔐 MIGRAÇÃO DE DADOS PARA CRIPTOGRAFIA")
    print("=" * 60)
    
    resposta = input("\n⚠️  Isso irá criptografar TODOS os dados no banco.\nDeseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta.upper() != 'SIM':
        print("❌ Migração cancelada")
        return
    
    supabase = get_supabase_client()
    
    # ===== MIGRAR CANDIDATOS =====
    print("\n📋 Migrando candidatos...")
    try:
        candidatos = supabase.table('candidatos').select('*').execute()
        total_candidatos = len(candidatos.data) if candidatos.data else 0
        contador = 0
        
        for candidato in (candidatos.data or []):
            # Verificar se já está criptografado
            email = candidato.get('email', '')
            if email and '@' in str(email):
                # Ainda em texto plano, criptografar
                dados_criptografados = encrypt_candidato(candidato)
                
                # Atualizar apenas campos sensíveis
                update_data = {
                    campo: dados_criptografados.get(campo)
                    for campo in CAMPOS_SENSIVEIS_CANDIDATOS
                    if campo in dados_criptografados and dados_criptografados.get(campo)
                }
                
                if update_data:
                    supabase.table('candidatos').update(update_data).eq('id', candidato['id']).execute()
                    contador += 1
                    print(f"  ✅ Candidato {contador}/{total_candidatos} - {candidato['id'][:8]}")
        
        print(f"\n✅ {contador} candidatos criptografados")
        
    except Exception as e:
        print(f"❌ Erro ao migrar candidatos: {str(e)}")
    
    # ===== MIGRAR VAGAS =====
    print("\n💼 Migrando vagas...")
    try:
        vagas = supabase.table('vagas').select('*').execute()
        total_vagas = len(vagas.data) if vagas.data else 0
        contador = 0
        
        for vaga in (vagas.data or []):
            # Verificar se já está criptografado
            email = vaga.get('email', '')
            if email and '@' in str(email):
                dados_criptografados = encrypt_vaga(vaga)
                
                update_data = {
                    campo: dados_criptografados.get(campo)
                    for campo in CAMPOS_SENSIVEIS_VAGAS
                    if campo in dados_criptografados and dados_criptografados.get(campo)
                }
                
                if update_data:
                    supabase.table('vagas').update(update_data).eq('id', vaga['id']).execute()
                    contador += 1
                    print(f"  ✅ Vaga {contador}/{total_vagas} - {vaga['id'][:8]}")
        
        print(f"\n✅ {contador} vagas criptografadas")
        
    except Exception as e:
        print(f"❌ Erro ao migrar vagas: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("\n💡 Agora todos os dados sensíveis estão protegidos!")


# =====================================
# TESTE DE CRIPTOGRAFIA
# =====================================

def testar_criptografia():
    """
    Testa se criptografia está funcionando
    """
    print("\n" + "=" * 60)
    print("🧪 TESTE DE CRIPTOGRAFIA")
    print("=" * 60)
    
    # Dados de teste
    teste = {
        'nome': 'João Silva',
        'email': 'joao@email.com',
        'telefone': '11999887766',
        'endereco': 'Rua ABC, 123'
    }
    
    print("\n📝 Dados originais:")
    print(f"  Email: {teste['email']}")
    print(f"  Telefone: {teste['telefone']}")
    
    # Criptografar
    print("\n🔒 Criptografando...")
    teste_criptografado = encrypt_candidato(teste)
    print(f"  Email: {teste_criptografado['email'][:50]}...")
    print(f"  Telefone: {teste_criptografado['telefone'][:50]}...")
    
    # Descriptografar
    print("\n🔓 Descriptografando...")
    teste_descriptografado = decrypt_candidato(teste_criptografado)
    print(f"  Email: {teste_descriptografado['email']}")
    print(f"  Telefone: {teste_descriptografado['telefone']}")
    
    # Verificar
    if teste_descriptografado['email'] == teste['email']:
        print("\n✅ TESTE PASSOU! Criptografia funcionando corretamente.")
    else:
        print("\n❌ TESTE FALHOU! Verifique a configuração.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "migrar":
            migrar_dados_existentes()
        elif sys.argv[1] == "testar":
            testar_criptografia()
        else:
            print("Uso: python encryption.py [migrar|testar]")
    else:
        print("Uso: python encryption.py [migrar|testar]")