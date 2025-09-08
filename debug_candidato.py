# debug_candidato.py - Testa geração de PDF com dados reais
import sys
import os
sys.path.append('backend')

from supabase_client import get_supabase_client
from pdf_utils import gerar_ficha_candidato
import json

def debug_candidatos():
    print("🔍 DEBUG: Analisando candidatos...")
    
    try:
        # Conectar Supabase
        supabase = get_supabase_client()
        
        # Buscar 1 candidato para teste
        response = supabase.table('candidatos').select('*').limit(1).execute()
        
        if not response.data:
            print("❌ Nenhum candidato encontrado!")
            return
        
        candidato = response.data[0]
        
        print("✅ Candidato encontrado:")
        print(f"📝 Nome: {candidato.get('nome_completo', 'SEM NOME')}")
        print(f"📧 Email: {candidato.get('email', 'SEM EMAIL')}")
        print(f"📞 Telefone: {candidato.get('telefone', 'SEM TELEFONE')}")
        print(f"🆔 ID: {candidato.get('id', 'SEM ID')}")
        
        print("\n📋 ESTRUTURA COMPLETA DO CANDIDATO:")
        for campo, valor in candidato.items():
            print(f"  {campo}: {valor}")
        
        print("\n🧪 TESTANDO GERAÇÃO DE PDF...")
        
        try:
            pdf_bytes = gerar_ficha_candidato(candidato)
            print(f"✅ PDF gerado! Tamanho: {len(pdf_bytes)} bytes")
            
            # Salvar PDF de teste
            with open("teste_ficha.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("💾 PDF salvo como 'teste_ficha.pdf'")
            
            return True
            
        except Exception as e:
            print(f"❌ ERRO na geração do PDF:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensagem: {str(e)}")
            
            import traceback
            print(f"   Traceback completo:")
            traceback.print_exc()
            
            return False
            
    except Exception as e:
        print(f"❌ ERRO na conexão/consulta:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        return False

if __name__ == "__main__":
    debug_candidatos()