# backend/google_drive_backup_oauth.py
"""
Sistema de Backup Automático para Google Drive - VERSÃO OAUTH
R.O Recrutamento - Sistema de Gestão de Candidatos e Vagas
"""

import os
import json
import zipfile
import pickle
from datetime import datetime
from io import BytesIO
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import logging

# Google Drive API com OAuth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# Supabase
import sys
sys.path.append(os.path.dirname(__file__))
from supabase_client import get_supabase_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURAÇÕES
# ============================================

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'credentials/token.pickle'
CREDENTIALS_FILE = 'credentials/credentials.json'

class GoogleDriveBackupOAuth:
    """Gerenciador de backups no Google Drive usando OAuth"""
    
    def __init__(
        self, 
        folder_id: str,
        max_retention: int = 30
    ):
        """
        Inicializa o sistema de backup
        
        Args:
            folder_id: ID da pasta do Google Drive para backups
            max_retention: Número máximo de backups a manter
        """
        self.folder_id = folder_id
        self.max_retention = max_retention
        self.service = None
        
        logger.info("✅ Sistema de backup OAuth inicializado")
    
    def _get_credentials(self) -> Credentials:
        """Obtém credenciais OAuth"""
        creds = None
        
        # Tentar carregar token salvo
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"❌ Arquivo de credenciais não encontrado: {CREDENTIALS_FILE}\n"
                        f"Baixe o arquivo OAuth 2.0 Client ID do Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais para próxima vez
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def _get_drive_service(self):
        """Cria e retorna serviço do Google Drive"""
        if self.service is None:
            try:
                creds = self._get_credentials()
                self.service = build('drive', 'v3', credentials=creds)
                logger.info("✅ Conectado ao Google Drive")
            except Exception as e:
                logger.error(f"❌ Erro ao conectar no Google Drive: {e}")
                raise
        
        return self.service
    
    def backup_supabase_tables(self, compress: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Faz backup de todas as tabelas do Supabase
        
        Args:
            compress: Se True, comprime o backup em ZIP
            
        Returns:
            Tuple (sucesso, file_id no Drive)
        """
        try:
            logger.info("🔄 Iniciando backup do Supabase...")
            
            # Conectar no Supabase
            supabase = get_supabase_client()
            
            # Tabelas para backup
            tabelas = [
                'candidatos',
                'candidatos_qualificados',
                'vagas',
                'vaga_observacoes',
                'candidatos_vagas'
            ]
            
            # Coletar dados de todas as tabelas
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'tables': {}
            }
            
            for tabela in tabelas:
                try:
                    logger.info(f"📥 Fazendo backup da tabela: {tabela}")
                    response = supabase.table(tabela).select('*').execute()
                    
                    if response.data:
                        backup_data['tables'][tabela] = response.data
                        logger.info(f"✅ {tabela}: {len(response.data)} registros")
                    else:
                        backup_data['tables'][tabela] = []
                        logger.warning(f"⚠️ {tabela}: tabela vazia")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao fazer backup de {tabela}: {e}")
                    backup_data['tables'][tabela] = {
                        'error': str(e),
                        'data': []
                    }
            
            # Criar nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_base = f"backup_ro_recrutamento_{timestamp}"
            
            # Salvar como JSON
            json_content = json.dumps(backup_data, ensure_ascii=False, indent=2)
            
            if compress:
                # Comprimir em ZIP
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.writestr(f"{filename_base}.json", json_content)
                
                zip_buffer.seek(0)
                file_content = zip_buffer
                filename = f"{filename_base}.zip"
                mime_type = 'application/zip'
                logger.info("✅ Backup comprimido em ZIP")
            else:
                # Enviar JSON direto
                file_content = BytesIO(json_content.encode('utf-8'))
                filename = f"{filename_base}.json"
                mime_type = 'application/json'
            
            # Upload para o Drive
            file_id = self._upload_to_drive(
                file_content,
                filename,
                mime_type
            )
            
            if file_id:
                logger.info(f"✅ Backup salvo no Google Drive: {filename}")
                
                # Limpar backups antigos
                self._cleanup_old_backups()
                
                return True, file_id
            else:
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Erro ao fazer backup: {e}")
            return False, None
    
    def _upload_to_drive(
        self,
        file_content: BytesIO,
        filename: str,
        mime_type: str
    ) -> Optional[str]:
        """
        Faz upload de arquivo para o Google Drive
        
        Returns:
            ID do arquivo no Drive ou None se falhar
        """
        try:
            service = self._get_drive_service()
            
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            media = MediaIoBaseUpload(
                file_content,
                mimetype=mime_type,
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, createdTime, size'
            ).execute()
            
            file_id = file.get('id')
            file_size = int(file.get('size', 0)) / (1024 * 1024)  # MB
            
            logger.info(f"✅ Upload concluído: {filename} ({file_size:.2f} MB)")
            logger.info(f"🆔 File ID: {file_id}")
            
            return file_id
            
        except HttpError as e:
            logger.error(f"❌ Erro HTTP ao fazer upload: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao fazer upload: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """Remove backups antigos mantendo apenas os mais recentes"""
        try:
            service = self._get_drive_service()
            
            # Buscar todos os backups na pasta
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                fields="files(id, name, createdTime)",
                orderBy="createdTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            if len(files) <= self.max_retention:
                logger.info(f"✅ Total de backups: {len(files)} (dentro do limite)")
                return
            
            # Deletar backups excedentes
            files_to_delete = files[self.max_retention:]
            
            for file in files_to_delete:
                try:
                    service.files().delete(fileId=file['id']).execute()
                    logger.info(f"🗑️ Backup antigo removido: {file['name']}")
                except Exception as e:
                    logger.error(f"❌ Erro ao deletar {file['name']}: {e}")
            
            logger.info(f"✅ Limpeza concluída. Mantidos {self.max_retention} backups")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de backups: {e}")
    
    def list_backups(self) -> List[Dict]:
        """
        Lista todos os backups disponíveis no Drive
        
        Returns:
            Lista de dicionários com informações dos backups
        """
        try:
            service = self._get_drive_service()
            
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                fields="files(id, name, createdTime, size)",
                orderBy="createdTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            backups = []
            for file in files:
                size_mb = int(file.get('size', 0)) / (1024 * 1024)
                backups.append({
                    'id': file['id'],
                    'name': file['name'],
                    'created': file['createdTime'],
                    'size_mb': f"{size_mb:.2f}"
                })
            
            return backups
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar backups: {e}")
            return []


# ============================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================

def criar_backup_automatico() -> Tuple[bool, Optional[str]]:
    """
    Cria backup automático usando variáveis de ambiente
    
    Returns:
        Tuple (sucesso, file_id)
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    folder_id = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
    max_retention = int(os.getenv('BACKUP_MAX_RETENTION', '30'))
    compress = os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true'
    
    if not folder_id:
        logger.error("❌ GOOGLE_DRIVE_BACKUP_FOLDER_ID não configurado!")
        return False, None
    
    backup_manager = GoogleDriveBackupOAuth(
        folder_id=folder_id,
        max_retention=max_retention
    )
    
    return backup_manager.backup_supabase_tables(compress=compress)


def listar_backups_disponiveis() -> List[Dict]:
    """
    Lista todos os backups disponíveis
    
    Returns:
        Lista de backups
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    folder_id = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
    
    if not folder_id:
        logger.error("❌ GOOGLE_DRIVE_BACKUP_FOLDER_ID não configurado!")
        return []
    
    backup_manager = GoogleDriveBackupOAuth(
        folder_id=folder_id
    )
    
    return backup_manager.list_backups()


# ============================================
# TESTE
# ============================================

if __name__ == "__main__":
    print("🧪 Testando sistema de backup OAuth...")
    
    sucesso, file_id = criar_backup_automatico()
    
    if sucesso:
        print(f"✅ Backup criado com sucesso!")
        print(f"🆔 File ID: {file_id}")
        
        print("\n📋 Listando backups disponíveis:")
        backups = listar_backups_disponiveis()
        for backup in backups:
            print(f"  • {backup['name']} - {backup['size_mb']} MB - {backup['created']}")
    else:
        print("❌ Falha ao criar backup")