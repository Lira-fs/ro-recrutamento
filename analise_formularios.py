"""
Analisador de Campos: Formulários vs Banco de Dados
Extrai campos de todos os formulários HTML e compara com estrutura do DB
"""

import re
from pathlib import Path
import json

# ========================================
# ESTRUTURA ATUAL DO BANCO (53 colunas)
# ========================================

COLUNAS_DB = [
    # IDs
    'id', 'formulario_id',
    
    # Dados Pessoais
    'nome_completo', 'data_nascimento', 'cpf', 'rg', 'estado_civil', 'nacionalidade',
    
    # Contato (criptografados)
    'telefone', 'whatsapp', 'email', 'endereco', 'cep', 'cidade',
    
    # CNH
    'possui_cnh', 'categoria_cnh', 'vencimento_cnh',
    
    # Filhos
    'tem_filhos', 'quantos_filhos', 'idades_filhos',
    
    # Treinamento
    'aceita_treinamento', 'turno_treinamento',
    
    # Disponibilidade
    'inicio_imediato', 'data_disponivel', 'eventos_noturnos', 'fim_semana',
    'dormir_fim_semana', 'viagens', 'passaporte', 'vencimento_passaporte',
    
    # Pretensões
    'pretensao_salarial', 'regime_trabalho', 'salario_negociavel',
    
    # Experiência
    'tempo_experiencia', 'experiencia_alto_padrao', 'tempo_alto_padrao',
    'possui_referencias',
    
    # Saúde/Hábitos
    'restricao_saude', 'especificar_restricao', 'fuma', 'consome_alcool',
    'veiculo_proprio', 'tipo_veiculo',
    
    # JSON
    'dados_especificos', 'referencias',
    
    # Controle
    'status', 'observacoes_adicionais', 'created_at', 'updated_at',
    'ficha_emitida', 'data_ficha_gerada'
]

# ========================================
# EXTRATOR DE CAMPOS DOS FORMULÁRIOS
# ========================================

