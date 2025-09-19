# backend/pdf_utils.py - VERSÃO COMPLETA COM WEASYPRINT
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


def render_html(template_name, context):
    """
    Renderiza template HTML usando Jinja2
    """
    try:
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        print(f"❌ Erro ao renderizar template {template_name}: {e}")
        raise


def formatar_texto_legivel(texto):
    """Converte texto com hífens/underscores em texto legível"""
    if not texto or texto == "":
        return "Não informado"

    texto_formatado = str(texto).replace("-", " ").replace("_", " ")
    texto_formatado = " ".join(word.capitalize() for word in texto_formatado.split())

    correções = {
        "Cnh": "CNH",
        "Rg": "RG",
        "Cpf": "CPF",
        "Tv": "TV",
        "Dvd": "DVD",
        "Intermediario": "Intermediário",
        "Basico": "Básico",
        "Avancado": "Avançado",
    }

    for termo_errado, termo_correto in correções.items():
        texto_formatado = texto_formatado.replace(termo_errado, termo_correto)

    return texto_formatado


def processar_dados_especificos(dados_especificos, formulario_id):
    """Processa o campo dados_especificos (JSON) baseado no tipo de formulário"""
    try:
        if not dados_especificos:
            return []

        # Parse JSON se for string
        if isinstance(dados_especificos, str):
            dados_especificos = json.loads(dados_especificos)

        dados_processados = []

        # MAPEAMENTO POR TIPO DE FORMULÁRIO
        mapeamentos = {
            "candi-baba": {
                "idades_experiencia": "Idades com Experiência",
                "cuidados_especiais": "Cuidados Especiais",
                "atividades_pedagogicas": "Atividades Pedagógicas",
                "nivel_ingles": "Nível de Inglês",
                "primeiros_socorros": "Primeiros Socorros",
                "natacao": "Sabe Nadar",
                "disponibilidade_viagens": "Disponível para Viagens",
            },
            "candi-caseiro": {
                "manutencao_geral": "Manutenção Geral",
                "jardinagem": "Jardinagem",
                "piscina": "Manutenção de Piscina",
                "eletrica_basica": "Elétrica Básica",
                "encanamento_basico": "Encanamento Básico",
                "seguranca": "Conhecimentos de Segurança",
                "animais_domesticos": "Cuidado com Animais",
            },
            "candi-copeiro": {
                "conhecimento_coqueteis": "Conhecimento em Coquetéis",
                "servico_mesa": "Serviço de Mesa",
                "conhecimento_vinhos": "Conhecimento em Vinhos",
                "experiencia_eventos": "Experiência em Eventos",
                "idiomas_conversacao": "Idiomas para Conversação",
            },
            "candi-motorista": {
                "categoria_cnh": "Categoria da CNH",
                "experiencia_categoria": "Experiência na Categoria",
                "veiculos_grandes": "Conduz Veículos Grandes",
                "conhecimento_mecanica": "Conhecimento em Mecânica",
                "disponibilidade_viagens": "Disponível para Viagens",
                "conhecimento_rotas": "Conhecimento de Rotas",
            },
            "candi-domestica": {
                "tipos_limpeza": "Tipos de Limpeza",
                "organizacao": "Organização",
                "cuidado_roupas": "Cuidado com Roupas",
                "cozinha_basica": "Cozinha Básica",
                "experiencia_casas_grandes": "Experiência em Casas Grandes",
            },
        }

        # Obter mapeamento para o formulário
        mapeamento = mapeamentos.get(formulario_id, {})

        # Processar cada campo
        for campo, valor in dados_especificos.items():
            # Usar mapeamento se existir, senão formatar campo
            nome_campo = mapeamento.get(campo, formatar_texto_legivel(campo))

            # Processar valor
            if isinstance(valor, list):
                # Filtrar itens "None" da lista
                lista_filtrada = [
                    v
                    for v in valor
                    if v and str(v).lower() not in ["none", "null", "nan", ""]
                ]
                if lista_filtrada:  # Só processar se sobrou algo na lista
                    valor_formatado = ", ".join(
                        [formatar_texto_legivel(v) for v in lista_filtrada]
                    )
                else:
                    continue  # Pular este campo se lista vazia
            elif isinstance(valor, bool):
                valor_formatado = "Sim" if valor else "Não"
            else:
                valor_str = str(valor).strip()
                # Filtrar valores indesejados
                if valor_str.lower() in ["none", "null", "nan", "", "não informado"]:
                    continue  # Pular este campo
                valor_formatado = formatar_texto_legivel(valor_str)

            dados_processados.append((nome_campo, valor_formatado))

        return dados_processados

    except Exception as e:
        print(f"Erro ao processar dados específicos: {e}")
        return []


