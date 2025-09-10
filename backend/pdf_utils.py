# backend/pdf_utils.py - VERSÃO COMPLETA CORRIGIDA
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

def html_to_pdf_fallback(html, dados_candidato=None):
    """
    Fallback que cria PDF básico usando ReportLab
    """
    from reportlab.pdfgen import canvas
    from io import BytesIO
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(50, 750, "FICHA R.O RECRUTAMENTO")
    
    if dados_candidato:
        p.drawString(50, 720, f"Nome: {dados_candidato.get('nome_completo', 'Não informado')}")
        p.drawString(50, 700, f"Telefone: {dados_candidato.get('telefone', 'Não informado')}")
        p.drawString(50, 680, f"Email: {dados_candidato.get('email', 'Não informado')}")
    
    p.save()
    return buffer.getvalue()

def formatar_texto_legivel(texto):
    """
    Converte texto com hífens/underscores em texto legível
    """
    if not texto or texto == '':
        return 'Não informado'
    
    texto_formatado = str(texto).replace('-', ' ').replace('_', ' ')
    texto_formatado = ' '.join(word.capitalize() for word in texto_formatado.split())
    
    correções = {
        'Cnh': 'CNH', 'Rg': 'RG', 'Cpf': 'CPF', 'Tv': 'TV', 'Dvd': 'DVD'
    }
    
    for termo_errado, termo_correto in correções.items():
        texto_formatado = texto_formatado.replace(termo_errado, termo_correto)
    
    return texto_formatado

def processar_dados_especificos(dados_especificos, formulario_id):
    """
    Processa o campo dados_especificos (JSON) baseado no tipo de formulário
    """
    try:
        if isinstance(dados_especificos, str):
            dados = json.loads(dados_especificos) if dados_especificos and dados_especificos != '{}' else {}
        else:
            dados = dados_especificos or {}
        
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
        print(f"Erro ao processar dados específicos: {e}")
        return []

def processar_dados_copeiro(dados):
    """Dados específicos para copeiro"""
    info = []
    
    if dados.get('conhecimento_coqueteis'):
        valor = formatar_texto_legivel(dados['conhecimento_coqueteis'])
        info.append(['Conhecimento em Coquetéis:', valor])
    
    if dados.get('servico_mesa'):
        valor = formatar_texto_legivel(dados['servico_mesa'])
        info.append(['Serviço de Mesa:', valor])
    
    if dados.get('conhecimento_vinhos'):
        valor = formatar_texto_legivel(dados['conhecimento_vinhos'])
        info.append(['Conhecimento em Vinhos:', valor])
    
    if dados.get('experiencia_eventos'):
        valor = formatar_texto_legivel(dados['experiencia_eventos'])
        info.append(['Experiência em Eventos:', valor])
    
    if dados.get('idiomas_conversacao'):
        if isinstance(dados['idiomas_conversacao'], list):
            idiomas = ', '.join([formatar_texto_legivel(idioma) for idioma in dados['idiomas_conversacao']])
        else:
            idiomas = formatar_texto_legivel(dados['idiomas_conversacao'])
        info.append(['Idiomas para Conversação:', idiomas])
    
    return info

def processar_dados_arrumadeira(dados):
    """Dados específicos para arrumadeira"""
    info = []
    
    if dados.get('tipos_residencia'):
        if isinstance(dados['tipos_residencia'], list):
            tipos = ', '.join([formatar_texto_legivel(tipo) for tipo in dados['tipos_residencia']])
        else:
            tipos = formatar_texto_legivel(dados['tipos_residencia'])
        info.append(['Tipos de Residência:', tipos])
    
    if dados.get('produtos_limpeza'):
        if isinstance(dados['produtos_limpeza'], list):
            produtos = ', '.join([formatar_texto_legivel(produto) for produto in dados['produtos_limpeza']])
        else:
            produtos = formatar_texto_legivel(dados['produtos_limpeza'])
        info.append(['Produtos de Limpeza:', produtos])
    
    if dados.get('equipamentos_limpeza'):
        if isinstance(dados['equipamentos_limpeza'], list):
            equipamentos = ', '.join([formatar_texto_legivel(equip) for equip in dados['equipamentos_limpeza']])
        else:
            equipamentos = formatar_texto_legivel(dados['equipamentos_limpeza'])
        info.append(['Equipamentos:', equipamentos])
    
    if dados.get('tecnicas_organizacao'):
        if isinstance(dados['tecnicas_organizacao'], list):
            tecnicas = ', '.join([formatar_texto_legivel(tecnica) for tecnica in dados['tecnicas_organizacao']])
        else:
            tecnicas = formatar_texto_legivel(dados['tecnicas_organizacao'])
        info.append(['Técnicas de Organização:', tecnicas])
    
    if dados.get('maior_diferencial'):
        valor = formatar_texto_legivel(dados['maior_diferencial'])
        info.append(['Maior Diferencial:', valor])
    
    return info

