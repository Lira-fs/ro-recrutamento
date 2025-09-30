# backend/google_drive_backup.py
"""
Sistema de Backup Automático para Google Drive
R.O Recrutamento - Sistema de Gestão de Candidatos e Vagas
"""

import os
import json
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import logging

# Google Drive API
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

# Supabase
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

class GoogleDriveBackup:
    """Gerenciador de backups no Google Drive"""
    
    def __init__(
        self, 
        service_account_file: str,
        folder_id: str,
        max_retention: int = 30
    ):
        """
        Inicializa o sistema de backup
        
        Args:
            service_account_file: Caminho para o arquivo JSON de credenciais
            folder_id: ID da pasta do Google Drive para backups
            max_retention: Número máximo de backups a manter
        """
        self.service_account_file = service_account_file
        self.folder_id = folder_id
        self.max_retention = max_retention
        self.service = None
        
        # Validar arquivo de credenciais
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(
                f"❌ Arquivo de credenciais não encontrado: {service_account_file}\n"
                f"Certifique-se de criar a pasta 'credentials' e colocar o arquivo JSON lá."
            )
        
        logger.info("✅ Sistema de backup inicializado")
    
    def _get_drive_service(self):
        """Cria e retorna serviço do Google Drive"""
        if self.service is None:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_file,
                    scopes=SCOPES
                )
                self.service = build('drive', 'v3', credentials=credentials)
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
    
    def download_backup(self, file_id: str, output_path: str) -> bool:
        """
        Baixa um backup específico do Drive
        
        Args:
            file_id: ID do arquivo no Drive
            output_path: Caminho local para salvar
            
        Returns:
            True se sucesso
        """
        try:
            service = self._get_drive_service()
            
            request = service.files().get_media(fileId=file_id)
            
            with open(output_path, 'wb') as f:
                from googleapiclient.http import MediaIoBaseDownload
                downloader = MediaIoBaseDownload(f, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"📥 Download: {progress}%")
            
            logger.info(f"✅ Backup baixado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar backup: {e}")
            return False
    
    def restore_backup(self, file_id: str, tables: Optional[List[str]] = None) -> bool:
        """
        Restaura backup do Drive para o Supabase
        
        Args:
            file_id: ID do arquivo no Drive
            tables: Lista de tabelas para restaurar (None = todas)
            
        Returns:
            True se sucesso
        """
        try:
            logger.info("🔄 Iniciando restauração do backup...")
            
            # Baixar backup temporariamente
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                tmp_path = tmp.name
            
            if not self.download_backup(file_id, tmp_path):
                return False
            
            # Ler dados do backup
            with open(tmp_path, 'r', encoding='utf-8') as f:
                if tmp_path.endswith('.zip'):
                    # Descomprimir se necessário
                    with zipfile.ZipFile(tmp_path, 'r') as zip_file:
                        json_content = zip_file.read(zip_file.namelist()[0])
                        backup_data = json.loads(json_content)
                else:
                    backup_data = json.load(f)
            
            # Conectar no Supabase
            supabase = get_supabase_client()
            
            # Restaurar tabelas
            tables_to_restore = tables or list(backup_data['tables'].keys())
            
            for tabela in tables_to_restore:
                if tabela not in backup_data['tables']:
                    logger.warning(f"⚠️ Tabela {tabela} não encontrada no backup")
                    continue
                
                registros = backup_data['tables'][tabela]
                
                if not registros:
                    logger.info(f"⏭️ {tabela}: sem dados para restaurar")
                    continue
                
                try:
                    logger.info(f"📥 Restaurando {tabela}: {len(registros)} registros")
                    
                    # Inserir em lotes
                    batch_size = 100
                    for i in range(0, len(registros), batch_size):
                        batch = registros[i:i + batch_size]
                        supabase.table(tabela).upsert(batch).execute()
                    
                    logger.info(f"✅ {tabela} restaurada com sucesso")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao restaurar {tabela}: {e}")
            
            # Limpar arquivo temporário
            os.unlink(tmp_path)
            
            logger.info("✅ Restauração concluída!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na restauração: {e}")
            return False


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
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    folder_id = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
    max_retention = int(os.getenv('BACKUP_MAX_RETENTION', '30'))
    compress = os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true'
    
    if not service_account_file or not folder_id:
        logger.error("❌ Variáveis de ambiente não configuradas!")
        return False, None
    
    backup_manager = GoogleDriveBackup(
        service_account_file=service_account_file,
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
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    folder_id = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
    
    if not service_account_file or not folder_id:
        logger.error("❌ Variáveis de ambiente não configuradas!")
        return []
    
    backup_manager = GoogleDriveBackup(
        service_account_file=service_account_file,
        folder_id=folder_id
    )
    
    return backup_manager.list_backups()


# ============================================
# TESTE
# ============================================

if __name__ == "__main__":
    print("🧪 Testando sistema de backup...")
    
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