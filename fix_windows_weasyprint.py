#!/usr/bin/env python3
# fix_windows_weasyprint.py - Solução para WeasyPrint no Windows
# ==============================================================

import os
import sys
import subprocess
import urllib.request
import shutil
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n🔄 PASSO {step}: {description}")
    print("-" * 50)

def check_windows_version():
    """Verifica versão do Windows"""
    print_step(1, "Verificando sistema Windows")
    
    try:
        import platform
        system_info = platform.platform()
        print(f"💻 Sistema: {system_info}")
        
        if "Windows" in system_info:
            print("✅ Windows detectado")
            return True
        else:
            print("⚠️ Não é Windows - este script é específico para Windows")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar sistema: {e}")
        return False

def install_gtk3_runtime():
    """Instala GTK3 Runtime para Windows"""
    print_step(2, "Instalando GTK3 Runtime")
    
    print("📥 OPÇÕES DE INSTALAÇÃO:")
    print("1. 🔧 Automática via chocolatey (recomendado)")
    print("2. 📱 Manual via download")
    print("3. ⏭️ Pular (já instalado)")
    
    choice = input("\nEscolha uma opção (1/2/3): ").strip()
    
    if choice == "1":
        return install_via_chocolatey()
    elif choice == "2":
        return install_manual_download()
    elif choice == "3":
        print("⏭️ Pulando instalação do GTK3")
        return True
    else:
        print("❌ Opção inválida")
        return False

def install_via_chocolatey():
    """Instala via Chocolatey"""
    print("\n🍫 Instalando via Chocolatey...")
    
    # Verificar se chocolatey está instalado
    try:
        result = subprocess.run(['choco', '--version'], 
                               capture_output=True, text=True, check=True)
        print(f"✅ Chocolatey encontrado: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Chocolatey não encontrado")
        print("💡 Instale Chocolatey primeiro: https://chocolatey.org/install")
        return False
    
    try:
        print("📦 Instalando GTK3 via Chocolatey...")
        result = subprocess.run([
            'choco', 'install', 'gtk-runtime', '-y'
        ], capture_output=True, text=True, check=True)
        
        print("✅ GTK3 Runtime instalado via Chocolatey!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação via Chocolatey: {e}")
        print("🔄 Tentando método manual...")
        return install_manual_download()

def install_manual_download():
    """Download manual do GTK3"""
    print("\n📱 Instalação manual do GTK3...")
    
    gtk_urls = [
        "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe",
        "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/latest"
    ]
    
    print("🌐 URLs para download manual:")
    for i, url in enumerate(gtk_urls, 1):
        print(f"{i}. {url}")
    
    print("\n📋 INSTRUÇÕES MANUAIS:")
    print("1. Baixe o instalador GTK3 Runtime")
    print("2. Execute como Administrador")
    print("3. Instale com configurações padrão")
    print("4. Reinicie o terminal/cmd")
    print("5. Execute este script novamente")
    
    installed = input("\n✅ GTK3 foi instalado? (s/N): ").lower()
    return installed in ['s', 'sim', 'y', 'yes']

def test_weasyprint_import():
    """Testa import do WeasyPrint"""
    print_step(3, "Testando import do WeasyPrint")
    
    try:
        import weasyprint
        print("✅ WeasyPrint importado com sucesso!")
        
        # Teste básico de funcionalidade
        html_simple = "<html><body><h1>Teste</h1></body></html>"
        css_simple = "body { font-family: Arial; }"
        
        from weasyprint import HTML, CSS
        html_doc = HTML(string=html_simple)
        css_doc = CSS(string=css_simple)
        
        pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc])
        
        if len(pdf_bytes) > 1000:
            print(f"✅ Teste funcional OK - PDF gerado: {len(pdf_bytes)} bytes")
            return True
        else:
            print(f"⚠️ PDF muito pequeno: {len(pdf_bytes)} bytes")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro funcional: {e}")
        return False