def processar_referencias(referencias):
    """Processa lista de referências"""
    try:
        if not referencias:
            return []

        # Parse JSON se for string
        if isinstance(referencias, str):
            referencias = json.loads(referencias)

        referencias_processadas = []

        for ref in referencias:
            if isinstance(ref, dict):
                referencias_processadas.append(
                    {
                        "nome": ref.get("nome", "Não informado"),
                        "telefone": ref.get("telefone", "Não informado"),
                        "relacao": formatar_texto_legivel(
                            ref.get("relacao", "Não informado")
                        ),
                        "periodo_inicio": ref.get("periodo_inicio", ""),
                        "periodo_fim": ref.get("periodo_fim", ""),
                    }
                )

        return referencias_processadas

    except Exception as e:
        print(f"Erro ao processar referências: {e}")
        return []


def formatar_funcao_display(formulario_id):
    """Converte ID do formulário em nome de função para exibição"""
    mapeamento_funcoes = {
        "candi-baba": "BABÁ",
        "candi-caseiro": "CASEIRO(A)",
        "candi-copeiro": "COPEIRO(A)",
        "candi-motorista": "MOTORISTA",
        "candi-domestica": "DOMÉSTICA",
        "candi-cozinheiro": "COZINHEIRO(A)",
        "candi-jardineiro": "JARDINEIRO(A)",
        "candi-seguranca": "SEGURANÇA",
    }

    return mapeamento_funcoes.get(formulario_id, formatar_texto_legivel(formulario_id))


def gerar_ficha_candidato_completa(dados_candidato):
    """
    Gera PDF completo da ficha do candidato usando WeasyPrint ou ReportLab

    Args:
        dados_candidato (dict): Dicionário com todos os dados do candidato

    Returns:
        tuple: (pdf_bytes, nome_arquivo)
    """
    try:
        print(
            f"📝 Gerando ficha para: {dados_candidato.get('nome_completo', 'Candidato sem nome')}"
        )

        # Processar dados
        dados_especificos = processar_dados_especificos(
            dados_candidato.get("dados_especificos"),
            dados_candidato.get("formulario_id", ""),
        )

        referencias = processar_referencias(dados_candidato.get("referencias", []))

        # Formatar data de cadastro
        data_cadastro = "Não informado"
        if dados_candidato.get("created_at"):
            try:
                data_obj = datetime.fromisoformat(
                    dados_candidato["created_at"].replace("Z", "+00:00")
                )
                data_cadastro = data_obj.strftime("%d/%m/%Y")
            except:
                data_cadastro = str(dados_candidato["created_at"])[:10]

        # Criar nome do arquivo
        nome_limpo = (
            dados_candidato.get("nome_completo", "candidato").replace(" ", "_").lower()
        )
        import re

        nome_limpo = re.sub(r"[^a-zA-Z0-9_]", "", nome_limpo)
        data_criacao = datetime.now().strftime("%d%m%Y")
        nome_arquivo = f"{nome_limpo}-{data_criacao}.pdf"

        # Preparar contexto para template
        context = {
            "nome": dados_candidato.get("nome_completo", "Não informado"),
            "cpf": dados_candidato.get("cpf", "Não informado"),
            "telefone": dados_candidato.get("telefone", "Não informado"),
            "whatsapp": dados_candidato.get("whatsapp", ""),
            "email": dados_candidato.get("email", "Não informado"),
            "endereco": dados_candidato.get("endereco", "Não informado"),
            "funcao": formatar_funcao_display(dados_candidato.get("formulario_id", "")),
            "data_cadastro": data_cadastro,
            "data_geracao": datetime.now().strftime("%d/%m/%Y às %H:%M"),
            "dados_candidato": dados_candidato,
            "dados_especificos": dados_especificos,
            "referencias": referencias,
            "observacoes": dados_candidato.get(
                "observacoes_adicionais", "Nenhuma observação"
            ),
        }

        # Tentar WeasyPrint primeiro
        if WEASYPRINT_AVAILABLE:
            try:
                print("🎨 Usando WeasyPrint com template...")

                # Renderizar HTML usando o template
                html_content = render_html("ficha.html", context)

                # Configurar fontes
                font_config = FontConfiguration()

                # Gerar PDF usando WeasyPrint
                html_doc = HTML(string=html_content)

                # Gerar PDF em bytes
                pdf_bytes = html_doc.write_pdf(font_config=font_config)

                print(f"✅ PDF gerado com WeasyPrint: {len(pdf_bytes)} bytes")
                print(f"📂 Nome do arquivo: {nome_arquivo}")

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
        print(f"❌ Erro ao gerar PDF: {str(e)}")
        import traceback

        traceback.print_exc()
        raise