def extrair_campos_html(caminho_arquivo):
    """Extrai todos os campos name= de um formulário HTML"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Regex para capturar name="campo" ou name='campo'
        pattern = r'name=["\']([^"\']+)["\']'
        campos = re.findall(pattern, conteudo)
        
        # Remover duplicatas e ordenar
        return sorted(set(campos))
    
    except Exception as e:
        print(f"❌ Erro ao ler {caminho_arquivo}: {e}")
        return []

def analisar_formularios(pasta_forms):
    """Analisa todos os formulários de candidatos"""
    
    formularios = {
        'baba': 'forms/colab-forms/form-candi-baba.html',
        'caseiro': 'forms/colab-forms/form-candi-caseiro.html',
        'copeiro': 'forms/colab-forms/form-candi-copeiro.html',
        'cozinheira': 'forms/colab-forms/form-candi-cozinheira.html',
        'governanta': 'forms/colab-forms/form-candi-governanta.html',
        'arrumadeira': 'forms/colab-forms/form-candi-arrumadeira.html',
        'casal': 'forms/colab-forms/form-candi-casal.html'
    }
    
    resultados = {}
    todos_campos = set()
    
    for tipo, caminho in formularios.items():
        campos = extrair_campos_html(caminho)
        resultados[tipo] = campos
        todos_campos.update(campos)
        print(f"\n📋 {tipo.upper()}: {len(campos)} campos")
    
    return resultados, todos_campos

# ========================================
# COMPARADOR DB vs FORMS
# ========================================

def comparar_estruturas(campos_forms, colunas_db):
    """Compara campos dos forms com colunas do DB"""
    
    # Converter nomes de campos HTML para snake_case do DB
    def html_to_db(nome):
        """Converte camelCase para snake_case"""
        # nomeCompleto -> nome_completo
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', nome)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    campos_convertidos = {html_to_db(c) for c in campos_forms}
    colunas_set = set(colunas_db)
    
    # Campos que existem nos forms mas NÃO no DB
    faltam_no_db = campos_convertidos - colunas_set
    
    # Colunas que existem no DB mas NÃO nos forms
    sobram_no_db = colunas_set - campos_convertidos
    
    # Campos em comum
    comuns = campos_convertidos & colunas_set
    
    return faltam_no_db, sobram_no_db, comuns

# ========================================
# RELATÓRIO
# ========================================

def gerar_relatorio():
    """Gera relatório completo"""
    
    print("="*60)
    print("📊 ANÁLISE: FORMULÁRIOS vs BANCO DE DADOS")
    print("="*60)
    
    # 1. Analisar formulários
    resultados, todos_campos = analisar_formularios('.')
    
    print(f"\n✅ TOTAL DE CAMPOS ÚNICOS: {len(todos_campos)}")
    print(f"✅ TOTAL DE COLUNAS NO DB: {len(COLUNAS_DB)}")
    
    # 2. Comparar
    faltam, sobram, comuns = comparar_estruturas(todos_campos, COLUNAS_DB)
    
    # 3. Relatório de campos faltando
    print("\n" + "="*60)
    print("🔴 CAMPOS QUE FALTAM NO BANCO DE DADOS")
    print("="*60)
    
    if faltam:
        print(f"\n⚠️ {len(faltam)} campos novos precisam ser adicionados:\n")
        for campo in sorted(faltam):
            print(f"   - {campo}")
    else:
        print("\n✅ Todos os campos dos formulários existem no DB!")
    
    # 4. Relatório de colunas não usadas
    print("\n" + "="*60)
    print("🟡 COLUNAS DO DB NÃO USADAS NOS FORMULÁRIOS")
    print("="*60)
    
    # Filtrar colunas de controle/sistema
    colunas_sistema = {'id', 'created_at', 'updated_at', 'status', 
                       'ficha_emitida', 'data_ficha_gerada', 'observacoes_adicionais',
                       'dados_especificos', 'referencias'}
    
    sobram_filtrado = sobram - colunas_sistema
    
    if sobram_filtrado:
        print(f"\n⚠️ {len(sobram_filtrado)} colunas podem ser removidas:\n")
        for coluna in sorted(sobram_filtrado):
            print(f"   - {coluna}")
    else:
        print("\n✅ Todas as colunas do DB estão sendo usadas!")
    
    # 5. Análise por formulário
    print("\n" + "="*60)
    print("📋 CAMPOS ESPECÍFICOS POR FORMULÁRIO")
    print("="*60)
    
    for tipo, campos in resultados.items():
        # Separar campos universais vs específicos
        universais = {'nomeCompleto', 'email', 'telefone', 'cpf', 'formulario_id'}
        especificos = [c for c in campos if c not in universais]
        
        print(f"\n{tipo.upper()}:")
        print(f"  Total: {len(campos)} campos")
        print(f"  Específicos: {len(especificos)}")
        
        if tipo == 'casal':
            print(f"  ⚠️ CASAL tem estrutura dupla (Ele/Ela)")
    
    # 6. Recomendações
    print("\n" + "="*60)
    print("💡 RECOMENDAÇÕES")
    print("="*60)
    
    print("""
1. CRIAR SQL para adicionar campos novos
2. DECIDIR se remove colunas não usadas (backup antes!)
3. MAPEAR quais campos vão para dados_especificos (JSONB)
4. ATUALIZAR validators.py com novos campos
5. ATUALIZAR encryption.py se houver campos sensíveis novos
    """)
    
    return {
        'faltam_no_db': sorted(faltam),
        'sobram_no_db': sorted(sobram_filtrado),
        'formularios': resultados
    }

# ========================================
# EXECUTAR
# ========================================

if __name__ == "__main__":
    resultado = gerar_relatorio()
    
    # Salvar JSON para análise
    with open('analise_campos.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Análise salva em: analise_campos.json")