#!/usr/bin/env python3
"""
Gerador de Senhas Hash para Autenticação - VERSÃO COMPATÍVEL
R.O Recrutamento
Funciona com qualquer versão do streamlit-authenticator
"""

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def gerar_hash_bcrypt(senha):
    """
    Gera hash bcrypt diretamente usando bcrypt
    Mais confiável que depender da API do streamlit-authenticator
    """
    try:
        import bcrypt
        # Gerar salt e hash
        salt = bcrypt.gensalt()
        hash_bytes = bcrypt.hashpw(senha.encode('utf-8'), salt)
        return hash_bytes.decode('utf-8')
    except ImportError:
        print("❌ Biblioteca bcrypt não instalada!")
        print("Execute: pip install bcrypt")
        return None

def tentar_streamlit_auth(senha):
    """
    Tenta usar streamlit-authenticator
    """
    try:
        import streamlit_authenticator as stauth
        
        # Tentar método novo (>= 0.3.0)
        try:
            hasher = stauth.Hasher()
            return hasher.hash(senha)
        except:
            pass
        
        # Tentar método antigo (< 0.3.0)
        try:
            return stauth.Hasher([senha]).generate()[0]
        except:
            pass
        
        # Se chegou aqui, usar bcrypt direto
        return None
        
    except ImportError:
        return None

def gerar_hash_senha():
    """Gera hash de senha para uso no sistema"""
    
    print_header("🔐 GERADOR DE SENHAS HASH - V2")
    
    print("Este script irá gerar hashes seguros para suas senhas.")
    print("NUNCA armazene senhas em texto puro!\n")
    
    # Verificar bibliotecas disponíveis
    print("🔍 Verificando bibliotecas disponíveis...")
    
    metodo = None
    try:
        import streamlit_authenticator as stauth
        print("✅ streamlit-authenticator encontrado")
        metodo = "stauth"
    except ImportError:
        print("⚠️  streamlit-authenticator não encontrado")
    
    try:
        import bcrypt
        print("✅ bcrypt encontrado")
        if metodo is None:
            metodo = "bcrypt"
    except ImportError:
        print("⚠️  bcrypt não encontrado")
    
    if metodo is None:
        print("\n❌ ERRO: Nenhuma biblioteca de hash encontrada!")
        print("\nInstale uma delas:")
        print("  pip install streamlit-authenticator")
        print("  pip install bcrypt")
        return
    
    print(f"\n✅ Usando método: {metodo}\n")
    
    # Lista de usuários
    usuarios = []
    
    # Usuário 1
    print("👤 USUÁRIO 1:")
    nome1 = input("Nome completo: ").strip()
    username1 = input("Username (login): ").strip()
    email1 = input("Email: ").strip()
    senha1 = input("Senha: ").strip()
    
    if not senha1:
        print("❌ Senha não pode ser vazia!")
        return
    
    usuarios.append({
        'nome': nome1,
        'username': username1,
        'email': email1,
        'senha': senha1
    })
    
    print("\n" + "-"*60 + "\n")
    
    # Usuário 2
    print("👤 USUÁRIO 2:")
    nome2 = input("Nome completo: ").strip()
    username2 = input("Username (login): ").strip()
    email2 = input("Email: ").strip()
    senha2 = input("Senha: ").strip()
    
    if not senha2:
        print("❌ Senha não pode ser vazia!")
        return
    
    usuarios.append({
        'nome': nome2,
        'username': username2,
        'email': email2,
        'senha': senha2
    })
    
    print_header("🔒 GERANDO HASHES")
    
    print("⏳ Processando...\n")
    
    # Gerar hashes
    hashes = []
    
    for usuario in usuarios:
        senha_hash = None
        
        # Tentar streamlit-authenticator primeiro
        if metodo == "stauth":
            senha_hash = tentar_streamlit_auth(usuario['senha'])
        
        # Se não funcionou, usar bcrypt direto
        if senha_hash is None:
            senha_hash = gerar_hash_bcrypt(usuario['senha'])
        
        if senha_hash is None:
            print(f"❌ Erro ao gerar hash para {usuario['nome']}")
            return
        
        hashes.append(senha_hash)
        print(f"✅ Hash gerado para {usuario['nome']}")
    
    print_header("📋 RESULTADO")
    
    for i, usuario in enumerate(usuarios):
        print(f"👤 {usuario['nome']} (@{usuario['username']})")
        print(f"   Email: {usuario['email']}")
        print(f"   Hash: {hashes[i]}")
        print()
    
    print_header("📝 COPIE PARA O ARQUIVO .env")
    
    print("Adicione estas linhas no FINAL do seu arquivo .env:\n")
    print("# ===== AUTENTICAÇÃO =====")
    
    for i, usuario in enumerate(usuarios):
        num = i + 1
        print(f"AUTH_USER{num}_NAME={usuario['nome']}")
        print(f"AUTH_USER{num}_USERNAME={usuario['username']}")
        print(f"AUTH_USER{num}_EMAIL={usuario['email']}")
        print(f"AUTH_USER{num}_PASSWORD_HASH={hashes[i]}")
        print()
    
    print("# Cookie settings")
    print("AUTH_COOKIE_NAME=ro_recrutamento_auth")
    
    # Gerar chave aleatória
    import secrets
    chave_aleatoria = secrets.token_urlsafe(32)
    print(f"AUTH_COOKIE_KEY={chave_aleatoria}")
    
    print("AUTH_COOKIE_EXPIRY_DAYS=30")
    
    print("\n" + "="*60)
    print("✅ AUTH_COOKIE_KEY foi gerada automaticamente!")
    print("   Ela já está pronta para uso e é única.")
    print("="*60 + "\n")
    
    print_header("✅ CONCLUÍDO")
    
    print("📋 Próximos passos:")
    print("1. ✅ Copie TODAS as linhas acima")
    print("2. ✅ Cole no FINAL do arquivo .env")
    print("3. ✅ Salve o arquivo .env")
    print("4. ✅ Execute: streamlit run app/streamlit_app.py")
    print("5. ✅ Faça login com:")
    print(f"      Usuário 1: {usuarios[0]['username']}")
    print(f"      Usuário 2: {usuarios[1]['username']}")
    print()
    
    # Salvar em arquivo temporário também
    try:
        with open('credenciais_geradas.txt', 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("CREDENCIAIS GERADAS - R.O RECRUTAMENTO\n")
            f.write("="*60 + "\n\n")
            
            f.write("# ===== AUTENTICAÇÃO =====\n")
            for i, usuario in enumerate(usuarios):
                num = i + 1
                f.write(f"AUTH_USER{num}_NAME={usuario['nome']}\n")
                f.write(f"AUTH_USER{num}_USERNAME={usuario['username']}\n")
                f.write(f"AUTH_USER{num}_EMAIL={usuario['email']}\n")
                f.write(f"AUTH_USER{num}_PASSWORD_HASH={hashes[i]}\n")
                f.write("\n")
            
            f.write("# Cookie settings\n")
            f.write("AUTH_COOKIE_NAME=ro_recrutamento_auth\n")
            f.write(f"AUTH_COOKIE_KEY={chave_aleatoria}\n")
            f.write("AUTH_COOKIE_EXPIRY_DAYS=30\n")
        
        print("💾 Credenciais também salvas em: credenciais_geradas.txt")
        print("⚠️  Copie para o .env e depois DELETE este arquivo!")
        print()
        
    except Exception as e:
        print(f"⚠️  Não foi possível salvar arquivo: {e}")

if __name__ == "__main__":
    try:
        gerar_hash_senha()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()