def gerar_pdf_reportlab(dados_candidato):
    """Gera PDF usando ReportLab (fallback)"""
    buffer = BytesIO()

    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo customizado para cabeçalho
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#a65e2e"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    # Estilo para seções
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#a65e2e"),
        spaceBefore=15,
        spaceAfter=10,
    )

    # Elementos do documento
    elements = []

    # Cabeçalho
    elements.append(Paragraph("R.O RECRUTAMENTO", header_style))
    elements.append(Paragraph("FICHA PROFISSIONAL", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # Nome e função
    nome = dados_candidato.get("nome_completo", "Não informado")
    funcao = formatar_funcao_display(dados_candidato.get("formulario_id", ""))

    elements.append(Paragraph(f"<b>{nome}</b>", styles["Title"]))
    elements.append(Paragraph(f"<b>{funcao}</b>", section_style))
    elements.append(Spacer(1, 15))

    # Dados pessoais
    elements.append(Paragraph("DADOS PESSOAIS", section_style))

    dados_pessoais = [
        ["Nome Completo:", dados_candidato.get("nome_completo", "Não informado")],
        ["CPF:", dados_candidato.get("cpf", "Não informado")],
        ["Telefone:", dados_candidato.get("telefone", "Não informado")],
        ["Email:", dados_candidato.get("email", "Não informado")],
        ["Endereço:", dados_candidato.get("endereco", "Não informado")],
    ]

    table_dados = Table(dados_pessoais, colWidths=[4 * cm, 12 * cm])
    table_dados.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
            ]
        )
    )

    elements.append(table_dados)
    elements.append(Spacer(1, 15))

    # Informações profissionais
    elements.append(Paragraph("INFORMAÇÕES PROFISSIONAIS", section_style))

    dados_profissionais = [
        ["Possui Filhos:", "Sim" if dados_candidato.get("tem_filhos") else "Não"],
        ["Possui CNH:", "Sim" if dados_candidato.get("possui_cnh") else "Não"],
        [
            "Pretensão Salarial:",
            f"R$ {dados_candidato.get('pretensao_salarial', 'Não informado')}",
        ],
        [
            "Aceita Treinamento:",
            "Sim" if dados_candidato.get("aceita_treinamento") else "Não",
        ],
    ]

    table_prof = Table(dados_profissionais, colWidths=[4 * cm, 12 * cm])
    table_prof.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
            ]
        )
    )

    elements.append(table_prof)
    elements.append(Spacer(1, 15))

    # Dados específicos (se houver)
    dados_especificos = processar_dados_especificos(
        dados_candidato.get("dados_especificos"),
        dados_candidato.get("formulario_id", ""),
    )

    if dados_especificos:
        elements.append(Paragraph(f"INFORMAÇÕES ESPECÍFICAS - {funcao}", section_style))

        for nome, valor in dados_especificos:
            elements.append(Paragraph(f"<b>{nome}:</b> {valor}", styles["Normal"]))

        elements.append(Spacer(1, 15))

    # Observações
    observacoes = dados_candidato.get("observacoes_adicionais", "")
    if observacoes and observacoes != "Nenhuma observação":
        elements.append(Paragraph("OBSERVAÇÕES", section_style))
        elements.append(Paragraph(observacoes, styles["Normal"]))
        elements.append(Spacer(1, 15))

    # Rodapé
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Ficha gerada em {data_geracao}", styles["Italic"]))
    elements.append(Paragraph("www.rorecrutamento.com.br", styles["Italic"]))

    # Gerar PDF
    doc.build(elements)
    return buffer.getvalue()


