# backend/pdf_utils_weasyprint.py - NOVA VERSÃO COM WEASYPRINT
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
import base64

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

def render_html(template_name, context):
    """
    Renderiza template HTML usando Jinja2
    """
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    return template.render(**context)

def formatar_texto_legivel(texto):
    """
    Converte texto com hífens/underscores em texto legível
    """
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
    """
    Processa o campo dados_especificos (JSON) baseado no tipo de formulário
    """
    try:
        if not dados_especificos:
            return []
        
        # Parse JSON se for string
        if isinstance(dados_especificos, str):
            dados_especificos = json.loads(dados_especificos)
        
        dados_processados = []
        
        # MAPEAMENTO POR TIPO DE FORMULÁRIO
        mapeamentos = {
            'candi-baba': {
                'idades_experiencia': 'Idades com Experiência',
                'cuidados_especiais': 'Cuidados Especiais',
                'atividades_pedagogicas': 'Atividades Pedagógicas',
                'nivel_ingles': 'Nível de Inglês',
                'primeiros_socorros': 'Primeiros Socorros',
                'natacao': 'Sabe Nadar',
                'disponibilidade_viagens': 'Disponível para Viagens'
            },
            'candi-caseiro': {
                'manutencao_geral': 'Manutenção Geral',
                'jardinagem': 'Jardinagem',
                'piscina': 'Manutenção de Piscina',
                'eletrica_basica': 'Elétrica Básica',
                'encanamento_basico': 'Encanamento Básico',
                'seguranca': 'Conhecimentos de Segurança',
                'animais_domesticos': 'Cuidado com Animais'
            },
            'candi-copeiro': {
                'conhecimento_coqueteis': 'Conhecimento em Coquetéis',
                'servico_mesa': 'Serviço de Mesa',
                'conhecimento_vinhos': 'Conhecimento em Vinhos',
                'experiencia_eventos': 'Experiência em Eventos',
                'idiomas_conversacao': 'Idiomas para Conversação'
            },
            'candi-motorista': {
                'categoria_cnh': 'Categoria da CNH',
                'experiencia_categoria': 'Experiência na Categoria',
                'veiculos_grandes': 'Conduz Veículos Grandes',
                'conhecimento_mecanica': 'Conhecimento em Mecânica',
                'disponibilidade_viagens': 'Disponível para Viagens',
                'conhecimento_rotas': 'Conhecimento de Rotas'
            },
            'candi-domestica': {
                'tipos_limpeza': 'Tipos de Limpeza',
                'organizacao': 'Organização',
                'cuidado_roupas': 'Cuidado com Roupas',
                'cozinha_basica': 'Cozinha Básica',
                'experiencia_casas_grandes': 'Experiência em Casas Grandes'
            }
        }
        
        # Obter mapeamento para o formulário
        mapeamento = mapeamentos.get(formulario_id, {})
        
        # Processar cada campo
        for campo, valor in dados_especificos.items():
            # Usar mapeamento se existir, senão formatar campo
            nome_campo = mapeamento.get(campo, formatar_texto_legivel(campo))
            
            # Processar valor
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

def processar_referencias(referencias):
    """
    Processa lista de referências
    """
    try:
        if not referencias:
            return []
        
        # Parse JSON se for string
        if isinstance(referencias, str):
            referencias = json.loads(referencias)
        
        referencias_processadas = []
        
        for ref in referencias:
            if isinstance(ref, dict):
                referencias_processadas.append({
                    'nome': ref.get('nome', 'Não informado'),
                    'telefone': ref.get('telefone', 'Não informado'),
                    'relacao': formatar_texto_legivel(ref.get('relacao', 'Não informado')),
                    'periodo_inicio': ref.get('periodo_inicio', ''),
                    'periodo_fim': ref.get('periodo_fim', '')
                })
        
        return referencias_processadas
        
    except Exception as e:
        print(f"Erro ao processar referências: {e}")
        return []

def formatar_funcao_display(formulario_id):
    """
    Converte ID do formulário em nome de função para exibição
    """
    mapeamento_funcoes = {
        'candi-baba': 'BABÁ',
        'candi-caseiro': 'CASEIRO(A)',
        'candi-copeiro': 'COPEIRO(A)',
        'candi-motorista': 'MOTORISTA',
        'candi-domestica': 'DOMÉSTICA',
        'candi-cozinheiro': 'COZINHEIRO(A)',
        'candi-jardineiro': 'JARDINEIRO(A)',
        'candi-seguranca': 'SEGURANÇA'
    }
    
    return mapeamento_funcoes.get(formulario_id, formatar_texto_legivel(formulario_id))