def processar_dados_baba(dados):
    """Dados específicos para babá"""
    info = []
    
    if dados.get('faixas_etarias'):
        if isinstance(dados['faixas_etarias'], list):
            faixas = ', '.join([formatar_texto_legivel(faixa) for faixa in dados['faixas_etarias']])
        else:
            faixas = formatar_texto_legivel(dados['faixas_etarias'])
        info.append(['Faixas Etárias:', faixas])
    
    if dados.get('numero_maximo_criancas'):
        info.append(['Número Máximo de Crianças:', str(dados['numero_maximo_criancas'])])
    
    if dados.get('primeiros_socorros'):
        valor = formatar_texto_legivel(dados['primeiros_socorros'])
        info.append(['Primeiros Socorros:', valor])
    
    if dados.get('atividades_ludicas'):
        valor = formatar_texto_legivel(dados['atividades_ludicas'])
        info.append(['Atividades Lúdicas:', valor])
    
    if dados.get('nivel_ingles'):
        valor = formatar_texto_legivel(dados['nivel_ingles'])
        info.append(['Nível de Inglês:', valor])
    
    return info

def processar_dados_caseiro(dados):
    """Dados específicos para caseiro"""
    info = []
    
    if dados.get('manutencao_eletrica'):
        valor = formatar_texto_legivel(dados['manutencao_eletrica'])
        info.append(['Manutenção Elétrica:', valor])
    
    if dados.get('manutencao_hidraulica'):
        valor = formatar_texto_legivel(dados['manutencao_hidraulica'])
        info.append(['Manutenção Hidráulica:', valor])
    
    if dados.get('experiencia_jardim'):
        valor = formatar_texto_legivel(dados['experiencia_jardim'])
        info.append(['Experiência com Jardim:', valor])
    
    if dados.get('cuidados_piscina'):
        valor = formatar_texto_legivel(dados['cuidados_piscina'])
        info.append(['Cuidados com Piscina:', valor])
    
    if dados.get('tipos_propriedade'):
        if isinstance(dados['tipos_propriedade'], list):
            tipos = ', '.join([formatar_texto_legivel(tipo) for tipo in dados['tipos_propriedade']])
        else:
            tipos = formatar_texto_legivel(dados['tipos_propriedade'])
        info.append(['Tipos de Propriedade:', tipos])
    
    return info

def processar_dados_governanta(dados):
    """Dados específicos para governanta"""
    info = []
    
    if dados.get('coordenacao_equipe'):
        valor = formatar_texto_legivel(dados['coordenacao_equipe'])
        info.append(['Coordenação de Equipe:', valor])
    
    if dados.get('gestao_compras'):
        valor = formatar_texto_legivel(dados['gestao_compras'])
        info.append(['Gestão de Compras:', valor])
    
    if dados.get('organizacao_eventos'):
        valor = formatar_texto_legivel(dados['organizacao_eventos'])
        info.append(['Organização de Eventos:', valor])
    
    if dados.get('idiomas_governanta'):
        if isinstance(dados['idiomas_governanta'], list):
            idiomas = ', '.join([formatar_texto_legivel(idioma) for idioma in dados['idiomas_governanta']])
        else:
            idiomas = formatar_texto_legivel(dados['idiomas_governanta'])
        info.append(['Idiomas:', idiomas])
    
    return info