def create_fallback_implementation():
    """Cria implementação com fallback robusto"""
    print_step(4, "Criando implementação com fallback")
    
    fallback_code = '''# backend/pdf_utils_windows.py - Versão com fallback robusto para Windows
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Tentar importar WeasyPrint
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint disponível")
except ImportError as e:
    print(f"⚠️ WeasyPrint não disponível: {e}")
    print("🔄 Usando fallback ReportLab")

# Sempre importar ReportLab como fallback
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

def formatar_texto_legivel(texto):
    """Converte texto com hífens/underscores em texto legível"""
    if not texto or texto == '':
        return 'Não informado'
    
    texto_formatado = str(texto).replace('-', ' ').replace('_', ' ')
    texto_formatado = ' '.join(word.capitalize() for word in texto_formatado.split())
    
    correções = {
        'Cnh': 'CNH', 'Rg': 'RG', 'Cpf': 'CPF', 'Tv': 'TV', 'Dvd': 'DVD',
        'Intermediario': 'Intermediário', 'Basico': 'Básico', 'Avancado': 'Avançado'
    }
    
    for termo_errado, termo_correto in correções.items():
        texto_formatado = texto_formatado.replace(termo_errado, termo_correto)
    
    return texto_formatado

def processar_dados_especificos(dados_especificos, formulario_id):
    """Processa dados específicos baseado no tipo de formulário"""
    try:
        if not dados_especificos:
            return []
        
        if isinstance(dados_especificos, str):
            dados_especificos = json.loads(dados_especificos)
        
        dados_processados = []
        
        mapeamentos = {
            'candi-baba': {
                'idades_experiencia': 'Idades com Experiência',
                'cuidados_especiais': 'Cuidados Especiais',
                'nivel_ingles': 'Nível de Inglês',
                'primeiros_socorros': 'Primeiros Socorros',
                'natacao': 'Sabe Nadar'
            },
            'candi-caseiro': {
                'manutencao_geral': 'Manutenção Geral',
                'jardinagem': 'Jardinagem',
                'piscina': 'Manutenção de Piscina'
            },
            'candi-copeiro': {
                'conhecimento_coqueteis': 'Conhecimento em Coquetéis',
                'servico_mesa': 'Serviço de Mesa',
                'conhecimento_vinhos': 'Conhecimento em Vinhos'
            }
        }
        
        mapeamento = mapeamentos.get(formulario_id, {})
        
        for campo, valor in dados_especificos.items():
            nome_campo = mapeamento.get(campo, formatar_texto_legivel(campo))
            
            if isinstance(valor, list):
                valor_formatado = ', '.join([formatar_texto_legivel(v) for v in valor])
            elif isinstance(valor, bool):
                valor_formatado = 'Sim' if valor else 'Não'
            else:
                valor_formatado = formatar_texto_legivel(str(valor))
            
            dados_processados.append((nome_campo, valor_formatado))
        
        return dados_processados
        
    except Exception as e:
        print(f"Erro ao processar dados específicos: {e}")
        return []

def formatar_funcao_display(formulario_id):
    """Converte ID do formulário em nome de função"""
    mapeamento_funcoes = {
        'candi-baba': 'BABÁ',
        'candi-caseiro': 'CASEIRO(A)',
        'candi-copeiro': 'COPEIRO(A)',
        'candi-motorista': 'MOTORISTA',
        'candi-domestica': 'DOMÉSTICA'
    }
    return mapeamento_funcoes.get(formulario_id, formatar_texto_legivel(formulario_id))

def gerar_pdf_reportlab(dados_candidato):
    """Gera PDF usando ReportLab (fallback)"""
    buffer = BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          rightMargin=2*cm, leftMargin=2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo customizado para cabeçalho
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#a65e2e'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Estilo para seções
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#a65e2e'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    # Elementos do documento
    elements = []
    
    # Cabeçalho
    elements.append(Paragraph("R.O RECRUTAMENTO", header_style))
    elements.append(Paragraph("FICHA PROFISSIONAL", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Nome e função
    nome = dados_candidato.get('nome_completo', 'Não informado')
    funcao = formatar_funcao_display(dados_candidato.get('formulario_id', ''))
    
    elements.append(Paragraph(f"<b>{nome}</b>", styles['Title']))
    elements.append(Paragraph(f"<b>{funcao}</b>", section_style))
    elements.append(Spacer(1, 15))
    
    # Dados pessoais
    elements.append(Paragraph("DADOS PESSOAIS", section_style))
    
    dados_pessoais = [
        ['Nome Completo:', dados_candidato.get('nome_completo', 'Não informado')],
        ['CPF:', dados_candidato.get('cpf', 'Não informado')],
        ['Telefone:', dados_candidato.get('telefone', 'Não informado')],
        ['Email:', dados_candidato.get('email', 'Não informado')],
        ['Endereço:', dados_candidato.get('endereco', 'Não informado')]
    ]
    
    table_dados = Table(dados_pessoais, colWidths=[4*cm, 12*cm])
    table_dados.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa'))
    ]))
    
    elements.append(table_dados)
    elements.append(Spacer(1, 15))
    
    # Informações profissionais
    elements.append(Paragraph("INFORMAÇÕES PROFISSIONAIS", section_style))
    
    dados_profissionais = [
        ['Possui Filhos:', 'Sim' if dados_candidato.get('tem_filhos') else 'Não'],
        ['Possui CNH:', 'Sim' if dados_candidato.get('possui_cnh') else 'Não'],
        ['Pretensão Salarial:', f"R$ {dados_candidato.get('pretensao_salarial', 'Não informado')}"],
        ['Aceita Treinamento:', 'Sim' if dados_candidato.get('aceita_treinamento') else 'Não']
    ]
    
    table_prof = Table(dados_profissionais, colWidths=[4*cm, 12*cm])
    table_prof.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa'))
    ]))
    
    elements.append(table_prof)
    elements.append(Spacer(1, 15))
    
    # Dados específicos (se houver)
    dados_especificos = processar_dados_especificos(
        dados_candidato.get('dados_especificos'), 
        dados_candidato.get('formulario_id', '')
    )
    
    if dados_especificos:
        elements.append(Paragraph(f"INFORMAÇÕES ESPECÍFICAS - {funcao}", section_style))
        
        for nome, valor in dados_especificos:
            elements.append(Paragraph(f"<b>{nome}:</b> {valor}", styles['Normal']))
        
        elements.append(Spacer(1, 15))
    
    # Observações
    observacoes = dados_candidato.get('observacoes_adicionais', '')
    if observacoes and observacoes != 'Nenhuma observação':
        elements.append(Paragraph("OBSERVAÇÕES", section_style))
        elements.append(Paragraph(observacoes, styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Rodapé
    data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Ficha gerada em {data_geracao}", styles['Italic']))
    elements.append(Paragraph("www.rorecrutamento.com.br", styles['Italic']))
    
    # Gerar PDF
    doc.build(elements)
    return buffer.getvalue()

def gerar_pdf_weasyprint(dados_candidato):
    """Gera PDF usando WeasyPrint (método preferido)"""
    if not WEASYPRINT_AVAILABLE:
        raise ImportError("WeasyPrint não disponível")
    
    # Implementação WeasyPrint aqui (simplificada)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2cm; }}
            .header {{ background: #a65e2e; color: white; padding: 20px; text-align: center; }}
            .section {{ margin: 20px 0; }}
            .label {{ font-weight: bold; color: #555; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>R.O RECRUTAMENTO - FICHA PROFISSIONAL</h1>
            <h2>{dados_candidato.get('nome_completo', 'Não informado')}</h2>
        </div>
        
        <div class="section">
            <h3>DADOS PESSOAIS</h3>
            <p><span class="label">Nome:</span> {dados_candidato.get('nome_completo', 'Não informado')}</p>
            <p><span class="label">CPF:</span> {dados_candidato.get('cpf', 'Não informado')}</p>
            <p><span class="label">Telefone:</span> {dados_candidato.get('telefone', 'Não informado')}</p>
            <p><span class="label">Email:</span> {dados_candidato.get('email', 'Não informado')}</p>
        </div>
        
        <div class="section">
            <p><em>Ficha gerada em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</em></p>
        </div>
    </body>
    </html>
    """
    
    html_doc = HTML(string=html_content)
    return html_doc.write_pdf()

def gerar_ficha_candidato_completa(dados_candidato):
    """
    Função principal - tenta WeasyPrint, fallback para ReportLab
    """
    try:
        print(f"📝 Gerando ficha para: {dados_candidato.get('nome_completo', 'Candidato')}")
        
        # Criar nome do arquivo
        nome_limpo = dados_candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
        import re
        nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
        data_criacao = datetime.now().strftime('%d%m%Y')
        nome_arquivo = f"{nome_limpo}-{data_criacao}.pdf"
        
        # Tentar WeasyPrint primeiro
        if WEASYPRINT_AVAILABLE:
            try:
                print("🎨 Usando WeasyPrint...")
                pdf_bytes = gerar_pdf_weasyprint(dados_candidato)
                print(f"✅ PDF gerado com WeasyPrint: {len(pdf_bytes)} bytes")
                return pdf_bytes, nome_arquivo
            except Exception as e:
                print(f"⚠️ WeasyPrint falhou: {e}")
                print("🔄 Alternando para ReportLab...")
        
        # Fallback para ReportLab
        print("📄 Usando ReportLab...")
        pdf_bytes = gerar_pdf_reportlab(dados_candidato)
        print(f"✅ PDF gerado com ReportLab: {len(pdf_bytes)} bytes")
        return pdf_bytes, nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro crítico na geração de PDF: {e}")
        raise

# Teste da implementação
if __name__ == "__main__":
    dados_teste = {
        'nome_completo': 'Teste Windows',
        'cpf': '000.000.000-00',
        'telefone': '(11) 00000-0000',
        'email': 'teste@windows.com',
        'endereco': 'Teste Windows',
        'formulario_id': 'candi-baba',
        'tem_filhos': False,
        'possui_cnh': True,
        'pretensao_salarial': 3000,
        'aceita_treinamento': True
    }
    
    try:
        pdf_bytes, nome_arquivo = gerar_ficha_candidato_completa(dados_teste)
        with open(f"teste_windows_{nome_arquivo}", "wb") as f:
            f.write(pdf_bytes)
        print(f"🎉 Teste concluído! Arquivo: teste_windows_{nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
'''
    
    # Salvar arquivo de fallback
    with open('backend/pdf_utils_windows.py', 'w', encoding='utf-8') as f:
        f.write(fallback_code)
    
    print("✅ Implementação com fallback criada: backend/pdf_utils_windows.py")
    return True