def gerar_css_customizado():
    """
    Retorna CSS otimizado para WeasyPrint
    """
    return """
    @page {
        size: A4;
        margin: 2.5cm;
        background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjEwIiBoZWlnaHQ9IjI5NyIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjZmNmY2ZjIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjZjhmOGY4Ii8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNiZykiLz48L3N2Zz4=');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        
        @bottom-center {
            content: "www.rorecrutamento.com.br | Documento confidencial - Uso restrito";
            font-size: 10px;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 5px;
        }
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Arial', 'DejaVu Sans', sans-serif;
        color: #333;
        line-height: 1.5;
        background: rgba(255, 255, 255, 0.95);
    }
    
    .container {
        width: 100%;
        padding: 0;
    }
    
    /* CABEÇALHO */
    .header {
        text-align: center;
        margin-bottom: 25px;
        padding: 20px 0;
        background: linear-gradient(135deg, #fff8f0, #f4e8d0);
        border-radius: 12px;
        border: 2px solid #a65e2e;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }
    
    .logo-placeholder {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #a65e2e, #d4a574);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
        margin-right: 15px;
    }
    
    .company-info {
        text-align: left;
    }
    
    .company-name {
        font-size: 24px;
        font-weight: bold;
        color: #a65e2e;
        margin-bottom: 3px;
    }
    
    .company-subtitle {
        font-size: 12px;
        color: #666;
        font-style: italic;
    }
    
    /* TÍTULO DO DOCUMENTO */
    .title-section {
        background: linear-gradient(135deg, #a65e2e, #d4a574);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    
    .document-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .candidate-name {
        font-size: 26px;
        font-weight: bold;
        margin-top: 8px;
    }
    
    /* FUNÇÃO/CARGO */
    .highlight-box {
        background: linear-gradient(135deg, #fff8f0, #f4e8d0);
        border: 2px solid #a65e2e;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        text-align: center;
    }
    
    .function-badge {
        background: linear-gradient(135deg, #a65e2e, #d4a574);
        color: white;
        padding: 12px 25px;
        border-radius: 25px;
        font-size: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    
    /* SEÇÕES DE CONTEÚDO */
    .content-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        border-left: 5px solid #a65e2e;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
        font-size: 18px;
        font-weight: bold;
        color: #a65e2e;
        margin-bottom: 18px;
        padding-bottom: 8px;
        border-bottom: 2px solid #a65e2e;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .info-item {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
    }
    
    .info-label {
        font-weight: bold;
        color: #555;
        font-size: 13px;
        margin-bottom: 5px;
    }
    
    .info-value {
        color: #333;
        font-size: 14px;
        word-wrap: break-word;
    }
    
    .full-width {
        grid-column: 1 / -1;
    }
    
    /* SEÇÃO DE REFERÊNCIAS */
    .referencias-section {
        background: rgba(255, 248, 240, 0.95);
        border: 2px solid #d4a574;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .referencia-item {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
    }
    
    .referencia-item:last-child {
        margin-bottom: 0;
    }
    
    /* OBSERVAÇÕES */
    .observacoes-box {
        background: rgba(248, 249, 250, 0.95);
        border: 2px dashed #a65e2e;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .empty-space {
        background: #f8f9fa;
        padding: 40px;
        border-radius: 8px;
        border: 2px dashed #ccc;
        text-align: center;
        color: #666;
        margin: 20px 0;
    }
    
    /* RODAPÉ */
    .footer {
        margin-top: 30px;
        padding: 20px 0;
        border-top: 2px solid #a65e2e;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #666;
    }
    
    .contact-info {
        display: flex;
        gap: 20px;
    }
    
    .contact-item {
        font-weight: bold;
        color: #a65e2e;
    }
    
    .generated-info {
        text-align: right;
        line-height: 1.4;
    }
    
    /* RESPONSIVIDADE PARA PDF */
    @media print {
        .info-grid {
            display: block;
        }
        
        .info-item {
            display: block;
            margin-bottom: 10px;
        }
    }
    """