# Teste da função
if __name__ == "__main__":
    dados_teste = {
        "nome_completo": "Maria Silva Santos",
        "cpf": "123.456.789-00",
        "telefone": "(11) 99999-9999",
        "whatsapp": "5511999999999",
        "email": "maria.santos@email.com",
        "endereco": "Rua das Flores, 123 - Jardim Paulista, São Paulo/SP",
        "formulario_id": "candi-baba",
        "tem_filhos": True,
        "quantos_filhos": 2,
        "possui_cnh": False,
        "categoria_cnh": None,
        "pretensao_salarial": 3200,
        "aceita_treinamento": True,
        "tempo_experiencia": "3-5-anos",
        "experiencia_alto_padrao": True,
        "possui_referencias": True,
        "created_at": "2024-01-15T10:30:00Z",
        "dados_especificos": {
            "idades_experiencia": ["0-2-anos", "3-6-anos"],
            "cuidados_especiais": "intermediario",
            "atividades_pedagogicas": "sim",
            "nivel_ingles": "basico",
            "primeiros_socorros": True,
            "natacao": True,
            "disponibilidade_viagens": False,
        },
        "referencias": [
            {
                "nome": "Ana Paula Costa",
                "telefone": "(11) 98888-8888",
                "relacao": "ex-patrao",
                "periodo_inicio": "2021",
                "periodo_fim": "2023",
            }
        ],
        "observacoes_adicionais": "Candidata muito dedicada e carinhosa com as crianças.",
    }

    try:
        pdf_bytes, nome_arquivo = gerar_ficha_candidato_completa(dados_teste)
        with open(f"teste_{nome_arquivo}", "wb") as f:
            f.write(pdf_bytes)
        print(f"✅ PDF de teste salvo como: teste_{nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

# ADICIONAR AO FINAL DO ARQUIVO backend/pdf_utils.py


def formatar_valor(valor, tipo="texto"):
    """Formata valores para exibição"""
    if not valor or valor == "":
        return "Não informado"

    if tipo == "dinheiro":
        try:
            valor_float = float(str(valor).replace(".", "").replace(",", "."))
            return (
                f"{valor_float:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )
        except:
            return str(valor)

    return str(valor)


def processar_beneficios(beneficios_str):
    """Processa string JSON de benefícios em lista"""
    try:
        if not beneficios_str:
            return []

        import json

        if isinstance(beneficios_str, str):
            beneficios = json.loads(beneficios_str)
        else:
            beneficios = beneficios_str

        return beneficios if isinstance(beneficios, list) else []
    except:
        return []


def processar_horario_contato(horario_str):
    """Processa string JSON de horários de contato em lista"""
    try:
        if not horario_str:
            return []

        import json

        if isinstance(horario_str, str):
            horarios = json.loads(horario_str)
        else:
            horarios = horario_str

        return horarios if isinstance(horarios, list) else []
    except:
        return []


def formatar_data_vaga(data_str):
    """Formata data da vaga para exibição"""
    try:
        if not data_str:
            return "Não informado"

        from datetime import datetime

        # Tentar diferentes formatos de data
        formatos = [
            "%Y-%m-%d %H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for formato in formatos:
            try:
                data_obj = datetime.strptime(str(data_str), formato)
                return data_obj.strftime("%d/%m/%Y às %H:%M")
            except:
                continue

        # Se não conseguir parsear, retornar string original
        return str(data_str)[:19]  # Primeiros 19 caracteres
    except:
        return "Não informado"


def gerar_ficha_vaga_completa(dados_vaga):
    """
    Gera PDF completo para vaga usando WeasyPrint
    100% compatível com estrutura real do Supabase
    """
    try:
        print(
            f"Gerando PDF para vaga: {dados_vaga.get('nome', 'Vaga')} {dados_vaga.get('sobrenome', '')}"
        )

        from datetime import datetime as dt_local

        data_atual = dt_local.now()
        data_formatada = data_atual.strftime("%d-%m-%Y")

        # Nome do arquivo
        nome_proprietario = f"{dados_vaga.get('nome', 'vaga')}_{dados_vaga.get('sobrenome', 'proprietario')}"
        nome_limpo = nome_proprietario.replace(" ", "_").lower()
        import re

        nome_limpo = re.sub(r"[^a-zA-Z0-9_]", "", nome_limpo)

        nome_arquivo = f"vaga_{nome_limpo}_{data_formatada}.pdf"

        # Processar dados específicos se existirem
        dados_especificos_processados = {}
        if dados_vaga.get("dados_especificos"):
            try:
                if isinstance(dados_vaga["dados_especificos"], str):
                    import json

                    dados_especificos_raw = json.loads(dados_vaga["dados_especificos"])
                else:
                    dados_especificos_raw = dados_vaga["dados_especificos"]

                # Formatar dados específicos para visualização
                for key, value in dados_especificos_raw.items():
                    if value and value != "":
                        dados_especificos_processados[key] = formatar_texto_legivel(
                            str(value)
                        )

            except Exception as e:
                print(f"Erro ao processar dados específicos: {e}")
                dados_especificos_processados = {}

        # Processar benefícios
        beneficios_list = processar_beneficios(dados_vaga.get("beneficios"))

        # Mapeamento de nomes de benefícios
        beneficio_names = {
            "vale-transporte": "Vale Transporte",
            "vale-alimentacao": "Vale Alimentação",
            "vale-refeicao": "Vale Refeição",
            "plano-saude": "Plano de Saúde",
            "plano-odontologico": "Plano Odontológico",
            "seguro-vida": "Seguro de Vida",
            "13o-salario": "13º Salário",
            "ferias-remuneradas": "Férias Remuneradas",
            "ajuda-custo": "Ajuda de Custo",
            "bonificacao": "Bonificação",
            "comissao": "Comissão",
        }

        # Processar horários de contato
        horario_contato_list = processar_horario_contato(
            dados_vaga.get("horario_contato")
        )

        # Contexto para o template
        context = {
            # Dados básicos
            "id": dados_vaga.get("id", ""),
            "nome": dados_vaga.get("nome", "Não informado"),
            "sobrenome": dados_vaga.get("sobrenome", ""),
            "email": dados_vaga.get("email", "Não informado"),
            "telefone_principal": dados_vaga.get("telefone_principal", "Não informado"),
            "telefone_opcional": dados_vaga.get("telefone_opcional", ""),
            "cidade": dados_vaga.get("cidade", "Não informado"),
            "rua_numero": dados_vaga.get("rua_numero", "Não informado"),
            "condominio": dados_vaga.get("condominio", ""),
            # Tipo e status
            "formulario_id": dados_vaga.get("formulario_id", ""),
            "status": dados_vaga.get("status", "ativa"),
            "status_detalhado": dados_vaga.get(
                "status_detalhado", dados_vaga.get("status", "ativa")
            ),
            # Datas
            "data_geracao": data_atual.strftime("%d/%m/%Y às %H:%M"),
            "created_at_formatted": formatar_data_vaga(dados_vaga.get("created_at")),
            "updated_at_formatted": formatar_data_vaga(dados_vaga.get("updated_at")),
            # Detalhes da vaga
            "salario_oferecido": dados_vaga.get("salario_oferecido", "Não informado"),
            "salario_oferecido_formatado": formatar_valor(
                dados_vaga.get("salario_oferecido"), "dinheiro"
            ),
            "regime_trabalho": dados_vaga.get("regime_trabalho", "Não informado"),
            "inicio_urgente": dados_vaga.get("inicio_urgente", "Não informado"),
            "horario_trabalho": dados_vaga.get("horario_trabalho", "Não informado"),
            "horario_fim_semana": dados_vaga.get("horario_fim_semana", ""),
            "folgas_semana": dados_vaga.get("folgas_semana", ""),
            "fim_semana_mensal_folga": dados_vaga.get("fim_semana_mensal_folga", ""),
            "dormir_trabalho": dados_vaga.get("dormir_trabalho", ""),
            # Requisitos
            "cnh_obrigatoria": dados_vaga.get("cnh_obrigatoria", ""),
            "experiencia_obrigatoria": dados_vaga.get("experiencia_obrigatoria", ""),
            "experiencia_minima": dados_vaga.get("experiencia_minima", ""),
            "tem_idade_minima": dados_vaga.get("tem_idade_minima", False),
            "idade_minima": dados_vaga.get("idade_minima", ""),
            "referencias_obrigatorias": dados_vaga.get("referencias_obrigatorias", ""),
            "interesse_treinamento": dados_vaga.get("interesse_treinamento", ""),
            # Características da residência
            "tipo_residencia": dados_vaga.get("tipo_residencia", ""),
            "tem_pets": dados_vaga.get("tem_pets", False),
            "tipos_pets": dados_vaga.get("tipos_pets", ""),
            "cuidados_pets": dados_vaga.get("cuidados_pets", ""),
            "estilo_casa": dados_vaga.get("estilo_casa", ""),
            "frequencia_veraneio": dados_vaga.get("frequencia_veraneio", ""),
            # Benefícios
            "beneficios": dados_vaga.get("beneficios", ""),
            "beneficios_list": beneficios_list,
            "beneficio_names": beneficio_names,
            "outros_beneficios": dados_vaga.get("outros_beneficios", ""),
            # Observações
            "restricoes_vaga": dados_vaga.get("restricoes_vaga", ""),
            "observacoes": dados_vaga.get("observacoes", ""),
            "observacoes_adicionais": dados_vaga.get("observacoes_adicionais", ""),
            # Contato
            "contato_preferido": dados_vaga.get("contato_preferido", ""),
            "horario_contato": dados_vaga.get("horario_contato", ""),
            "horario_contato_list": horario_contato_list,
            # Dados específicos e outros
            "dados_especificos": dados_especificos_processados,
            "aceita_termos": dados_vaga.get("aceita_termos", False),
            "dados_vaga": dados_vaga,
            "nome_arquivo": nome_arquivo,
        }

        # Gerar HTML usando template de vaga
        html = render_html("ficha_vaga.html", context)

        try:
            # Tentar WeasyPrint primeiro (mesma lógica dos candidatos)
            if WEASYPRINT_AVAILABLE:
                from weasyprint import HTML, CSS
                from weasyprint.text.fonts import FontConfiguration

                font_config = FontConfiguration()

                # CSS adicional para vagas (reutilizando cores da marca)
                css_vaga = CSS(
                    string="""
                    @page {
                        size: A4;
                        margin: 2.5cm;
                        @top-center {
                            content: "R.O RECRUTAMENTO - Ficha de Vaga";
                            font-size: 12px;
                            color: #a65e2e;
                        }
                        @bottom-center {
                            content: "Página " counter(page) " de " counter(pages);
                            font-size: 10px;
                            color: #666;
                        }
                    }
                    
                    body {
                        background: linear-gradient(135deg, #fefefe 0%, #f8f8f8 100%);
                    }
                    
                    .header {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    
                    .status-badge {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    
                    .benefits-list {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                """,
                    font_config=font_config,
                )

                # Gerar PDF com WeasyPrint
                html_doc = HTML(string=html, base_url=TEMPLATE_DIR)
                pdf_bytes = html_doc.write_pdf(
                    stylesheets=[css_vaga], font_config=font_config
                )

                if len(pdf_bytes) < 1000:
                    raise Exception("PDF muito pequeno, usando fallback")

        except Exception as e:
            print(f"ERRO WEASYPRINT: {e}")
            print("Usando fallback para vaga...")

            # Fallback com pdfkit
            try:
                import pdfkit

                options = {
                    "page-size": "A4",
                    "encoding": "UTF-8",
                    "enable-local-file-access": None,
                    "no-outline": None,
                    "margin-top": "2.5cm",
                    "margin-right": "2.5cm",
                    "margin-bottom": "2.5cm",
                    "margin-left": "2.5cm",
                    "print-media-type": None,
                    "disable-smart-shrinking": None,
                }

                pdf_bytes = pdfkit.from_string(html, False, options=options)

                if len(pdf_bytes) < 1000:
                    raise Exception("PDF pdfkit muito pequeno")

            except Exception as e2:
                print(f"ERRO PDFKIT: {e2}")
                print("Usando fallback básico...")
                pdf_bytes = html_to_pdf_fallback_vaga(html, dados_vaga)

        print(f"PDF da vaga gerado com sucesso! Tamanho: {len(pdf_bytes)} bytes")
        print(f"Nome do arquivo: {nome_arquivo}")
        return pdf_bytes, nome_arquivo

    except Exception as e:
        print(f"Erro ao gerar PDF da vaga: {str(e)}")
        import traceback

        traceback.print_exc()
        raise


def html_to_pdf_fallback_vaga(html, dados_vaga=None):
    """
    Fallback básico para PDF de vaga usando ReportLab
    Reutiliza padrão dos candidatos adaptado para vagas
    """
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Cabeçalho
    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0.65, 0.37, 0.18)  # Cor da marca #a65e2e
    p.drawString(50, 750, "FICHA DE VAGA - R.O RECRUTAMENTO")

    if dados_vaga:
        p.setFillColorRGB(0, 0, 0)  # Voltar para preto
        p.setFont("Helvetica", 12)
        y = 700

        # Dados básicos da vaga
        p.drawString(
            50,
            y,
            f"Proprietário: {dados_vaga.get('nome', '')} {dados_vaga.get('sobrenome', '')}",
        )
        y -= 20
        p.drawString(50, y, f"Email: {dados_vaga.get('email', 'Não informado')}")
        y -= 20
        p.drawString(
            50, y, f"Telefone: {dados_vaga.get('telefone_principal', 'Não informado')}"
        )
        y -= 20
        p.drawString(50, y, f"Cidade: {dados_vaga.get('cidade', 'Não informado')}")
        y -= 30

        # Detalhes da vaga
        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(0.65, 0.37, 0.18)
        p.drawString(50, y, "DETALHES DA VAGA")
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica", 12)
        y -= 25

        p.drawString(
            50,
            y,
            f"Função: {dados_vaga.get('formulario_id', '').replace('vaga-', '').title()}",
        )
        y -= 20
        p.drawString(50, y, f"Salário: R$ {dados_vaga.get('salario_oferecido', 'N/A')}")
        y -= 20
        p.drawString(
            50, y, f"Regime: {dados_vaga.get('regime_trabalho', 'Não informado')}"
        )
        y -= 20
        p.drawString(
            50, y, f"Urgência: {dados_vaga.get('inicio_urgente', 'Não informado')}"
        )
        y -= 20
        p.drawString(
            50,
            y,
            f"Status: {dados_vaga.get('status_detalhado', dados_vaga.get('status', 'ativa')).upper()}",
        )
        y -= 30

        # Requisitos específicos se existirem
        if dados_vaga.get("dados_especificos"):
            try:
                import json

                dados_esp = (
                    json.loads(dados_vaga["dados_especificos"])
                    if isinstance(dados_vaga["dados_especificos"], str)
                    else dados_vaga["dados_especificos"]
                )

                p.setFont("Helvetica-Bold", 14)
                p.setFillColorRGB(0.65, 0.37, 0.18)
                p.drawString(50, y, "REQUISITOS ESPECÍFICOS")
                p.setFillColorRGB(0, 0, 0)
                p.setFont("Helvetica", 10)
                y -= 20

                for key, value in dados_esp.items():
                    if y < 100:  # Evitar sair da página
                        break
                    p.drawString(50, y, f"• {key.replace('_', ' ').title()}: {value}")
                    y -= 15
            except:
                pass

        # Rodapé
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0.4, 0.4, 0.4)
        p.drawString(50, 50, "R.O RECRUTAMENTO - Sistema de Gestão de Vagas")
        p.drawString(
            50,
            35,
            f"Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        )

    p.save()
    return buffer.getvalue()


# ========================================
# FUNÇÃO AUXILIAR PARA DETECÇÃO DE TEMPLATE
# ========================================


def detectar_template_por_tipo(formulario_id):
    """
    Detecta qual template usar baseado no tipo de formulário
    """
    if formulario_id and formulario_id.startswith("vaga-"):
        return "ficha_vaga.html"
    elif formulario_id and formulario_id.startswith("candi-"):
        return "ficha.html"  # Template original dos candidatos
    else:
        return "ficha.html"  # Default para candidatos


def gerar_ficha_vaga_completa(dados_vaga):
    """
    Gera PDF completo para vaga usando WeasyPrint
    100% compatível com estrutura real do Supabase
    """
    try:
        print(
            f"Gerando PDF para vaga: {dados_vaga.get('nome', 'Vaga')} {dados_vaga.get('sobrenome', '')}"
        )

        from datetime import datetime as dt_local

        data_atual = dt_local.now()
        data_formatada = data_atual.strftime("%d-%m-%Y")

        # Nome do arquivo
        nome_proprietario = f"{dados_vaga.get('nome', 'vaga')}_{dados_vaga.get('sobrenome', 'proprietario')}"
        nome_limpo = nome_proprietario.replace(" ", "_").lower()
        import re

        nome_limpo = re.sub(r"[^a-zA-Z0-9_]", "", nome_limpo)

        nome_arquivo = f"vaga_{nome_limpo}_{data_formatada}.pdf"

        # Processar dados específicos se existirem
        dados_especificos_processados = {}
        if dados_vaga.get("dados_especificos"):
            try:
                if isinstance(dados_vaga["dados_especificos"], str):
                    import json

                    dados_especificos_raw = json.loads(dados_vaga["dados_especificos"])
                else:
                    dados_especificos_raw = dados_vaga["dados_especificos"]

                # Formatar dados específicos para visualização
                for key, value in dados_especificos_raw.items():
                    if value and value != "":
                        dados_especificos_processados[key] = formatar_texto_legivel(
                            str(value)
                        )

            except Exception as e:
                print(f"Erro ao processar dados específicos: {e}")
                dados_especificos_processados = {}

        # Contexto para o template
        context = {
            "nome": dados_vaga.get("nome", "Não informado"),
            "sobrenome": dados_vaga.get("sobrenome", ""),
            "email": dados_vaga.get("email", "Não informado"),
            "telefone_principal": dados_vaga.get("telefone_principal", "Não informado"),
            "telefone_opcional": dados_vaga.get("telefone_opcional", ""),
            "cidade": dados_vaga.get("cidade", "Não informado"),
            "rua_numero": dados_vaga.get("rua_numero", "Não informado"),
            "condominio": dados_vaga.get("condominio", ""),
            "formulario_id": dados_vaga.get("formulario_id", ""),
            "status_detalhado": dados_vaga.get(
                "status_detalhado", dados_vaga.get("status", "ativa")
            ),
            "data_geracao": data_atual.strftime("%d/%m/%Y às %H:%M"),
            "salario_oferecido": formatar_valor(
                dados_vaga.get("salario_oferecido"), "dinheiro"
            ),
            "regime_trabalho": dados_vaga.get("regime_trabalho", "Não informado"),
            "inicio_urgente": dados_vaga.get("inicio_urgente", "Não informado"),
            "horario_trabalho": dados_vaga.get("horario_trabalho", "Não informado"),
            "horario_fim_semana": dados_vaga.get("horario_fim_semana", ""),
            "folgas_semana": dados_vaga.get("folgas_semana", ""),
            "dormir_trabalho": dados_vaga.get("dormir_trabalho", ""),
            "cnh_obrigatoria": dados_vaga.get("cnh_obrigatoria", ""),
            "experiencia_obrigatoria": dados_vaga.get("experiencia_obrigatoria", ""),
            "experiencia_minima": dados_vaga.get("experiencia_minima", ""),
            "tipo_residencia": dados_vaga.get("tipo_residencia", ""),
            "tem_pets": dados_vaga.get("tem_pets", ""),
            "tipos_pets": dados_vaga.get("tipos_pets", ""),
            "cuidados_pets": dados_vaga.get("cuidados_pets", ""),
            "estilo_casa": dados_vaga.get("estilo_casa", ""),
            "frequencia_veraneio": dados_vaga.get("frequencia_veraneio", ""),
            "dados_especificos": dados_especificos_processados,
            "observacoes": dados_vaga.get("observacoes", ""),
            "dados_vaga": dados_vaga,
            "nome_arquivo": nome_arquivo,
        }

        # Gerar HTML usando template de vaga
        html = render_html("ficha_vaga.html", context)

        # Usar WeasyPrint se disponível
        if WEASYPRINT_AVAILABLE:
            try:
                from weasyprint import HTML, CSS
                from weasyprint.text.fonts import FontConfiguration

                font_config = FontConfiguration()
                html_doc = HTML(string=html, base_url=TEMPLATE_DIR)
                pdf_bytes = html_doc.write_pdf(font_config=font_config)

                if len(pdf_bytes) < 1000:
                    raise Exception("PDF muito pequeno")

            except Exception as e:
                print(f"ERRO WEASYPRINT: {e}")
                # Fallback simples
                pdf_bytes = gerar_pdf_simples_vaga(dados_vaga)
        else:
            # Fallback simples se WeasyPrint não disponível
            pdf_bytes = gerar_pdf_simples_vaga(dados_vaga)

        print(f"PDF da vaga gerado com sucesso! Tamanho: {len(pdf_bytes)} bytes")
        print(f"Nome do arquivo: {nome_arquivo}")
        return pdf_bytes, nome_arquivo

    except Exception as e:
        print(f"Erro ao gerar PDF da vaga: {str(e)}")
        import traceback

        traceback.print_exc()
        raise


def gerar_pdf_simples_vaga(dados_vaga):
    """Fallback simples para PDF de vaga"""
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Cabeçalho
    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0.65, 0.37, 0.18)
    p.drawString(50, 750, "FICHA DE VAGA - R.O RECRUTAMENTO")

    # Dados básicos
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 12)
    y = 700

    p.drawString(
        50,
        y,
        f"Proprietário: {dados_vaga.get('nome', '')} {dados_vaga.get('sobrenome', '')}",
    )
    y -= 20
    p.drawString(50, y, f"Email: {dados_vaga.get('email', 'Não informado')}")
    y -= 20
    p.drawString(
        50, y, f"Telefone: {dados_vaga.get('telefone_principal', 'Não informado')}"
    )
    y -= 20
    p.drawString(50, y, f"Cidade: {dados_vaga.get('cidade', 'Não informado')}")
    y -= 30

    # Detalhes da vaga
    p.setFont("Helvetica-Bold", 14)
    p.setFillColorRGB(0.65, 0.37, 0.18)
    p.drawString(50, y, "DETALHES DA VAGA")
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 12)
    y -= 25

    p.drawString(
        50,
        y,
        f"Função: {dados_vaga.get('formulario_id', '').replace('vaga-', '').title()}",
    )
    y -= 20
    p.drawString(50, y, f"Salário: R$ {dados_vaga.get('salario_oferecido', 'N/A')}")
    y -= 20
    p.drawString(50, y, f"Regime: {dados_vaga.get('regime_trabalho', 'Não informado')}")
    y -= 20
    p.drawString(
        50, y, f"Urgência: {dados_vaga.get('inicio_urgente', 'Não informado')}"
    )

    p.save()
    return buffer.getvalue()


