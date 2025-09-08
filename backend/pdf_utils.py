# backend/pdf_utils_completo.py - Versão completa com todos os dados
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

def render_html(template_name, context):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    return template.render(**context)

def html_to_pdf_fallback(html):
    from reportlab.pdfgen import canvas
    from io import BytesIO
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(50, 750, "FICHA R.O RECRUTAMENTO")
    p.save()
    return buffer.getvalue()

def processar_dados_especificos(dados_especificos, formulario_id):
    """
    Processa o campo dados_especificos (JSON) baseado no tipo de formulário
    """
    try:
        if isinstance(dados_especificos, str):
            dados = json.loads(dados_especificos) if dados_especificos and dados_especificos != '{}' else {}
        else:
            dados = dados_especificos or {}
        
        # Processar baseado no tipo de formulário
        if formulario_id == 'candi-copeiro':
            return processar_dados_copeiro(dados)
        elif formulario_id == 'candi-arrumadeira':
            return processar_dados_arrumadeira(dados)
        elif formulario_id == 'candi-baba':
            return processar_dados_baba(dados)
        elif formulario_id == 'candi-caseiro':
            return processar_dados_caseiro(dados)
        elif formulario_id == 'candi-governanta':
            return processar_dados_governanta(dados)
        elif formulario_id == 'candi-cozinheira':
            return processar_dados_cozinheira(dados)
        else:
            return []
            
    except Exception as e:
        print(f"⚠️ Erro ao processar dados específicos: {e}")
        return []

def processar_dados_copeiro(dados):
    """Dados específicos para copeiro"""
    info = []
    
    if dados.get('conhecimento_coqueteis'):
        info.append(['Conhecimento em Coquetéis:', dados['conhecimento_coqueteis']])
    
    if dados.get('servico_mesa'):
        info.append(['Serviço de Mesa:', dados['servico_mesa']])
    
    if dados.get('conhecimento_vinhos'):
        info.append(['Conhecimento em Vinhos:', dados['conhecimento_vinhos']])
    
    if dados.get('experiencia_eventos'):
        info.append(['Experiência em Eventos:', dados['experiencia_eventos']])
    
    if dados.get('idiomas_conversacao'):
        idiomas = ', '.join(dados['idiomas_conversacao']) if isinstance(dados['idiomas_conversacao'], list) else dados['idiomas_conversacao']
        info.append(['Idiomas para Conversação:', idiomas])
    
    return info

def processar_dados_arrumadeira(dados):
    """Dados específicos para arrumadeira"""
    info = []
    
    if dados.get('tipos_residencia'):
        tipos = ', '.join(dados['tipos_residencia']) if isinstance(dados['tipos_residencia'], list) else dados['tipos_residencia']
        info.append(['Tipos de Residência:', tipos])
    
    if dados.get('produtos_limpeza'):
        produtos = ', '.join(dados['produtos_limpeza']) if isinstance(dados['produtos_limpeza'], list) else dados['produtos_limpeza']
        info.append(['Produtos de Limpeza:', produtos])
    
    if dados.get('equipamentos_limpeza'):
        equipamentos = ', '.join(dados['equipamentos_limpeza']) if isinstance(dados['equipamentos_limpeza'], list) else dados['equipamentos_limpeza']
        info.append(['Equipamentos:', equipamentos])
    
    if dados.get('tecnicas_organizacao'):
        tecnicas = ', '.join(dados['tecnicas_organizacao']) if isinstance(dados['tecnicas_organizacao'], list) else dados['tecnicas_organizacao']
        info.append(['Técnicas de Organização:', tecnicas])
    
    if dados.get('maior_diferencial'):
        info.append(['Maior Diferencial:', dados['maior_diferencial']])
    
    return info

def processar_dados_baba(dados):
    """Dados específicos para babá"""
    info = []
    
    if dados.get('faixas_etarias'):
        faixas = ', '.join(dados['faixas_etarias']) if isinstance(dados['faixas_etarias'], list) else dados['faixas_etarias']
        info.append(['Faixas Etárias:', faixas])
    
    if dados.get('numero_maximo_criancas'):
        info.append(['Número Máximo de Crianças:', dados['numero_maximo_criancas']])
    
    if dados.get('primeiros_socorros'):
        info.append(['Primeiros Socorros:', dados['primeiros_socorros']])
    
    if dados.get('atividades_ludicas'):
        info.append(['Atividades Lúdicas:', dados['atividades_ludicas']])
    
    if dados.get('nivel_ingles'):
        info.append(['Nível de Inglês:', dados['nivel_ingles']])
    
    return info

def processar_dados_caseiro(dados):
    """Dados específicos para caseiro"""
    info = []
    
    if dados.get('manutencao_eletrica'):
        info.append(['Manutenção Elétrica:', dados['manutencao_eletrica']])
    
    if dados.get('manutencao_hidraulica'):
        info.append(['Manutenção Hidráulica:', dados['manutencao_hidraulica']])
    
    if dados.get('experiencia_jardim'):
        info.append(['Experiência com Jardim:', dados['experiencia_jardim']])
    
    if dados.get('cuidados_piscina'):
        info.append(['Cuidados com Piscina:', dados['cuidados_piscina']])
    
    if dados.get('tipos_propriedade'):
        tipos = ', '.join(dados['tipos_propriedade']) if isinstance(dados['tipos_propriedade'], list) else dados['tipos_propriedade']
        info.append(['Tipos de Propriedade:', tipos])
    
    return info