def gerar_ficha_candidato_completa(dados_candidato):
    """
    Gera PDF completo da ficha do candidato usando WeasyPrint
    
    Args:
        dados_candidato (dict): Dicionário com todos os dados do candidato
    
    Returns:
        tuple: (pdf_bytes, nome_arquivo)
    """
    try:
        print(f"📝 Gerando ficha para: {dados_candidato.get('nome_completo', 'Candidato sem nome')}")
        
        # Processar dados
        dados_especificos = processar_dados_especificos(
            dados_candidato.get('dados_especificos'), 
            dados_candidato.get('formulario_id', '')
        )
        
        referencias = processar_referencias(dados_candidato.get('referencias', []))
        
        # Formatar data de cadastro
        data_cadastro = 'Não informado'
        if dados_candidato.get('created_at'):
            try:
                data_obj = datetime.fromisoformat(dados_candidato['created_at'].replace('Z', '+00:00'))
                data_cadastro = data_obj.strftime('%d/%m/%Y')
            except:
                data_cadastro = str(dados_candidato['created_at'])[:10]
        
        # Criar nome do arquivo
        nome_limpo = dados_candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
        import re
        nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
        data_criacao = datetime.now().strftime('%d%m%Y')
        nome_arquivo = f"{nome_limpo}-{data_criacao}.pdf"
        
        # Preparar contexto para template
        context = {
            'nome': dados_candidato.get('nome_completo', 'Não informado'),
            'cpf': dados_candidato.get('cpf', 'Não informado'),
            'telefone': dados_candidato.get('telefone', 'Não informado'),
            'whatsapp': dados_candidato.get('whatsapp', ''),
            'email': dados_candidato.get('email', 'Não informado'),
            'endereco': dados_candidato.get('endereco', 'Não informado'),
            'funcao': formatar_funcao_display(dados_candidato.get('formulario_id', '')),
            'data_cadastro': data_cadastro,
            'data_geracao': datetime.now().strftime('%d/%m/%Y às %H:%M'),
            'dados_candidato': dados_candidato,
            'dados_especificos': dados_especificos,
            'referencias': referencias,
            'observacoes': dados_candidato.get('observacoes_adicionais', 'Nenhuma observação')
        }
        
        # Renderizar HTML
        html_content = render_html('ficha_weasyprint.html', context)
        
        # Configurar fontes
        font_config = FontConfiguration()
        
        # Gerar PDF usando WeasyPrint
        html_doc = HTML(string=html_content)
        css_doc = CSS(string=gerar_css_customizado())
        
        # Gerar PDF em bytes
        pdf_bytes = html_doc.write_pdf(
            stylesheets=[css_doc],
            font_config=font_config
        )
        
        print(f"✅ PDF gerado com sucesso!")
        print(f"📄 Tamanho: {len(pdf_bytes)} bytes")
        print(f"📂 Nome do arquivo: {nome_arquivo}")
        
        return pdf_bytes, nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback simples usando ReportLab
        print("🔄 Tentando fallback com ReportLab...")
        return gerar_pdf_fallback_reportlab(dados_candidato)

def gerar_pdf_fallback_reportlab(dados_candidato):
    """
    Fallback usando ReportLab para casos de erro
    """
    try:
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        # Cabeçalho
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, 750, "R.O RECRUTAMENTO - FICHA PROFISSIONAL")
        
        # Dados básicos
        p.setFont("Helvetica", 12)
        y = 700
        
        dados_basicos = [
            f"Nome: {dados_candidato.get('nome_completo', 'Não informado')}",
            f"CPF: {dados_candidato.get('cpf', 'Não informado')}",
            f"Telefone: {dados_candidato.get('telefone', 'Não informado')}",
            f"Email: {dados_candidato.get('email', 'Não informado')}",
            f"Endereço: {dados_candidato.get('endereco', 'Não informado')}",
            f"Função: {formatar_funcao_display(dados_candidato.get('formulario_id', ''))}",
            f"Possui CNH: {'Sim' if dados_candidato.get('possui_cnh') else 'Não'}",
            f"Tem filhos: {'Sim' if dados_candidato.get('tem_filhos') else 'Não'}",
        ]
        
        for linha in dados_basicos:
            p.drawString(50, y, linha)
            y -= 20
        
        # Rodapé
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(50, 50, f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        p.drawString(50, 35, "www.rorecrutamento.com.br")
        
        p.save()
        pdf_bytes = buffer.getvalue()
        
        # Nome do arquivo
        nome_limpo = dados_candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
        import re
        nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
        nome_arquivo = f"{nome_limpo}-fallback.pdf"
        
        print(f"⚠️ PDF fallback gerado com ReportLab")
        return pdf_bytes, nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro crítico no fallback: {e}")
        raise

# Teste da função
if __name__ == "__main__":
    dados_teste = {
        'nome_completo': 'Maria Silva',
        'cpf': '123.456.789-00',
        'telefone': '(11) 99999-9999',
        'whatsapp': '5511999999999',
        'email': 'maria@email.com',
        'endereco': 'Rua das Flores, 123 - São Paulo/SP',
        'formulario_id': 'candi-baba',
        'tem_filhos': True,
        'quantos_filhos': 2,
        'possui_cnh': False,
        'categoria_cnh': None,
        'pretensao_salarial': 2800,
        'aceita_treinamento': True,
        'tempo_experiencia': '3-5-anos',
        'experiencia_alto_padrao': True,
        'possui_referencias': True,
        'dados_especificos': {
            'idades_experiencia': ['0-2-anos', '3-6-anos'],
            'cuidados_especiais': 'intermediario',
            'atividades_pedagogicas': 'sim',
            'nivel_ingles': 'basico',
            'primeiros_socorros': True,
            'natacao': True,
            'disponibilidade_viagens': False
        },
        'referencias': [
            {
                'nome': 'Ana Paula Costa',
                'telefone': '(11) 98888-8888',
                'relacao': 'ex-patrao',
                'periodo_inicio': '2020',
                'periodo_fim': '2023'
            }
        ],
        'observacoes_adicionais': 'Candidata muito dedicada e carinhosa com as crianças'
    }
    
    try:
        pdf_bytes, nome_arquivo = gerar_ficha_candidato_completa(dados_teste)
        with open(f"teste_{nome_arquivo}", "wb") as f:
            f.write(pdf_bytes)
        print(f"✅ PDF de teste salvo como: teste_{nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")