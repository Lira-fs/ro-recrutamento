# backend/supabase_client.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_client() -> Client:
    """
    Conecta no Supabase usando as credenciais do arquivo .env
    
    Returns:
        Client: Cliente Supabase conectado
        
    Raises:
        RuntimeError: Se as credenciais não estiverem configuradas
    """
    
    # Buscar credenciais do .env
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    # Verificar se credenciais existem
    if not url or not key:
        raise RuntimeError(
            "❌ ERRO: Credenciais do Supabase não encontradas!\n"
            "Certifique-se que o arquivo .env existe e contém:\n"
            "SUPABASE_URL=sua_url\n"
            "SUPABASE_KEY=sua_chave"
        )
    
    try:
        # Criar e retornar cliente
        supabase = create_client(url, key)
        print("✅ Conectado ao Supabase com sucesso!")
        return supabase
        
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao conectar no Supabase: {str(e)}")

def test_connection():
    """
    Testa a conexão com o banco de dados
    """
    try:
        supabase = get_supabase_client()
        
        # Testar consulta simples na tabela candidatos
        response = supabase.table('candidatos').select('id').limit(1).execute()
        
        print(f"✅ Teste de conexão OK! Encontrado {len(response.data)} registro(s)")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de conexão: {str(e)}")
        return False

# Testar ao executar diretamente
if __name__ == "__main__":
    print("🔌 Testando conexão com Supabase...")
    test_connection()