def detectar_template_por_tipo(formulario_id):
    """Detecta qual template usar baseado no tipo de formulário"""
    if formulario_id and formulario_id.startswith("vaga-"):
        return "ficha_vaga.html"
    elif formulario_id and formulario_id.startswith("candi-"):
        return "ficha.html"
    else:
        return "ficha.html"


def html_to_pdf_fallback_vaga(html, dados_vaga=None):
    """
    Fallback básico para PDF de vaga usando ReportLab
    Reutiliza padrão dos candidatos adaptado para vagas
    """
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Cabeçalho
    p.setFont("Helvetica-Bold", 20)
    p.setFillColorRGB(0.65, 0.37, 0.18)  # Cor da marca #a65e2e
    p.drawString(50, 750, "FICHA DE VAGA - R.O RECRUTAMENTO")

    if dados_vaga:
        p.setFillColorRGB(0, 0, 0)  # Voltar para preto
        p.setFont("Helvetica", 12)
        y = 700

        # Dados básicos da vaga
        p.drawString(
            50,
            y,
            f"Proprietário: {dados_vaga.get('nome', '')} {dados_vaga.get('sobrenome', '')}",
        )
        y -= 20
        p.drawString(50, y, f"Email: {dados_vaga.get('email', 'Não informado')}")
        y -= 20
        p.drawString(
            50, y, f"Telefone: {dados_vaga.get('telefone_principal', 'Não informado')}"
        )
        y -= 20
        p.drawString(50, y, f"Cidade: {dados_vaga.get('cidade', 'Não informado')}")
        y -= 30

        # Detalhes da vaga
        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(0.65, 0.37, 0.18)
        p.drawString(50, y, "DETALHES DA VAGA")
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica", 12)
        y -= 25

        p.drawString(
            50,
            y,
            f"Função: {dados_vaga.get('formulario_id', '').replace('vaga-', '').title()}",
        )
        y -= 20
        p.drawString(50, y, f"Salário: R$ {dados_vaga.get('salario_oferecido', 'N/A')}")
        y -= 20
        p.drawString(
            50, y, f"Regime: {dados_vaga.get('regime_trabalho', 'Não informado')}"
        )
        y -= 20
        p.drawString(
            50, y, f"Urgência: {dados_vaga.get('inicio_urgente', 'Não informado')}"
        )
        y -= 20
        p.drawString(
            50, y, f"Status: {dados_vaga.get('status_detalhado', 'ativa').upper()}"
        )
        y -= 30

        # Rodapé
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0.4, 0.4, 0.4)
        p.drawString(50, 50, "R.O RECRUTAMENTO - Sistema de Gestão de Vagas")
        p.drawString(
            50,
            35,
            f"Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        )

    p.save()
    return buffer.getvalue()


# ========================================
# FUNÇÃO AUXILIAR PARA DETECÇÃO DE TEMPLATE
# ========================================


def detectar_template_por_tipo(formulario_id):
    """
    Detecta qual template usar baseado no tipo de formulário
    """
    if formulario_id and formulario_id.startswith("vaga-"):
        return "ficha_vaga.html"
    elif formulario_id and formulario_id.startswith("candi-"):
        return "ficha.html"  # Template original dos candidatos
    else:
        return "ficha.html"  # Default para candidatos