def processar_dados_cozinheira(dados):
    """Dados específicos para cozinheira"""
    info = []
    
    if dados.get('tipos_culinaria'):
        if isinstance(dados['tipos_culinaria'], list):
            tipos = ', '.join([formatar_texto_legivel(tipo) for tipo in dados['tipos_culinaria']])
        else:
            tipos = formatar_texto_legivel(dados['tipos_culinaria'])
        info.append(['Tipos de Culinária:', tipos])
    
    if dados.get('restricoes_alimentares'):
        if isinstance(dados['restricoes_alimentares'], list):
            restricoes = ', '.join([formatar_texto_legivel(restricao) for restricao in dados['restricoes_alimentares']])
        else:
            restricoes = formatar_texto_legivel(dados['restricoes_alimentares'])
        info.append(['Restrições Alimentares:', restricoes])
    
    if dados.get('experiencia_eventos'):
        valor = formatar_texto_legivel(dados['experiencia_eventos'])
        info.append(['Experiência em Eventos:', valor])
    
    if dados.get('cardapios_especiais'):
        valor = formatar_texto_legivel(dados['cardapios_especiais'])
        info.append(['Cardápios Especiais:', valor])
    
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
        
        referencias_validas = []
        for ref in referencias:
            if ref and ref.get('nome'):
                referencias_validas.append(ref)
        
        return referencias_validas
        
    except Exception as e:
        print(f"Erro ao processar referências: {e}")
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
        print(f"Gerando PDF completo para: {dados_candidato.get('nome_completo', 'Nome não encontrado')}")
        
        from datetime import datetime as dt_local
        data_atual = dt_local.now()
        data_formatada = data_atual.strftime('%d-%m-%Y')
        
        nome_limpo = dados_candidato.get('nome_completo', 'candidato').replace(' ', '_').lower()
        import re
        nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '', nome_limpo)
        
        nome_arquivo = f"{nome_limpo}-{data_formatada}.pdf"
        
        context = {
            'nome': dados_candidato.get('nome_completo', 'Não informado'),
            'cpf': dados_candidato.get('cpf', 'Não informado'),
            'telefone': dados_candidato.get('telefone', 'Não informado'),
            'whatsapp': dados_candidato.get('whatsapp', 'Não informado'),
            'email': dados_candidato.get('email', 'Não informado'),
            'endereco': dados_candidato.get('endereco', 'Não informado'),
            'data_nascimento': dados_candidato.get('data_nascimento', 'Não informado'),
            'formulario_id': dados_candidato.get('formulario_id', ''),
            'data_geracao': data_atual.strftime('%d/%m/%Y às %H:%M'),
            'dados_candidato': dados_candidato,
            'nome_arquivo': nome_arquivo,
            'tem_filhos': 'Sim' if dados_candidato.get('tem_filhos') else 'Não',
            'quantos_filhos': dados_candidato.get('quantos_filhos', 'Não informado') if dados_candidato.get('tem_filhos') else 'N/A',
            'possui_cnh': 'Sim' if dados_candidato.get('possui_cnh') else 'Não',
            'categoria_cnh': dados_candidato.get('categoria_cnh', 'Não informado') if dados_candidato.get('possui_cnh') else 'N/A',
            'data_cadastro': dados_candidato.get('created_at', 'Não informado'),
            'dados_especificos': processar_dados_especificos(dados_candidato.get('dados_especificos', {}), dados_candidato.get('formulario_id', '')),
            'referencias': processar_referencias(dados_candidato.get('referencias', [])),
            'observacoes': dados_candidato.get('observacoes_adicionais', 'Nenhuma observação')
        }

        html = render_html('ficha.html', context)

        try:
            options = {
                'page-size': 'A4',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'no-outline': None,
                'margin-top': '2.5cm',
                'margin-right': '2.5cm', 
                'margin-bottom': '2.5cm',
                'margin-left': '2.5cm',
                'print-media-type': None,
                'disable-smart-shrinking': None
            }
            pdf_bytes = pdfkit.from_string(html, False, options=options)
            
            if len(pdf_bytes) < 1000:
                raise Exception("PDF muito pequeno, provável erro no pdfkit")
                
        except Exception as e:
            print(f"ERRO PDFKIT: {e}")
            print("Usando fallback...")
            pdf_bytes = html_to_pdf_fallback(html, dados_candidato)
                
        print(f"PDF completo gerado com sucesso! Tamanho: {len(pdf_bytes)} bytes")
        print(f"Nome do arquivo: {nome_arquivo}")
        return pdf_bytes, nome_arquivo
        
    except Exception as e:
        print(f"Erro ao gerar PDF completo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

# Teste
if __name__ == "__main__":
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
        print("PDF completo salvo como 'teste_completo.pdf'")
    except Exception as e:
        print(f"Erro no teste: {e}")