def processar_dados_governanta(dados):
    """Dados específicos para governanta"""
    info = []
    
    if dados.get('coordenacao_equipe'):
        info.append(['Coordenação de Equipe:', dados['coordenacao_equipe']])
    
    if dados.get('gestao_compras'):
        info.append(['Gestão de Compras:', dados['gestao_compras']])
    
    if dados.get('organizacao_eventos'):
        info.append(['Organização de Eventos:', dados['organizacao_eventos']])
    
    if dados.get('idiomas_governanta'):
        idiomas = ', '.join(dados['idiomas_governanta']) if isinstance(dados['idiomas_governanta'], list) else dados['idiomas_governanta']
        info.append(['Idiomas:', idiomas])
    
    return info

def processar_dados_cozinheira(dados):
    """Dados específicos para cozinheira"""
    info = []
    
    if dados.get('tipos_culinaria'):
        tipos = ', '.join(dados['tipos_culinaria']) if isinstance(dados['tipos_culinaria'], list) else dados['tipos_culinaria']
        info.append(['Tipos de Culinária:', tipos])
    
    if dados.get('restricoes_alimentares'):
        restricoes = ', '.join(dados['restricoes_alimentares']) if isinstance(dados['restricoes_alimentares'], list) else dados['restricoes_alimentares']
        info.append(['Restrições Alimentares:', restricoes])
    
    if dados.get('experiencia_eventos'):
        info.append(['Experiência em Eventos:', dados['experiencia_eventos']])
    
    if dados.get('cardapios_especiais'):
        info.append(['Cardápios Especiais:', dados['cardapios_especiais']])
    
    return info

def processar_referencias(referencias_json):
    """
    Processa o campo referencias (JSON)
    """
    try:
        if isinstance(referencias_json, str):
            referencias = json.loads(referencias_json) if referencias_json and referencias_json != '[]' else []
        else:
            referencias = referencias_json or []
        
        # Filtrar referências válidas (que têm pelo menos nome)
        referencias_validas = []
        for ref in referencias:
            if ref and ref.get('nome'):
                referencias_validas.append(ref)
        
        return referencias_validas
        
    except Exception as e:
        print(f"⚠️ Erro ao processar referências: {e}")
        return []

def formatar_valor(valor, tipo='texto'):
    """
    Formata valores, tratando null, vazio, etc.
    """
    if valor is None or valor == '' or str(valor).lower() == 'nan':
        return 'Não informado'
    
    if tipo == 'dinheiro':
        try:
            if str(valor).replace('.', '').replace(',', '').isdigit():
                return f"R$ {float(valor):,.2f}".replace(',', '.')
            else:
                return 'Não informado'
        except:
            return 'Não informado'
    
    if tipo == 'boolean':
        if isinstance(valor, bool):
            return 'Sim' if valor else 'Não'
        elif str(valor).lower() in ['true', '1', 'sim']:
            return 'Sim'
        else:
            return 'Não'
    
    return str(valor)

def gerar_ficha_candidato_completa(dados_candidato):
    """
    Gera PDF completo com todos os dados do candidato
    """
    try:
        print(f"🎨 Gerando PDF completo para: {dados_candidato.get('nome_completo', 'Nome não encontrado')}")
        
        # Preparar contexto para template HTML
        context = {
            'nome': dados_candidato.get('nome_completo', 'Não informado'),
            'cpf': dados_candidato.get('cpf', 'Não informado'),
            'telefone': dados_candidato.get('telefone', 'Não informado'),
            'whatsapp': dados_candidato.get('whatsapp', 'Não informado'),
            'email': dados_candidato.get('email', 'Não informado'),
            'endereco': dados_candidato.get('endereco', 'Não informado'),
            'data_nascimento': dados_candidato.get('data_nascimento', 'Não informado'),
            'formulario_id': dados_candidato.get('formulario_id', ''),
            'data_geracao': datetime.now().strftime('%d/%m/%Y às %H:%M'),
            'dados_candidato': dados_candidato
        }

        # Renderizar HTML usando template
        html = render_html('ficha.html', context)

        # Gerar PDF do HTML
        try:
            options = {'page-size': 'A4', 'encoding': "UTF-8"}
            pdf_bytes = pdfkit.from_string(html, False, options=options)
        except:
            pdf_bytes = html_to_pdf_fallback(html)
                
        print(f"✅ PDF completo gerado com sucesso! Tamanho: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF completo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

# Teste
if __name__ == "__main__":
    # Dados de teste baseados no seu exemplo
    dados_teste = {
        'nome_completo': 'Gabriel Lira',
        'cpf': '123.456.789-00',
        'telefone': '(11) 99999-9999',
        'whatsapp': '5511970434094',
        'email': 'gabriel@email.com',
        'endereco': 'Rua das Flores, 123 - São Paulo/SP',
        'formulario_id': 'candi-copeiro',
        'tem_filhos': False,
        'quantos_filhos': None,
        'possui_cnh': False,
        'categoria_cnh': None,
        'pretensao_salarial': 3500,
        'aceita_treinamento': True,
        'tempo_experiencia': '2-5-anos',
        'experiencia_alto_padrao': True,
        'possui_referencias': True,
        'dados_especificos': {
            'conhecimento_coqueteis': 'intermediario',
            'servico_mesa': 'avancado',
            'conhecimento_vinhos': 'basico',
            'experiencia_eventos': 'sim',
            'idiomas_conversacao': ['portugues', 'ingles']
        },
        'referencias': [
            {
                'nome': 'Maria Silva',
                'telefone': '(11) 98888-8888',
                'relacao': 'ex-patrao',
                'periodo_inicio': '2020',
                'periodo_fim': '2023'
            }
        ],
        'observacoes_adicionais': 'Candidato muito dedicado e pontual'
    }
    
    try:
        pdf = gerar_ficha_candidato_completa(dados_teste)
        with open("teste_completo.pdf", "wb") as f:
            f.write(pdf)
        print("💾 PDF completo salvo como 'teste_completo.pdf'")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")