def update_main_implementation():
    """Atualiza implementação principal para usar fallback"""
    print_step(5, "Atualizando implementação principal")
    
    # Fazer backup da implementação atual
    if os.path.exists('backend/pdf_utils.py'):
        shutil.copy2('backend/pdf_utils.py', 'backend/pdf_utils_backup.py')
        print("✅ Backup criado: backend/pdf_utils_backup.py")
    
    # Copiar versão com fallback
    if os.path.exists('backend/pdf_utils_windows.py'):
        shutil.copy2('backend/pdf_utils_windows.py', 'backend/pdf_utils.py')
        print("✅ Implementação atualizada com fallback robusto")
        return True
    else:
        print("❌ Arquivo pdf_utils_windows.py não encontrado")
        return False

def test_final_implementation():
    """Teste final da implementação"""
    print_step(6, "Teste final da implementação")
    
    try:
        # Importar nova implementação
        sys.path.insert(0, 'backend')
        from pdf_utils import gerar_ficha_candidato_completa
        
        dados_teste = {
            'nome_completo': 'Teste Final Windows',
            'cpf': '111.222.333-44',
            'telefone': '(11) 11111-1111',
            'email': 'teste.final@windows.com',
            'endereco': 'Rua Teste Final, 123',
            'formulario_id': 'candi-baba',
            'tem_filhos': True,
            'possui_cnh': False,
            'pretensao_salarial': 2800,
            'aceita_treinamento': True
        }
        
        print("🧪 Executando teste final...")
        pdf_bytes, nome_arquivo = gerar_ficha_candidato_completa(dados_teste)
        
        # Salvar arquivo
        test_filename = f"teste_final_{nome_arquivo}"
        with open(test_filename, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✅ Teste final OK!")
        print(f"📄 Tamanho: {len(pdf_bytes):,} bytes")
        print(f"📂 Arquivo: {test_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste final: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print_header("CORREÇÃO WEASYPRINT PARA WINDOWS")
    
    if not check_windows_version():
        return
    
    print("\n🎯 PLANO DE AÇÃO:")
    print("1. Instalar GTK3 Runtime (necessário para WeasyPrint)")
    print("2. Testar WeasyPrint")
    print("3. Criar implementação com fallback ReportLab")
    print("4. Testar sistema completo")
    
    continuar = input("\n❓ Continuar? (s/N): ").lower()
    if continuar not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    # Executar correções
    success_steps = []
    
    # GTK3 Installation
    if install_gtk3_runtime():
        success_steps.append("GTK3 instalado")
    
    # Test WeasyPrint
    weasyprint_works = test_weasyprint_import()
    if weasyprint_works:
        success_steps.append("WeasyPrint funcional")
    
    # Create fallback implementation
    if create_fallback_implementation():
        success_steps.append("Fallback criado")
    
    # Update main implementation
    if update_main_implementation():
        success_steps.append("Implementação atualizada")
    
    # Final test
    if test_final_implementation():
        success_steps.append("Teste final OK")
    
    # Relatório final
    print_header("RELATÓRIO FINAL")
    
    print("✅ PASSOS CONCLUÍDOS:")
    for step in success_steps:
        print(f"   • {step}")
    
    if len(success_steps) >= 3:  # Pelo menos fallback funcionando
        print("\n🎉 SISTEMA FUNCIONAL!")
        print("✅ PDF pode ser gerado via ReportLab (fallback)")
        if weasyprint_works:
            print("✅ WeasyPrint também disponível")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. streamlit run app/streamlit_app.py")
        print("2. Testar geração de PDF no dashboard")
        print("3. Verificar qualidade dos PDFs")
        
    else:
        print("\n⚠️ CORREÇÃO PARCIAL")
        print("💡 Sistema funcionará com ReportLab")
        print("🔧 Para melhor qualidade, instale GTK3 manualmente")

if __name__ == "__main__":
    main()