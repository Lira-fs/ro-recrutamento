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
        
        # Criar buffer para PDF
        buffer = BytesIO()
        
        # Criar documento
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.7*inch,
            rightMargin=0.7*inch
        )
        
        # Estilos personalizados
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        titulo_style = ParagraphStyle(
            'TituloCustom',
            parent=styles['Title'],
            fontSize=20,
            spaceAfter=10,
            textColor=colors.Color(0.65, 0.37, 0.18),  # Cor bronze
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para nome do candidato
        nome_style = ParagraphStyle(
            'NomeCustom',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.Color(0.17, 0.24, 0.31),  # Azul escuro
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para seções
        secao_style = ParagraphStyle(
            'SecaoCustom',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.Color(0.65, 0.37, 0.18),  # Cor bronze
            fontName='Helvetica-Bold'
        )
        
        # Conteúdo do PDF
        story = []
        
        # CABEÇALHO ESTILIZADO
        titulo = Paragraph("R.O RECRUTAMENTO", titulo_style)
        story.append(titulo)
        
        subtitulo = Paragraph(
            "<i>Agência de Profissionais Domésticos Qualificados</i>", 
            styles['Normal']
        )
        subtitulo.alignment = TA_CENTER
        story.append(subtitulo)
        story.append(Spacer(1, 20))
        
        # LINHA DECORATIVA
        linha_dados = [['', '']]
        linha_table = Table(linha_dados, colWidths=[6*inch, 0.5*inch])
        linha_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 3, colors.Color(0.65, 0.37, 0.18)),
        ]))
        story.append(linha_table)
        story.append(Spacer(1, 10))
        
        # NOME DO CANDIDATO DESTACADO
        nome = formatar_valor(dados_candidato.get('nome_completo'))
        nome_principal = Paragraph(nome, nome_style)
        story.append(nome_principal)
        
        # Badge da função
        funcao_map = {
            'candi-baba': '👶 BABÁ',
            'candi-caseiro': '🏠 CASEIRO', 
            'candi-copeiro': '🍷 COPEIRO',
            'candi-cozinheira': '👨‍🍳 COZINHEIRA(O)',
            'candi-governanta': '👑 GOVERNANTA',
            'candi-arrumadeira': '🧹 ARRUMADEIRA',
            'candi-casal': '👫 CASAL'
        }
        
        funcao = funcao_map.get(dados_candidato.get('formulario_id', ''), 'PROFISSIONAL')
        badge_funcao = Paragraph(f"<b>{funcao}</b>", styles['Normal'])
        badge_funcao.alignment = TA_CENTER
        story.append(badge_funcao)
        story.append(Spacer(1, 25))
        
        # SEÇÃO: DADOS PESSOAIS
        secao_pessoais = Paragraph("📋 DADOS PESSOAIS", secao_style)
        story.append(secao_pessoais)
        
        dados_pessoais = [
            ['Nome Completo:', formatar_valor(dados_candidato.get('nome_completo'))],
            ['CPF:', formatar_valor(dados_candidato.get('cpf'))],
            ['RG:', formatar_valor(dados_candidato.get('rg'))],
            ['Data de Nascimento:', formatar_valor(dados_candidato.get('data_nascimento'))],
            ['Estado Civil:', formatar_valor(dados_candidato.get('estado_civil'))],
            ['Nacionalidade:', formatar_valor(dados_candidato.get('nacionalidade', 'Brasileira'))],
        ]
        
        tabela_dados = Table(dados_pessoais, colWidths=[2.2*inch, 4*inch])
        tabela_dados.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8))
        ]))
        
        story.append(tabela_dados)
        story.append(Spacer(1, 20))
        
        # SEÇÃO: CONTATO
        secao_contato = Paragraph("📞 INFORMAÇÕES DE CONTATO", secao_style)
        story.append(secao_contato)
        
        contato_dados = [
            ['Telefone:', formatar_valor(dados_candidato.get('telefone'))],
            ['WhatsApp:', formatar_valor(dados_candidato.get('whatsapp'))],
            ['Email:', formatar_valor(dados_candidato.get('email'))],
        ]
        
        tabela_contato = Table(contato_dados, colWidths=[2.2*inch, 4*inch])
        tabela_contato.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8))
        ]))
        
        story.append(tabela_contato)
        story.append(Spacer(1, 20))
        
        # SEÇÃO: ENDEREÇO
        secao_endereco = Paragraph("📍 ENDEREÇO", secao_style)
        story.append(secao_endereco)
        
        endereco_dados = [
            ['Endereço Completo:', formatar_valor(dados_candidato.get('endereco'))],
            ['CEP:', formatar_valor(dados_candidato.get('cep'))],
            ['Cidade:', formatar_valor(dados_candidato.get('cidade'))],
        ]
        
        tabela_endereco = Table(endereco_dados, colWidths=[2.2*inch, 4*inch])
        tabela_endereco.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8))
        ]))
        
        story.append(tabela_endereco)
        story.append(Spacer(1, 20))
        
        # SEÇÃO: INFORMAÇÕES PROFISSIONAIS
        secao_prof = Paragraph("💼 INFORMAÇÕES PROFISSIONAIS", secao_style)
        story.append(secao_prof)
        
        info_profissional = [
            ['Função:', funcao],
            ['Data de Cadastro:', dados_candidato.get('created_at', 'Não informado')[:10] if dados_candidato.get('created_at') else 'Não informado'],
            ['Tem Filhos:', formatar_valor(dados_candidato.get('tem_filhos'), 'boolean')],
            ['Quantidade de Filhos:', formatar_valor(dados_candidato.get('quantos_filhos'))],
            ['Possui CNH:', formatar_valor(dados_candidato.get('possui_cnh'), 'boolean')],
            ['Categoria CNH:', formatar_valor(dados_candidato.get('categoria_cnh'))],
            ['Pretensão Salarial:', formatar_valor(dados_candidato.get('pretensao_salarial'), 'dinheiro')],
            ['Aceita Treinamento:', formatar_valor(dados_candidato.get('aceita_treinamento'), 'boolean')],
            ['Tempo de Experiência:', formatar_valor(dados_candidato.get('tempo_experiencia'))],
            ['Experiência Alto Padrão:', formatar_valor(dados_candidato.get('experiencia_alto_padrao'), 'boolean')],
            ['Possui Referências:', formatar_valor(dados_candidato.get('possui_referencias'), 'boolean')],
        ]
        
        tabela_prof = Table(info_profissional, colWidths=[2.2*inch, 4*inch])
        tabela_prof.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8))
        ]))
        
        story.append(tabela_prof)
        story.append(Spacer(1, 20))
        
        # SEÇÃO: DADOS ESPECÍFICOS POR FUNÇÃO
        dados_especificos = processar_dados_especificos(
            dados_candidato.get('dados_especificos', '{}'), 
            dados_candidato.get('formulario_id', '')
        )
        
        if dados_especificos:
            secao_especificos = Paragraph("🎯 INFORMAÇÕES ESPECÍFICAS DA FUNÇÃO", secao_style)
            story.append(secao_especificos)
            
            tabela_especificos = Table(dados_especificos, colWidths=[2.2*inch, 4*inch])
            tabela_especificos.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.98, 0.95)),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.7, 0.9, 0.7))
            ]))
            
            story.append(tabela_especificos)
            story.append(Spacer(1, 20))
        
        # SEÇÃO: REFERÊNCIAS PROFISSIONAIS
        referencias = processar_referencias(dados_candidato.get('referencias', '[]'))
        
        if referencias:
            secao_ref = Paragraph("📞 REFERÊNCIAS PROFISSIONAIS", secao_style)
            story.append(secao_ref)
            
            for i, ref in enumerate(referencias[:3]):  # Máximo 3 referências
                ref_dados = [
                    [f'Referência {i+1}:', formatar_valor(ref.get('nome'))],
                    ['Telefone:', formatar_valor(ref.get('telefone'))],
                    ['Relação:', formatar_valor(ref.get('relacao'))],
                ]
                
                if ref.get('periodo_inicio') or ref.get('periodo_fim'):
                    periodo_inicio = formatar_valor(ref.get('periodo_inicio', ''))
                    periodo_fim = formatar_valor(ref.get('periodo_fim', 'atual'))
                    periodo = f"{periodo_inicio} até {periodo_fim}"
                    ref_dados.append(['Período:', periodo])
                
                tabela_ref = Table(ref_dados, colWidths=[2.2*inch, 4*inch])
                tabela_ref.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.98, 0.95)),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.7, 0.9, 0.7))
                ]))
                
                story.append(tabela_ref)
                story.append(Spacer(1, 10))
        
        # OBSERVAÇÕES ADICIONAIS
        if dados_candidato.get('observacoes_adicionais'):
            secao_obs = Paragraph("📝 OBSERVAÇÕES ADICIONAIS", secao_style)
            story.append(secao_obs)
            
            obs_dados = [
                ['Observações:', formatar_valor(dados_candidato.get('observacoes_adicionais'))]
            ]
            
            tabela_obs = Table(obs_dados, colWidths=[2.2*inch, 4*inch])
            tabela_obs.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(1, 0.98, 0.94)),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.9, 0.8, 0.6))
            ]))
            
            story.append(tabela_obs)
            story.append(Spacer(1, 20))
        
        # NOVA PÁGINA PARA RODAPÉ
        story.append(Spacer(1, 50))
        
        # LINHA DECORATIVA FINAL
        linha_final = Table([['', '']], colWidths=[6*inch, 0.5*inch])
        linha_final.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.Color(0.65, 0.37, 0.18)),
        ]))
        story.append(linha_final)
        story.append(Spacer(1, 15))
        
        # RODAPÉ ESTILIZADO
        rodape_style = ParagraphStyle(
            'RodapeCustom',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.Color(0.4, 0.4, 0.4)
        )
        
        rodape = Paragraph(
            f"<b>R.O RECRUTAMENTO</b><br/>"
            f"📱 WhatsApp: (11) 95107-2131 | 🌐 www.rorecrutamento.com.br<br/>"
            f"📄 Ficha gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/><br/>"
            f"<i>Este documento contém informações confidenciais do candidato.<br/>"
            f"Uso restrito para processo seletivo - Não compartilhar.</i>",
            rodape_style
        )
        story.append(rodape)
        
        # Gerar PDF
        doc.build(story)
        
        # Obter bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
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