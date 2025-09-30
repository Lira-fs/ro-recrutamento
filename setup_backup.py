#!/usr/bin/env python3
"""
Script de Configuração do Sistema de Backup
R.O Recrutamento
"""

import os
import json
from pathlib import Path

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(number, text):
    """Imprime número do passo"""
    print(f"\n{'='*60}")
    print(f"PASSO {number}: {text}")
    print('='*60 + "\n")

def verificar_estrutura_pastas():
    """Verifica e cria estrutura de pastas necessária"""
    print_step(1, "Verificando Estrutura de Pastas")
    
    pastas_necessarias = [
        'backend',
        'credentials',
        'app',
        'templates'
    ]
    
    for pasta in pastas_necessarias:
        caminho = Path(pasta)
        if caminho.exists():
            print(f"✅ Pasta '{pasta}' encontrada")
        else:
            caminho.mkdir(exist_ok=True)
            print(f"📁 Pasta '{pasta}' criada")
    
    return True

def verificar_credenciais_google():
    """Verifica arquivo de credenciais do Google"""
    print_step(2, "Verificando Credenciais do Google Drive")
    
    cred_path = Path('credentials/service-account.json')
    
    if cred_path.exists():
        print(f"✅ Arquivo de credenciais encontrado: {cred_path}")
        
        # Validar JSON
        try:
            with open(cred_path, 'r') as f:
                cred_data = json.load(f)
            
            # Verificar campos obrigatórios
            campos_obrigatorios = [
                'type',
                'project_id',
                'private_key_id',
                'private_key',
                'client_email',
                'client_id'
            ]
            
            campos_faltando = [campo for campo in campos_obrigatorios 
                             if campo not in cred_data]
            
            if campos_faltando:
                print(f"⚠️ Campos faltando no JSON: {', '.join(campos_faltando)}")
                return False
            
            print(f"✅ Arquivo de credenciais válido")
            print(f"📧 Service Account Email: {cred_data['client_email']}")
            print(f"🆔 Project ID: {cred_data['project_id']}")
            
            return True
            
        except json.JSONDecodeError:
            print("❌ Arquivo JSON inválido!")
            return False
    else:
        print(f"❌ Arquivo de credenciais NÃO encontrado: {cred_path}")
        print("\n📝 COMO OBTER AS CREDENCIAIS:")
        print("""
        1. Acesse: https://console.cloud.google.com
        2. Crie um novo projeto (ou use existente)
        3. Ative a API do Google Drive
        4. Vá em: IAM & Admin → Service Accounts
        5. Crie uma nova Service Account
        6. Baixe o arquivo JSON das credenciais
        7. Renomeie para 'service-account.json'
        8. Coloque na pasta 'credentials/'
        """)
        return False

def verificar_env():
    """Verifica arquivo .env"""
    print_step(3, "Verificando Arquivo .env")
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    # Ler .env
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Verificar variáveis do Google Drive
    variaveis_necessarias = [
        'GOOGLE_SERVICE_ACCOUNT_FILE',
        'GOOGLE_DRIVE_BACKUP_FOLDER_ID'
    ]
    
    faltando = []
    for var in variaveis_necessarias:
        if var not in env_content:
            faltando.append(var)
            print(f"⚠️ Variável '{var}' não encontrada no .env")
        else:
            print(f"✅ Variável '{var}' configurada")
    
    if faltando:
        print("\n❌ Configure as variáveis faltantes no .env:")
        print("""
        GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
        GOOGLE_DRIVE_BACKUP_FOLDER_ID=sua_pasta_id_aqui
        GOOGLE_SERVICE_ACCOUNT_EMAIL=seu-service-account@projeto.iam.gserviceaccount.com
        BACKUP_INTERVAL_HOURS=24
        BACKUP_MAX_RETENTION=30
        BACKUP_AUTO_START=true
        BACKUP_COMPRESSION=true
        """)
        return False
    
    return True

def verificar_dependencias():
    """Verifica se todas as bibliotecas estão instaladas"""
    print_step(4, "Verificando Dependências")
    
    dependencias = [
        ('google-api-python-client', 'googleapiclient'),
        ('google-auth', 'google.auth'),
        ('supabase', 'supabase'),
        ('python-dotenv', 'dotenv'),
        ('schedule', 'schedule')
    ]
    
    todas_instaladas = True
    
    for nome_pip, nome_import in dependencias:
        try:
            __import__(nome_import)
            print(f"✅ {nome_pip}")
        except ImportError:
            print(f"❌ {nome_pip} NÃO instalado")
            todas_instaladas = False
    
    if not todas_instaladas:
        print("\n📦 Instale as dependências faltantes:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def testar_conexao_drive():
    """Testa conexão com Google Drive"""
    print_step(5, "Testando Conexão com Google Drive")
    
    try:
        from dotenv import load_dotenv
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        load_dotenv()
        
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        if not service_account_file or not os.path.exists(service_account_file):
            print("❌ Arquivo de credenciais não encontrado")
            return False
        
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # Testar listagem
        results = service.files().list(pageSize=1).execute()
        
        print("✅ Conexão com Google Drive estabelecida com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar no Google Drive: {e}")
        return False

def testar_backup_completo():
    """Executa teste completo de backup"""
    print_step(6, "Executando Teste de Backup")
    
    try:
        import sys
        sys.path.append('backend')
        
        from google_drive_backup import criar_backup_automatico
        
        print("🔄 Criando backup de teste...")
        sucesso, file_id = criar_backup_automatico()
        
        if sucesso:
            print(f"✅ Backup de teste criado com sucesso!")
            print(f"🆔 File ID: {file_id}")
            return True
        else:
            print("❌ Falha ao criar backup de teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de backup: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print_header("CONFIGURAÇÃO DO SISTEMA DE BACKUP")
    print("R.O Recrutamento - Sistema de Gestão")
    
    print("\n🎯 Este script irá:")
    print("  1. Verificar estrutura de pastas")
    print("  2. Validar credenciais do Google Drive")
    print("  3. Verificar arquivo .env")
    print("  4. Testar dependências")
    print("  5. Testar conexão com Google Drive")
    print("  6. Executar backup de teste")
    
    continuar = input("\n❓ Continuar? (s/n): ")
    
    if continuar.lower() != 's':
        print("❌ Configuração cancelada")
        return
    
    # Executar verificações
    resultados = []
    
    resultados.append(("Estrutura de Pastas", verificar_estrutura_pastas()))
    resultados.append(("Credenciais Google", verificar_credenciais_google()))
    resultados.append(("Arquivo .env", verificar_env()))
    resultados.append(("Dependências", verificar_dependencias()))
    resultados.append(("Conexão Drive", testar_conexao_drive()))
    resultados.append(("Backup Teste", testar_backup_completo()))
    
    # Resumo
    print_header("RESUMO DA CONFIGURAÇÃO")
    
    for nome, sucesso in resultados:
        status = "✅" if sucesso else "❌"
        print(f"{status} {nome}")
    
    todos_ok = all(resultado[1] for resultado in resultados)
    
    if todos_ok:
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n✅ Sistema de backup está pronto para uso")
        print("\n💡 Próximos passos:")
        print("  1. Execute: streamlit run app/streamlit_app.py")
        print("  2. Acesse a aba '💾 Backups' no dashboard")
        print("  3. Crie seu primeiro backup manual")
    else:
        print("\n⚠️ CONFIGURAÇÃO INCOMPLETA")
        print("Corrija os problemas acima e execute este script novamente")

if __name__ == "__main__":
    main()