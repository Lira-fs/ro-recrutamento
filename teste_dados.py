# teste_dados.py
import sys
sys.path.append('backend')
from pdf_utils import render_html

dados_teste = {
    'nome_completo': 'Adriana de Almeida Gomes Teste',
    'cpf': '003.887.101-79',
    'telefone': '(11) 97219-6794',
    'email': '010778gomes@gmail.com',
    'endereco': 'Estrada Arlindo Torcato, 123'
}

context = {
    'nome': dados_teste['nome_completo'],
    'cpf': dados_teste['cpf'], 
    'telefone': dados_teste['telefone'],
    'email': dados_teste['email'],
    'endereco': dados_teste['endereco'],
    'dados_candidato': dados_teste,
    'funcao': 'DOMESTICA',
    'data_cadastro': '11/09/2025',
    'data_geracao': '11/09/2025',
    'dados_especificos': [],
    'referencias': [],
    'observacoes': 'Teste'
}

print('DADOS SENDO PASSADOS:')
for key, value in context.items():
    if key != 'dados_candidato':
        print(f'{key}: "{value}"')

try:
    html = render_html('ficha.html', context)
    
    # Salvar HTML para inspeção
    with open('debug_template.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print('HTML gerado salvo em debug_template.html')
    print('Verifique se as variáveis estão sendo substituídas corretamente')
    
except Exception as e:
    print(f'Erro: {e}')