const CONFIG_TITULOS = {
    
    // CANDIDATOS
    'candi-baba': {
        funcao: 'Babá',
        titulo_principal: 'Formulário para cadastro de candidato: Babá',
        titulo_experiencia: 'Babá',
        icone: 'fa-baby-carriage'
    },
    'candi-caseiro': {
        funcao: 'Caseiro(a)',
        titulo_principal: 'Formulário para cadastro de candidato: Caseiro(a)',
        titulo_experiencia: 'Caseiro(a)',
        icone: 'fa-home'
    },
    'candi-cozinheira': {
        funcao: 'Cozinheira(o)',
        titulo_principal: 'Formulário para cadastro de candidato: Cozinheira(o)',
        titulo_experiencia: 'Cozinheira(o)',
        icone: 'fa-utensils'
    },
    'candi-copeiro': {
        funcao: 'Copeiro(a)',
        titulo_principal: 'Formulário para cadastro de candidato: Copeiro(a)',
        titulo_experiencia: 'Copeiro(a)',
        icone: 'fa-coffee'
    },
    'candi-arrumadeira': {
        funcao: 'Arrumadeira',
        titulo_principal: 'Formulário para cadastro de candidato: Arrumadeira',
        titulo_experiencia: 'Arrumadeira',
        icone: 'fa-broom'
    },
    'candi-governanta': {
        funcao: 'Governanta',
        titulo_principal: 'Formulário para cadastro de candidata: Governanta',
        titulo_experiencia: 'Governanta',
        icone: 'fa-users'
    },
    'candi-casal': {
        funcao: 'Casal',
        titulo_principal: 'Formulário para cadastro de candidato: Casal Caseiros',
        titulo_experiencia: 'Casal Caseiros',
        icone: 'fa-users'
    },

    //vagas 

    'vaga-baba': {
        funcao: 'Babá',
        titulo_principal: 'Formulário para cadastro de vaga: Babá',
        titulo_experiencia: 'Babá',
        icone: 'fa-baby-carriage'
    },
    'vaga-caseiro': {
        funcao: 'Caseiro(a)',
        titulo_principal: 'Formulário para cadastro de vaga: Caseiro(a)',
        titulo_experiencia: 'Caseiro(a)',
        icone: 'fa-home'
    },
    'vaga-cozinheira': {
        funcao: 'Cozinheira(o)',
        titulo_principal: 'Formulário para cadastro de vaga: Cozinheira(o)',
        titulo_experiencia: 'Cozinheira(o)',
        icone: 'fa-utensils'
    },
    'vaga-copeiro': {
        funcao: 'Copeiro(a)',
        titulo_principal: 'Formulário para cadasto de vaga: Copeiro(a)',
        titulo_experiencia: 'Copeiro(a)',
        icone: 'fa-coffee'
    },
    'vaga-arrumadeira': {
        funcao: 'Arrumadeira',
        titulo_principal: 'Formulário para cadastro de vaga: Arrumadeira',
        titulo_experiencia: 'Arrumadeira',
        icone: 'fa-broom'
    },
    'vaga-casal': {
        funcao: 'Casal',
        titulo_principal: 'Formulário para cadastro de vaga: Casal',
        titulo_experiencia: 'Casal',
        icone: 'fa-users'
    },
    'vaga-governanta': {
        funcao: 'Governanta',
        titulo_principal: 'Formulário para cadastro de vaga: Governanta',
        titulo_experiencia: 'Governanta',
        icone: 'fa-users'
    }
};

/**
 * Obtém o tipo de formulário atual pela URL ou input hidden
 */
function getTipoFormulario() {
    // Tentar pegar do input hidden
    const inputFormularioId = document.querySelector('input[name="formulario_id"]');
    if (inputFormularioId && inputFormularioId.value) {
        return inputFormularioId.value;
    }

    // Fallback: tentar detectar pela URL
    const path = window.location.pathname;
    const matches = path.match(/form-candi-(\w+)\.html/);
    if (matches) {
        return `vaga-${matches[1]}`;
    }

    console.warn('⚠️ Não foi possível detectar o tipo de formulário');
    return null;
}

/**
 * Retorna configuração completa do título
 */
function getConfigTitulo(formularioId = null) {
    const tipo = formularioId || getTipoFormulario();
    
    if (!tipo || !CONFIG_TITULOS[tipo]) {
        console.error(`❌ Tipo de formulário desconhecido: ${tipo}`);
        return {
            funcao: 'Candidato',
            titulo_principal: 'Formulário de Cadastro',
            titulo_experiencia: 'Profissional',
            icone: 'fa-user'
        };
    }

    return CONFIG_TITULOS[tipo];
}

/**
 * Retorna apenas o título de experiência
 */
function getTituloExperiencia(formularioId = null) {
    return getConfigTitulo(formularioId).titulo_experiencia;
}

/**
 * Retorna o título principal completo
 */
function getTituloPrincipal(formularioId = null) {
    return getConfigTitulo(formularioId).titulo_principal;
}

/**
 * Retorna apenas o nome da função
 */
function getFuncao(formularioId = null) {
    return getConfigTitulo(formularioId).funcao;
}

/**
 * Aplica títulos dinâmicos automaticamente na página
 */
function aplicarTitulosDinamicos() {
    const config = getConfigTitulo();
    
    // 1. SETAR VARIÁVEIS GLOBAIS PRIMEIRO
    window.TITULO_FUNCAO = config.titulo_experiencia;
    window.TITULO_COMPLETO = config.titulo_principal;
    
    console.log(`🎯 Título setado: ${window.TITULO_FUNCAO}`);

    // 2. Atualizar h1
    let tituloPrincipal = document.querySelector('[data-titulo-dinamico]');
    if (tituloPrincipal) {
        tituloPrincipal.textContent = config.titulo_principal;
    }

    // 3. Atualizar título da página
    document.title = config.titulo_principal;
}

window.TITULO_FUNCAO = getTituloExperiencia();
window.TITULO_COMPLETO = getTituloPrincipal();

window.CONFIG_TITULOS = CONFIG_TITULOS;
window.getTipoFormulario = getTipoFormulario;
window.getConfigTitulo = getConfigTitulo;
window.getTituloExperiencia = getTituloExperiencia;
window.getTituloPrincipal = getTituloPrincipal;
window.getFuncao = getFuncao;
window.aplicarTitulosDinamicos = aplicarTitulosDinamicos;

console.log('🎯 Sistema de títulos dinâmicos carregado!');