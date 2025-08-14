/* ===================================
   R.O RECRUTAMENTO - GLOBAL-SECTION.JS
   Sistema unificado para formulários de candidatos
   Versão limpa - 100% Supabase
   =================================== */

// ========================================
// 🎯 CONFIGURAÇÃO E CONSTANTES
// ========================================

// Tipos de candidatos válidos
const TIPOS_CANDIDATOS = [
    'candi-baba',
    'candi-copeiro', 
    'candi-caseiro',
    'candi-cozinheira',
    'candi-governanta',
    'candi-arrumadeira',
    'candi-casal'
];

// Estado do sistema
let sistemInicializado = false;
let secoesCarregadas = 0;
let totalSecoes = 0;

// ========================================
// 📋 SEÇÕES HTML REUTILIZÁVEIS
// ========================================

const secoes = {
    
    // DADOS PESSOAIS
    'dados-pessoais': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-user"></i>
                Dados Pessoais
            </h2>
            
            <div class="form-grid">
                <div class="form-group full-width">
                    <label for="nomeCompleto">Nome Completo <span class="required-asterisk">*</span></label>
                    <input type="text" id="nomeCompleto" name="nomeCompleto" required>
                </div>
                
                <div class="form-group">
                    <label for="dataNascimento">Data de Nascimento <span class="required-asterisk">*</span></label>
                    <input type="date" id="dataNascimento" name="dataNascimento" required>
                </div>
                
                <div class="form-group">
                    <label for="cpf">CPF <span class="required-asterisk">*</span></label>
                    <input type="text" id="cpf" name="cpf" placeholder="000.000.000-00" required>
                </div>
                
                <div class="form-group">
                    <label for="rg">RG <span class="required-asterisk">*</span></label>
                    <input type="text" id="rg" name="rg" required>
                </div>
                
                <div class="form-group">
                    <label for="estadoCivil">Estado Civil <span class="required-asterisk">*</span></label>
                    <select id="estadoCivil" name="estadoCivil" required>
                        <option value="">Selecione</option>
                        <option value="solteiro">Solteiro(a)</option>
                        <option value="casado">Casado(a)</option>
                        <option value="divorciado">Divorciado(a)</option>
                        <option value="viuvo">Viúvo(a)</option>
                        <option value="uniao-estavel">União Estável</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="nacionalidade">Nacionalidade <span class="required-asterisk">*</span></label>
                    <input type="text" id="nacionalidade" name="nacionalidade" value="Brasileira" required>
                </div>
            </div>
        </section>
    `,
    
    // CONTATO
    'contato': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-phone"></i>
                Contato
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="telefone">Telefone Principal <span class="required-asterisk">*</span></label>
                    <input type="tel" id="telefone" name="telefone" placeholder="(11) 99999-9999" required>
                </div>
                
                <div class="form-group">
                    <label for="whatsapp">WhatsApp <span class="required-asterisk">*</span></label>
                    <input type="tel" id="whatsapp" name="whatsapp" placeholder="(11) 99999-9999" required>
                </div>
                
                <div class="form-group full-width">
                    <label for="email">E-mail <span class="required-asterisk">*</span></label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group full-width">
                    <label for="endereco">Endereço Completo <span class="required-asterisk">*</span></label>
                    <input type="text" id="endereco" name="endereco" placeholder="Rua, número, bairro, cidade, estado" required>
                </div>
                
                <div class="form-group">
                    <label for="cep">CEP <span class="required-asterisk">*</span></label>
                    <input type="text" id="cep" name="cep" placeholder="00000-000" required>
                </div>
            </div>

            <!-- CNH e Filhos -->
            <div class="form-subsection">
                <div class="form-group">
                    <label>Possui CNH?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="possuiCnh" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="possuiCnh" value="sim" required>
                            <span>Sim</span>
                        </label>
                    </div>
                </div>
                
                <div class="cnh-details">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="categoriaCnh">Categoria</label>
                            <select id="categoriaCnh" name="categoriaCnh">
                                <option value="">Selecione</option>
                                <option value="A">A</option>
                                <option value="B">B</option>
                                <option value="AB">AB</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="vencimentoCnh">Vencimento CNH</label>
                            <input type="date" id="vencimentoCnh" name="vencimentoCnh">
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-subsection">
                <div class="form-group">
                    <label>Tem filhos?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="temFilhos" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="temFilhos" value="sim" required>
                            <span>Sim</span>
                        </label>
                    </div>
                </div>
                
                <div class="filhos-details">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="quantosFilhos">Quantos filhos?</label>
                            <input type="number" id="quantosFilhos" name="quantosFilhos" min="1" max="10">
                        </div>
                        
                        <div class="form-group">
                            <label for="idadesFilhos">Idades dos filhos</label>
                            <input type="text" id="idadesFilhos" name="idadesFilhos" placeholder="Ex: 5, 8, 12 anos">
                        </div>
                    </div>
                </div>
            </div>
        </section>
    `,
    
    // TREINAMENTO OBRIGATÓRIO
    'treinamento-obrigatorio': `
        <section class="form-section treinamento-section">
            <h2 class="section-title">
                <i class="fas fa-graduation-cap"></i>
                Treinamento Obrigatório - Centro de Treinamento
            </h2>
            
            <div class="treinamento-info">
                <div class="info-box">
                    <i class="fas fa-info-circle"></i>
                    <div>
                        <h3>Importante!</h3>
                        <p>Para fazer parte do nosso banco de dados, é <strong>obrigatório</strong> passar pelo treinamento introdutório em nosso Centro de Treinamento.</p>
                        <p><i class="fas fa-map-marker-alt"></i> <strong>Local:</strong> Rua Pedro Mascagni, 425 – Itatiba</p>
                    </div>
                </div>
            </div>

            <div class="form-grid">
                <div class="form-group full-width">
                    <label class="treinamento-question">Você se habilita a participar do treinamento obrigatório no Centro de Treinamento? <span class="required-asterisk">*</span></label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="aceitaTreinamento" value="sim" required>
                            <span>Sim, aceito participar do treinamento</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="aceitaTreinamento" value="nao" required>
                            <span>Não aceito</span>
                        </label>
                    </div>
                </div>
            </div>

            <div class="turno-selection">
                <div class="form-group">
                    <label for="turnoTreinamento">Qual turno você pode participar? (Segunda a Sexta)</label>
                    <select id="turnoTreinamento" name="turnoTreinamento" required>
                        <option value="">Selecione o turno</option>
                        <option value="manha">Manhã (08h às 12h)</option>
                        <option value="tarde">Tarde (13h às 17h)</option>
                        <option value="noite">Noite (18h às 22h)</option>
                    </select>
                </div>
            </div>

            <div class="rejection-message">
                <div class="alert-box">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>
                        <h4>Ops! Treinamento Obrigatório</h4>
                        <p>Infelizmente, o treinamento no Centro de Treinamento é <strong>obrigatório</strong> para todos os profissionais que desejam fazer parte do nosso banco de dados.</p>
                        <p>Este treinamento é o que nos diferencia e garante a qualidade dos nossos serviços!</p>
                        <p><strong>Reconsidere sua decisão para continuar o cadastro.</strong></p>
                    </div>
                </div>
            </div>
        </section>
    `,
    
    // PRETENSÕES E CONDIÇÕES
    'pretensoes-condicoes': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-dollar-sign"></i>
                Pretensões e Condições
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="pretensaoSalarial">Pretensão salarial mensal (bruto)</label>
                    <input type="text" id="pretensaoSalarial" name="pretensaoSalarial" placeholder="R$ 0.000,00">
                </div>
                
                <div class="form-group">
                    <label for="regimeTrabalho">Regime de trabalho preferido</label>
                    <select id="regimeTrabalho" name="regimeTrabalho">
                        <option value="">Selecione</option>
                        <option value="clt">CLT (Carteira Assinada)</option>
                        <option value="mei">MEI</option>
                        <option value="freelancer">Freelancer</option>
                    </select>
                </div>
            </div>

            <div class="form-subsection">
                <div class="form-group">
                    <label>Salário negociável?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="negociavel" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="negociavel" value="sim" required>
                            <span>Sim</span>
                        </label>
                    </div>
                </div>
            </div>
        </section>
    `,
    
    // DISPONIBILIDADE
    'disponibilidade': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-calendar-check"></i>
                Disponibilidade
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label>Disponibilidade para início imediato?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="inicioImediato" value="sim" required>
                            <span>Sim</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="inicioImediato" value="nao" required>
                            <span>Não</span>
                        </label>
                    </div>
                </div>
                
                <div class="data-disponivel">
                    <div class="form-group">
                        <label for="dataDisponivel">Data disponível</label>
                        <input type="date" id="dataDisponivel" name="dataDisponivel">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Disponibilidade para eventos noturnos?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="eventosNoturnos" value="sim" required>
                            <span>Sim</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="eventosNoturnos" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="eventosNoturnos" value="ocasionalmente" required>
                            <span>Ocasionalmente</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Disponibilidade para trabalhar em finais de semana/feriados?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="fimSemana" value="sim-sempre" required>
                            <span>Sim, sempre</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="fimSemana" value="nao" required>
                            <span>Não</span>
                        </label>
                    </div>
                </div>

                <div class="form-group full-width">
                    <label>Pode dormir no trabalho aos fins de semana?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="dormirFimSemana" value="sim" required>
                            <span>Sim</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="dormirFimSemana" value="nao" required>
                            <span>Não</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Disponibilidade para viagens?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="viagens" value="sim" required>
                            <span>Sim (nacionais/internacionais)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="viagens" value="apenas-nacionais" required>
                            <span>Apenas nacionais</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="viagens" value="nao" required>
                            <span>Não</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Possui passaporte internacional válido?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="passaporte" value="sim" required>
                            <span>Sim</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="passaporte" value="pode-providenciar" required>
                            <span>Não, mas posso providenciar</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="passaporte" value="nao-interesse" required>
                            <span>Não tenho interesse</span>
                        </label>
                    </div>
                </div>
                
                <div class="passaporte-vencimento">
                    <div class="form-group">
                        <label for="vencimentoPassaporte">Vencimento do passaporte</label>
                        <input type="date" id="vencimentoPassaporte" name="vencimentoPassaporte">
                    </div>
                </div>
            </div>
        </section>
    `
};

// ========================================
// 🔧 SISTEMA DE CARREGAMENTO DE SEÇÕES
// ========================================

/**
 * Carrega uma seção específica em um container
 */
function carregarSecao(nomeSecao, containerId) {
    return new Promise((resolve, reject) => {
        try {
            console.log(`🔄 Carregando seção: ${nomeSecao} -> ${containerId}`);
            
            const container = document.getElementById(containerId);
            if (!container) {
                throw new Error(`Container ${containerId} não encontrado`);
            }
            
            if (!secoes[nomeSecao]) {
                throw new Error(`Seção ${nomeSecao} não existe`);
            }
            
            container.innerHTML = secoes[nomeSecao];
            console.log(`✅ Seção ${nomeSecao} carregada`);
            
            setTimeout(() => {
                inicializarFuncionalidadesSecao(nomeSecao);
                secoesCarregadas++;
                resolve(nomeSecao);
            }, 10);
            
        } catch (error) {
            console.error(`❌ Erro ao carregar seção ${nomeSecao}:`, error);
            reject(error);
        }
    });
}

/**
 * Carrega todas as seções padrão
 */
function carregarTodasSecoesPadrao() {
    const secoesParaCarregar = [
        { nome: 'dados-pessoais', container: 'dados-pessoais-container' },
        { nome: 'treinamento-obrigatorio', container: 'treinamento-obrigatorio-container' },
        { nome: 'contato', container: 'contato-container' },
        { nome: 'pretensoes-condicoes', container: 'pretensoes-condicoes-container' },
        { nome: 'disponibilidade', container: 'disponibilidade-container' }
    ];
    
    totalSecoes = secoesParaCarregar.length;
    secoesCarregadas = 0;
    
    console.log(`🚀 Carregando ${totalSecoes} seções...`);
    
    const promises = secoesParaCarregar.map(secao => 
        carregarSecao(secao.nome, secao.container)
    );
    
    return Promise.all(promises);
}

// ========================================
// 🎛️ FUNCIONALIDADES DAS SEÇÕES
// ========================================

/**
 * Inicializa funcionalidades após carregar seções
 */
function inicializarFuncionalidadesSecao(nomeSecao) {
    console.log(`🔧 Inicializando: ${nomeSecao}`);
    
    switch(nomeSecao) {
        case 'dados-pessoais':
            configurarMascaraCPF();
            break;
        case 'contato':
            configurarMascarasTelefone();
            configurarMascaraCEP();
            configurarCamposCondicionaisCNH();
            configurarCamposCondicionaisFilhos();
            break;
        case 'disponibilidade':
            configurarCamposCondicionaisDisponibilidade();
            break;
        case 'treinamento-obrigatorio':
            configurarTreinamentoObrigatorio();
            break;
    }
}

/**
 * Configura máscara de CPF
 */
function configurarMascaraCPF() {
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            let valor = e.target.value.replace(/\D/g, '');
            valor = valor.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            e.target.value = valor;
        });
    }
}

/**
 * Configura máscaras de telefone
 */
function configurarMascarasTelefone() {
    const telefoneInputs = ['telefone', 'whatsapp'];
    
    telefoneInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', function(e) {
                let valor = e.target.value.replace(/\D/g, '');
                valor = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                e.target.value = valor;
            });
        }
    });
}

/**
 * Configura máscara de CEP
 */
function configurarMascaraCEP() {
    const cepInput = document.getElementById('cep');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let valor = e.target.value.replace(/\D/g, '');
            valor = valor.replace(/(\d{5})(\d{3})/, '$1-$2');
            e.target.value = valor;
        });
    }
}

/**
 * Configura campos condicionais da CNH
 */
function configurarCamposCondicionaisCNH() {
    const possuiCnh = document.querySelectorAll('input[name="possuiCnh"]');
    const cnhDetails = document.querySelector('.cnh-details');
    
    if (possuiCnh.length && cnhDetails) {
        possuiCnh.forEach(radio => {
            radio.addEventListener('change', function() {
                cnhDetails.classList.toggle('show', this.value === 'sim');
            });
        });
    }
}

/**
 * Configura campos condicionais dos filhos
 */
function configurarCamposCondicionaisFilhos() {
    const temFilhos = document.querySelectorAll('input[name="temFilhos"]');
    const filhosDetails = document.querySelector('.filhos-details');
    
    if (temFilhos.length && filhosDetails) {
        temFilhos.forEach(radio => {
            radio.addEventListener('change', function() {
                filhosDetails.classList.toggle('show', this.value === 'sim');
            });
        });
    }
}

/**
 * Configura campos condicionais de disponibilidade
 */
function configurarCamposCondicionaisDisponibilidade() {
    // Data disponível
    const inicioImediato = document.querySelectorAll('input[name="inicioImediato"]');
    const dataDisponivel = document.querySelector('.data-disponivel');
    
    if (inicioImediato.length && dataDisponivel) {
        inicioImediato.forEach(radio => {
            radio.addEventListener('change', function() {
                dataDisponivel.classList.toggle('show', this.value === 'nao');
            });
        });
    }
    
    // Passaporte
    const passaporte = document.querySelectorAll('input[name="passaporte"]');
    const passaporteVencimento = document.querySelector('.passaporte-vencimento');
    
    if (passaporte.length && passaporteVencimento) {
        passaporte.forEach(radio => {
            radio.addEventListener('change', function() {
                passaporteVencimento.classList.toggle('show', this.value === 'sim');
            });
        });
    }
}

/**
 * Configura treinamento obrigatório
 */
/**
 * Configura treinamento obrigatório - VERSÃO CORRIGIDA
 */
function configurarTreinamentoObrigatorio() {
    const aceitaTreinamento = document.querySelectorAll('input[name="aceitaTreinamento"]');
    const turnoSelection = document.querySelector('.turno-selection');
    const rejectionMessage = document.querySelector('.rejection-message');
    const turnoSelect = document.getElementById('turnoTreinamento');
    
    if (!aceitaTreinamento.length) {
        console.warn('⚠️ Campos de treinamento não encontrados');
        return;
    }
    
    console.log('🎓 Configurando treinamento obrigatório...');
    
    // ✅ INICIALIZAR ESTADO - garantir que elementos existam
    if (turnoSelection) {
        turnoSelection.style.display = 'none';
        turnoSelection.classList.remove('show');
    }
    if (rejectionMessage) {
        rejectionMessage.style.display = 'none';
        rejectionMessage.classList.remove('show');
    }
    
    // ✅ BLOQUEAR FORMULÁRIO INICIALMENTE
    bloquearOutrasSecoes();
    
    aceitaTreinamento.forEach(radio => {
        radio.addEventListener('change', function() {
            console.log(`📄 Treinamento mudou para: ${this.value}`);
            
            if (this.value === 'sim') {
                // ✅ ACEITO O TREINAMENTO
                console.log('✅ Treinamento aceito, mostrando seleção de turno...');
                
                if (turnoSelection) {
                    turnoSelection.style.display = 'block';
                    turnoSelection.classList.add('show');
                    console.log('📅 Seleção de turno exibida');
                }
                if (rejectionMessage) {
                    rejectionMessage.style.display = 'none';
                    rejectionMessage.classList.remove('show');
                }
                if (turnoSelect) {
                    turnoSelect.required = true;
                    console.log('⚡ Campo turno marcado como obrigatório');
                }
                
                // ✅ SE JÁ TEM TURNO SELECIONADO, LIBERAR IMEDIATAMENTE
                if (turnoSelect && turnoSelect.value) {
                    console.log('🚀 Turno já selecionado, liberando formulário...');
                    desbloquearOutrasSecoes();
                } else {
                    console.log('⏳ Aguardando seleção de turno...');
                    // Manter bloqueado até selecionar turno
                    bloquearOutrasSecoes();
                }
                
            } else {
                // ❌ NÃO ACEITO O TREINAMENTO
                console.log('❌ Treinamento rejeitado');
                
                if (turnoSelection) {
                    turnoSelection.style.display = 'none';
                    turnoSelection.classList.remove('show');
                }
                if (rejectionMessage) {
                    rejectionMessage.style.display = 'block';
                    rejectionMessage.classList.add('show');
                    console.log('⚠️ Mensagem de rejeição exibida');
                }
                if (turnoSelect) {
                    turnoSelect.required = false;
                    turnoSelect.value = '';
                }
                
                // Manter bloqueado
                bloquearOutrasSecoes();
            }
        });
    });
    
    // ✅ EVENTO PARA SELEÇÃO DE TURNO
    if (turnoSelect) {
        turnoSelect.addEventListener('change', function() {
            console.log(`🕐 Turno selecionado: ${this.value}`);
            
            const treinamentoAceito = isTreinamentoAceito();
            console.log(`🎓 Treinamento aceito: ${treinamentoAceito}`);
            
            if (this.value && treinamentoAceito) {
                console.log('🎉 CONDIÇÕES ATENDIDAS: Liberando formulário!');
                desbloquearOutrasSecoes();
            } else if (!this.value && treinamentoAceito) {
                console.log('⚠️ Turno removido, bloqueando formulário...');
                bloquearOutrasSecoes();
            }
        });
        
        // ✅ VERIFICAR ESTADO INICIAL DO TURNO
        const estadoInicial = turnoSelect.value;
        if (estadoInicial) {
            console.log(`🔄 Estado inicial do turno: ${estadoInicial}`);
        }
    }
    
    console.log('✅ Treinamento obrigatório configurado com sucesso');
}

function mostrarMensagemBloqueio() {
    // Remover mensagem existente se houver
    const mensagemExistente = document.querySelector('.form-blocked-message');
    if (mensagemExistente) {
        mensagemExistente.remove();
    }
}

/**
 * Bloqueia APENAS outras seções (não a de treinamento) - FUNÇÃO CORRIGIDA
 */
function bloquearOutrasSecoes() {
    // Selecionar TODAS as seções EXCETO treinamento E header/footer
    const secoes = document.querySelectorAll('.form-section:not(.treinamento-section)');
    const containers = document.querySelectorAll('[id$="-container"]:not(#treinamento-obrigatorio-container)');
    const submitBtn = document.querySelector('.btn-submit, button[type="submit"]');
    
    console.log(`🔒 Bloqueando ${secoes.length} seções + ${containers.length} containers`);
    
    // Usar pointer-events e opacity ao invés de sobrepor o header
    secoes.forEach(secao => {
        secao.classList.add('form-locked');
        secao.classList.remove('form-unlocked');
        secao.style.pointerEvents = 'none';
        secao.style.opacity = '0.5';
        secao.style.position = 'relative';
    });
    
    containers.forEach(container => {
        container.classList.add('form-locked');
        container.classList.remove('form-unlocked');
        container.style.pointerEvents = 'none';
        container.style.opacity = '0.5';
    });
    
    // Bloquear apenas botão de envio, não navegação
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
    }
    
    // Garantir que header/footer/navegação continuem funcionais
    const header = document.querySelector('header, .header, #header-container');
    const footer = document.querySelector('footer, .footer, #footer-container');
    const nav = document.querySelector('nav, .nav, .navigation');
    
    [header, footer, nav].forEach(element => {
        if (element) {
            element.style.pointerEvents = 'auto';
            element.style.opacity = '1';
            element.style.zIndex = '9999';
        }
    });
    
    // Mostrar mensagem visual mais sutil
    mostrarMensagemBloqueio();
    
    console.log('🔒 Outras seções bloqueadas (navegação permanece liberada)');
}

/**
 * Desbloqueia outras seções - FUNÇÃO CORRIGIDA
 */
function desbloquearOutrasSecoes() {
    const secoes = document.querySelectorAll('.form-section:not(.treinamento-section)');
    const containers = document.querySelectorAll('[id$="-container"]:not(#treinamento-obrigatorio-container)');
    const submitBtn = document.querySelector('.btn-submit, button[type="submit"]');
    
    console.log(`🔓 Desbloqueando ${secoes.length} seções + ${containers.length} containers`);
    
    // Restaurar interação completa
    secoes.forEach(secao => {
        secao.classList.remove('form-locked');
        secao.classList.add('form-unlocked');
        secao.style.pointerEvents = 'auto';
        secao.style.opacity = '1';
    });
    
    containers.forEach(container => {
        container.classList.remove('form-locked');
        container.classList.add('form-unlocked');
        container.style.pointerEvents = 'auto';
        container.style.opacity = '1';
    });
    
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    }
    
    // Remover mensagem de bloqueio
    removerMensagemBloqueio();
    
    console.log('✅ Formulário desbloqueado! Treinamento aceito e turno selecionado.');
}



/**
 * Verifica se treinamento foi aceito - FUNÇÃO MELHORADA
 */
function isTreinamentoAceito() {
    const aceita = document.querySelector('input[name="aceitaTreinamento"]:checked');
    const resultado = aceita && aceita.value === 'sim';
    console.log(`🎓 Verificação treinamento: ${resultado ? 'ACEITO' : 'NÃO ACEITO'}`);
    return resultado;
}
// ========================================
// 🚀 SISTEMA DE ENVIO - 100% SUPABASE
// ========================================

/**
/**
 * Inicializa sistema de envio universal
 */
function inicializarSistemaEnvio() {
    if (sistemInicializado) return;
    
    console.log('🚀 Inicializando sistema de envio...');
    
    // Inicializar Supabase
    inicializarSupabase();
    
    // Buscar formulários
    const formularios = document.querySelectorAll('form.candidate-form, form[id*="form"]');
    
    if (formularios.length === 0) {
        console.warn('⚠️ Nenhum formulário encontrado');
        return;
    }
    
    console.log(`📋 Encontrados ${formularios.length} formulário(s)`);
    
    formularios.forEach((form, index) => {
        if (form.hasAttribute('data-envio-configurado')) return;
        
        form.setAttribute('data-envio-configurado', 'true');
        
        const formularioId = form.querySelector('input[name="formulario_id"]');
        if (!formularioId) {
            console.error(`❌ Form ${index + 1} sem formulario_id!`);
        } else {
            console.log(`✅ Form configurado: ${formularioId.value}`);
        }
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            processarEnvioFormulario(form);
        });
    });
    
    sistemInicializado = true;
    console.log('🎉 Sistema de envio inicializado!');
}

/**
 * Inicializa conexão com Supabase
 */
async function inicializarSupabase() {
    try {
        if (window.supabase) {
            console.log('✅ Supabase já inicializado');
            return;
        }
        
        // Importar Supabase dinamicamente
        const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2');
        
        window.supabase = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.key);
        
        console.log('✅ Supabase inicializado');
        
        // Testar conexão
        const { data, error } = await window.supabase
            .from('candidatos')
            .select('count', { count: 'exact', head: true });
            
        if (error) {
            console.warn('⚠️ Teste de conexão Supabase:', error.message);
        } else {
            console.log('✅ Conexão Supabase testada com sucesso');
        }
        
    } catch (error) {
        console.error('❌ Erro ao inicializar Supabase:', error);
        throw new Error('Falha na inicialização do Supabase');
    }
}

/**
 * Processa envio do formulário
 */
async function processarEnvioFormulario(form) {
    console.log('📤 Processando envio do formulário...');
    
    try {
        // 1. Validações
        if (!validarFormulario(form)) return;
        if (!isTreinamentoAceito()) {
            alert('❌ Você deve aceitar o treinamento obrigatório para continuar.');
            return;
        }
        
        // 2. Loading
        setEstadoLoading(form, true);
        
        // 3. Coletar dados
        const dadosFormulario = coletarDadosFormulario(form);
        console.log('📋 Dados coletados:', dadosFormulario);
        
        // 4. Estruturar para Supabase
        const dadosEstruturados = estruturarDadosSupabase(dadosFormulario);
        console.log('📊 Dados estruturados:', dadosEstruturados);
        
        // 5. Enviar para Supabase
        await enviarParaSupabase(dadosEstruturados);
        
        // 6. Sucesso
        console.log('🎉 Envio realizado com sucesso!');
        mostrarModalSucesso(dadosFormulario.formulario_id);
        
    } catch (error) {
        console.error('❌ Erro no envio:', error);
        mostrarErro(error.message);
    } finally {
        setEstadoLoading(form, false);
    }
}

/**
 * Valida formulário
 */
function validarFormulario(form) {
    console.log('🔍 Validando formulário...');
    
    const erros = [];
    
    // Campos obrigatórios
    const camposObrigatorios = form.querySelectorAll('[required]');
    camposObrigatorios.forEach(campo => {
        if (!campo.value || campo.value.trim() === '') {
            const nome = campo.name || campo.id || 'Campo sem nome';
            erros.push(`Campo "${nome}" é obrigatório`);
        }
    });
    
    // Validar formulario_id
    const formularioId = form.querySelector('input[name="formulario_id"]');
    if (!formularioId || !formularioId.value) {
        erros.push('Tipo de formulário não identificado');
    } else if (!TIPOS_CANDIDATOS.includes(formularioId.value)) {
        erros.push(`Tipo de candidato inválido: ${formularioId.value}`);
    }
    
    // Validar email
    const email = form.querySelector('input[name="email"]');
    if (email && email.value && !validarEmail(email.value)) {
        erros.push('Email inválido');
    }
    
    if (erros.length > 0) {
        console.error('❌ Erros de validação:', erros);
        mostrarErrosValidacao(erros);
        return false;
    }
    
    console.log('✅ Formulário válido');
    return true;
}

/**
 * Coleta dados do formulário
 */
function coletarDadosFormulario(form) {
    const formData = new FormData(form);
    const dados = {};
    
    for (let [key, value] of formData.entries()) {
        if (dados[key]) {
            // Se já existe, converter para array
            if (Array.isArray(dados[key])) {
                dados[key].push(value);
            } else {
                dados[key] = [dados[key], value];
            }
        } else {
            dados[key] = value;
        }
    }
    
    return dados;
}

/**
 * Estrutura dados para Supabase
 */
function estruturarDadosSupabase(formData) {
    // Dados universais
    const dadosUniversais = {
        formulario_id: formData.formulario_id,
        nome_completo: formData.nomeCompleto || null,
        data_nascimento: formData.dataNascimento || null,
        cpf: formData.cpf || null,
        rg: formData.rg || null,
        estado_civil: formData.estadoCivil || null,
        nacionalidade: formData.nacionalidade || 'Brasileira',
        telefone: formData.telefone || null,
        whatsapp: formData.whatsapp || null,
        email: formData.email || null,
        endereco: formData.endereco || null,
        cep: formData.cep || null,
        cidade: extrairCidadeEndereco(formData.endereco),
        possui_cnh: formData.possuiCnh === 'sim',
        categoria_cnh: formData.categoriaCnh || null,
        vencimento_cnh: formData.vencimentoCnh || null,
        tem_filhos: formData.temFilhos === 'sim',
        quantos_filhos: formData.quantosFilhos ? parseInt(formData.quantosFilhos) : null,
        idades_filhos: formData.idadesFilhos || null,
        aceita_treinamento: formData.aceitaTreinamento === 'sim',
        turno_treinamento: formData.turnoTreinamento || null,
        inicio_imediato: formData.inicioImediato === 'sim',
        data_disponivel: formData.dataDisponivel || null,
        eventos_noturnos: formData.eventosNoturnos || null,
        fim_semana: formData.fimSemana || null,
        dormir_fim_semana: formData.dormirFimSemana || null,
        viagens: formData.viagens || null,
        passaporte: formData.passaporte || null,
        vencimento_passaporte: formData.vencimentoPassaporte || null,
        pretensao_salarial: converterSalario(formData.pretensaoSalarial),
        regime_trabalho: validarRegimeTrabalho(formData.regimeTrabalho),
        salario_negociavel: formData.negociavel === 'sim',
        tempo_experiencia: formData.tempoExperiencia || null,
        experiencia_alto_padrao: formData.experienciaAltoPadrao === 'sim',
        tempo_alto_padrao: formData.tempoAltoPadrao || null,
        possui_referencias: formData.possuiReferencias === 'sim',
        restricao_saude: formData.restricaoSaude === 'sim',
        especificar_restricao: formData.especificarRestricao || null,
        fuma: formData.fuma === 'sim',
        consome_alcool: formData.consumeAlcool || null,
        veiculo_proprio: formData.veiculoProprio === 'sim',
        tipo_veiculo: formData.tipoVeiculo || null,
        observacoes_adicionais: formData.observacoesAdicionais || null
    };
    
    // Dados específicos por tipo
    const dadosEspecificos = extrairDadosEspecificos(formData);
    
    // Referências
    const referencias = extrairReferencias(formData);
    
    return {
        ...dadosUniversais,
        dados_especificos: dadosEspecificos,
        referencias: referencias
    };
}

/**
 * Extrai dados específicos baseado no tipo
 */
function extrairDadosEspecificos(formData) {
    const tipo = formData.formulario_id;
    
    switch (tipo) {
        case 'candi-baba':
            return extrairDadosBaba(formData);
        case 'candi-caseiro':
            return extrairDadosCaseiro(formData);
        case 'candi-copeiro':
            return extrairDadosCopeiro(formData);
        case 'candi-cozinheira':
            return extrairDadosCozinheira(formData);
        case 'candi-governanta':
            return extrairDadosGovernanta(formData);
        case 'candi-arrumadeira':
            return extrairDadosArrumadeira(formData);
        case 'candi-casal':
            return extrairDadosCasal(formData);
        default:
            return {};
    }
}

/**
 * Extrai dados específicos da babá
 */
function extrairDadosBaba(formData) {
    return {
        faixas_etarias: arraySeguro(formData.faixasEtarias),
        faixa_preferencia: formData.faixaPreferencia,
        numero_maximo_criancas: formData.numeroMaximoCriancas,
        conhecimento_desenvolvimento: formData.conhecimentoDesenvolvimento,
        atividades_ludicas: formData.atividadesLudicas,
        necessidades_especiais: arraySeguro(formData.necessidadesEspeciais),
        outros_necessidades: formData.outrosNecessidadesEspecificar,
        preparar_refeicoes: formData.prepararRefeicoes,
        restricoes_alimentares: arraySeguro(formData.restricoesAlimentares),
        outros_restricoes: formData.outrosRestricoesEspecificar,
        primeiros_socorros: formData.primeirosSocorros,
        data_curso_primeiros: formData.dataCursoPrimeiros,
        outros_cursos: arraySeguro(formData.outrosCursos),
        outros_cursos_especificar: formData.outrosCursosEspecificar,
        dormir_trabalho: formData.dormirTrabalho,
        morar_local: formData.morarLocal,
        atividades: arraySeguro(formData.atividades),
        outros_atividades: formData.outrosAtividadesEspecificar,
        lida_birras: formData.lidaBirras,
        nivel_ingles: formData.nivelIngles,
        nivel_espanhol: formData.nivelEspanhol,
        nivel_frances: formData.nivelFrances,
        outros_idiomas: formData.outrosIdiomas,
        ensina_idiomas: formData.ensinaIdiomas === 'sim',
        quais_idiomas_ensina: formData.quaisIdiomasEnsina,
        tem_alergias: formData.temAlergias === 'sim',
        especificar_alergias: formData.especificarAlergias,
        situacoes_emergencia: formData.situacoesEmergencia,
        porque_escolheu_baba: formData.porqueEscolheuBaba,
        estilo_cuidar: formData.estiloCuidar
    };
}

/**
 * Extrai dados específicos do caseiro
 */
function extrairDadosCaseiro(formData) {
    return {
        manutencao_eletrica: formData.manutencaoEletrica,
        manutencao_hidraulica: formData.manutencaoHidraulica,
        cuidados_jardim: formData.cuidadosJardim,
        cuidados_piscina: formData.cuidadosPiscina,
        experiencia_seguranca: formData.experienciaSeguranca,
        automacao_residencial: formData.automacaoResidencial,
        equipamentos_jardinagem: arraySeguro(formData.equipamentosJardinagem),
        outros_equipamentos_jardim: formData.outrosEquipamentosJardimEspecificar,
        morar_local: formData.morarLocal,
        certificacoes: arraySeguro(formData.certificacoes),
        outros_certificacoes: formData.outrosCertificacoesEspecificar,
        situacoes_emergencia: formData.situacoesEmergencia,
        porque_contratar: formData.porqueContratar
    };
}

/**
 * Extrai dados específicos do copeiro (placeholder para futuras implementações)
 */
function extrairDadosCopeiro(formData) {
    return {
        // Competências técnicas
        conhecimento_vinhos: formData.conhecimentoVinhos || null,
        habilidade_coqueteis: formData.habilidadeCoqueteis || null,
        montagem_mesas: formData.montagemMesas || null,
        decoracao_mesa: formData.decoracaoMesa || null,
        gestao_estoque: formData.gestaoEstoque || null,
        etiqueta_protocolo: formData.etiquetaProtocolo || null,
        
        // Tipos de eventos
        tipos_eventos: arraySeguro(formData.tiposEventos),
        outros_eventos_especificar: formData.outrosEventosEspecificar || null,
        frequencia_eventos: formData.frequenciaEventos || null,
        
        // Qualificações
        certificacoes_copeiro: arraySeguro(formData.certificacoes),
        
        // Questões profissionais
        maior_diferencial: formData.maiorDiferencial || null,
        organiza_rotina: formData.organizaRotina || null,
        observacoes_adicionais: formData.observacoesAdicionais || null
    };
}

/**
 * Extrai dados específicos da cozinheira (placeholder para futuras implementações)
 */
function extrairDadosCozinheira(formData) {
    return {
         // Experiência profissional
        tipos_estabelecimento: arraySeguro(formData.tiposEstabelecimento),
        outros_estabelecimentos_especificar: formData.outrosEstabelecimentosEspecificar || null,
        
        // Especialidades culinárias
        culinarias: arraySeguro(formData.culinarias),
        outros_culinarias_especificar: formData.outrosCulinariasEspecificar || null,
        brasileira_regional_especificar: formData.brasileiraRegionalEspecificar || null,
        culinaria_favorita: formData.culinariaFavorita || null,
        nivel_brasileira: formData.nivelBrasileira || null,
        nivel_italiana: formData.nivelItaliana || null,
        nivel_francesa: formData.nivelFrancesa || null,
        nivel_asiatica: formData.nivelAsiatica || null,
        
        // Restrições alimentares e dietas
        dietas_especiais: arraySeguro(formData.dietasEspeciais),
        outros_dietas_especificar: formData.outrosDietasEspecificar || null,
        alergias_alimentares: arraySeguro(formData.alergiasAlimentares),
        outras_alergias_especificar: formData.outrasAlergiasEspecificar || null,
        adapta_receitas: formData.adaptaReceitas || null,
        
        // Técnicas e habilidades
        tecnicas_coccao: arraySeguro(formData.tecnicasCoccao),
        outros_tecnicas_coccao_especificar: formData.outrosTecnicasCoccaoEspecificar || null,
        experiencia_sobremesas: formData.experienciaSobremesas || null,
        habilidades_especificas: arraySeguro(formData.habilidadesEspecificas),
        outros_habilidades_especificar: formData.outrosHabilidadesEspecificar || null,
        
        // Gestão e planejamento
        planejamento_cardapios: formData.planejamentoCardapios || null,
        gestao_estoque_cozinha: formData.gestaoEstoque || null,
        
        // Certificações
        certificacoes_cozinha: arraySeguro(formData.certificacoes),
        outros_certificacoes_especificar: formData.outrosCertificacoesEspecificar || null,
        
        // Informações complementares
        alergia_alimento: formData.alergiaAlimento === 'sim',
        especificar_alergia_alimento: formData.especificarAlergiaAlimento || null,
        
        // Questões profissionais
        prato_especialidade: formData.pratoEspecialidade || null,
        atualizacao_tendencias: formData.atualizacaoTendencias || null,
        
        // Referências específicas
        ref1_tipo_cozinha: formData.ref1TipoCozinha || null,
        ref2_tipo_cozinha: formData.ref2TipoCozinha || null
    };
}

/**
 * Extrai dados específicos da governanta (placeholder para futuras implementações)
 */
function extrairDadosGovernanta(formData) {
    return {
            // Experiência profissional
        coordenou_equipes: formData.coordenouEquipes === 'sim',
        tamanho_equipe: formData.tamanhoEquipe || null,
        respon_rotina_compras: formData.responRotinaCompras === 'sim',
        tipos_residencia: arraySeguro(formData.tiposResidencia),
        outros_residencia_especificar: formData.outrosResidenciaEspecificar || null,
        
        // Competências técnicas
        organizacao_lideranca: formData.organizacaoLideranca || null,
        controle_estoque: formData.controleEstoque || null,
        organizacao_rotina: formData.organizacaoRotina || null,
        atendimento_moradores: formData.atendimentoMoradores || null,
        planejamento_refeicoes: formData.planejamentoRefeicoes || null,
        etiqueta_protocolo: formData.etiquetaProtocolo || null,
        preparacao_eventos: formData.preparacaoEventos || null,
        
        // Certificações
        certificacoes_governanta: arraySeguro(formData.certificacoes),
        outros_certificacoes_especificar: formData.outrosCertificacoesEspecificar || null,
        
        // Perfil e postura
        organiza_equipe: formData.organizaEquipe || null,
        participou_eventos: formData.participouEventos === 'sim',
        descricao_eventos: formData.descricaoEventos || null,
        
        // Expectativas e diferenciais
        porque_pessoa_certa: formData.porquePessoaCerta || null,
        diferencial_governanta: formData.diferencialGovernanta || null,
        
        // Saúde e bem-estar
        alergia_limpeza: formData.alergiaLimpeza === 'sim',
        especificar_alergia: formData.especificarAlergia || null
    };
}

/**
 * Extrai dados específicos da arrumadeira (placeholder para futuras implementações)
 */
function extrairDadosArrumadeira(formData) {
    return {
         // Experiência profissional
        tipos_residencia: arraySeguro(formData.tiposResidencia),
        outros_residencia_especificar: formData.outrosResidenciaEspecificar || null,
        
        // Competências técnicas
        equipamentos_limpeza: arraySeguro(formData.equipamentosLimpeza),
        outros_equipamentos_especificar: formData.outrosEquipamentosEspecificar || null,
        organizacao_closets: formData.organizacaoClosets || null,
        montagem_cama: formData.montagemCama || null,
        tecnicas_lavanderia: formData.tecnicasLavanderia || null,
        habilidade_passar: formData.habilidadePassar || null,
        
        // Especialidades em organização
        tecnicas_organizacao: arraySeguro(formData.tecnicasOrganizacao),
        outros_tecnicas_especificar: formData.outrosTecnicasEspecificar || null,
        experiencia_eventos: formData.experienciaEventos || null,
        
        // Produtos e técnicas de limpeza
        produtos_limpeza: arraySeguro(formData.produtosLimpeza),
        outros_produtos_especificar: formData.outrosProdutosEspecificar || null,
        alergia_limpeza: formData.alergiaLimpeza === 'sim',
        especificar_alergia: formData.especificarAlergia || null,
        metodos_limpeza: arraySeguro(formData.metodosLimpeza),
        outros_metodos_especificar: formData.outrosMetodosEspecificar || null,
        
        // Qualificações
        certificacoes_arrumadeira: arraySeguro(formData.certificacoes),
        outros_certificacoes_especificar: formData.outrosCertificacoesEspecificar || null,
        
        // Situações especiais
        experiencia_animais: formData.experienciaAnimais === 'sim',
        tipos_animais: arraySeguro(formData.tiposAnimais),
        outros_animais_especificar: formData.outrosAnimaisEspecificar || null,
        experiencia_criancas: formData.experienciaCriancas || null,
        lida_objetos_valor: formData.lidaObjetosValor || null,
        
        // Informações de saúde
        problemas_articulacoes: formData.problemasArticulacoes === 'sim',
        especificar_problemas: formData.especificarProblemas || null,
        
        // Questões profissionais
        maior_diferencial: formData.maiorDiferencial || null,
        organiza_rotina: formData.organizaRotina || null
    };
}

/**
 * Extrai dados específicos do casal (placeholder para futuras implementações)
 */
function extrairDadosCasal(formData) {
    return {
        // Dados pessoais - Ele
        nome_completo_ele: formData.nomeCompletoEle || null,
        data_nascimento_ele: formData.dataNascimentoEle || null,
        cpf_ele: formData.cpfEle || null,
        telefone_ele: formData.telefoneEle || null,
        whatsapp_ele: formData.whatsappEle || null,
        email_ele: formData.emailEle || null,
        possui_cnh_ele: formData.possuiCnhEle === 'sim',
        categoria_cnh_ele: formData.categoriaCnhEle || null,
        
        // Dados pessoais - Ela
        nome_completo_ela: formData.nomeCompletoEla || null,
        data_nascimento_ela: formData.dataNascimentoEla || null,
        cpf_ela: formData.cpfEla || null,
        telefone_ela: formData.telefoneEla || null,
        whatsapp_ela: formData.whatsappEla || null,
        email_ela: formData.emailEla || null,
        possui_cnh_ela: formData.possuiCnhEla === 'sim',
        categoria_cnh_ela: formData.categoriaCnhEla || null,
        
        // Informações gerais do casal
        estado_civil_casal: formData.estadoCivil || null,
        tempo_juntos: formData.tempoJuntos || null,
        endereco_completo: formData.enderecoCompleto || null,
        morar_residencia: formData.morarResidencia === 'sim',
        possui_pets: formData.possuiPets === 'sim',
        tipo_pet: formData.tipoPet || null,
        
        // Experiência profissional
        trabalhou_juntos: formData.trabalharamJuntos === 'sim',
        tempo_caseiros: formData.tempoCaseiros || null,
        
        // Competências - Ele
        competencias_ele: arraySeguro(formData.competenciasEle),
        sabe_fazer_churrasco: formData.sabeFazerChurrasco || null,
        sabe_assar_pizza: formData.sabeAssarPizza || null,
        montar_aperitivos: formData.montarAperitivos || null,
        servicos_barman: formData.servicosBarman === 'sim',
        nivel_coqueteis: arraySeguro(formData.nivelCoqueteis),
        experiencia_jardim: formData.experienciaJardim || null,
        detalhes_jardim: formData.detalhesJardim || null,
        cuidar_piscina: formData.cuidarPiscina || null,
        detalhes_piscina: formData.detalhesPiscina || null,
        outros_conhecimentos_ele: formData.outrosConhecimentosEle || null,
        
        // Competências - Ela
        competencias_ela: arraySeguro(formData.competenciasEla),
        sabe_cozinhar: formData.sabeCozinhar === 'sim',
        habilidades_cozinha: arraySeguro(formData.habilidadesCozinha),
        conhece_confeitaria: formData.conheceConfeitaria || null,
        especialidades_culinarias: formData.especialidadesCulinarias || null,
        outros_conhecimentos_ela: formData.outrosConhecimentosEla || null,
        
        // Disponibilidade
        morar_trabalho: formData.morarTrabalho === 'sim',
        fim_semana: formData.fimSemana === 'sim',
        
        // Regime e pretensão
        regime_desejado: formData.regimeDesejado || null,
        regime_outro_especificar: formData.regimeOutroEspecificar || null,
        pretensao_salarial_casal: converterSalario(formData.pretensaoSalarialCasal),
        
        // Objetivo e motivação
        porque_juntos: formData.porqueJuntos || null,
        diferencial_casal: formData.diferencialCasal || null,
        
        // Informações complementares
        fumam: formData.fumam === 'sim',
        consomem_alcool: formData.consumemAlcool || null
    };
}

/**
 * Extrai referências do formulário
 */
function extrairReferencias(formData) {
    const referencias = [];
    
    if (formData.possuiReferencias === 'sim') {
        // Referência 1
        if (formData.ref1Nome) {
            referencias.push({
                nome: formData.ref1Nome,
                telefone: formData.ref1Telefone,
                periodo_inicio: formData.ref1Inicio,
                periodo_fim: formData.ref1Fim,
                idades_criancas: formData.ref1IdadesCriancas || null,
                relacao: formData.ref1Relacao,
                outro_especificar: formData.ref1OutroEspecificar
            });
        }
        
        // Referência 2
        if (formData.ref2Nome) {
            referencias.push({
                nome: formData.ref2Nome,
                telefone: formData.ref2Telefone,
                periodo_inicio: formData.ref2Inicio,
                periodo_fim: formData.ref2Fim,
                idades_criancas: formData.ref2IdadesCriancas || null,
                relacao: formData.ref2Relacao,
                outro_especificar: formData.ref2OutroEspecificar
            });
        }
    }
    
    return referencias;
}

/**
 * Envia dados para Supabase
 */
async function enviarParaSupabase(dados) {
    console.log('📤 Enviando para Supabase...');
    
    if (!window.supabase) {
        throw new Error('Supabase não inicializado');
    }
    
    const { data, error } = await window.supabase
        .from('candidatos')
        .insert([dados]);
    
    if (error) {
        console.error('❌ Erro Supabase:', error);
        throw new Error(`Erro ao salvar: ${error.message}`);
    }
    
    console.log('✅ Dados salvos:', data);
    return data;
}

// ========================================
// 🎨 SISTEMA DE MODAL DE SUCESSO
// ========================================

/**
 * Mostra modal de sucesso
 */
function mostrarModalSucesso(tipoFormulario) {
    console.log(`🎉 Mostrando modal de sucesso: ${tipoFormulario}`);
    
    let modal = document.getElementById('successModal');
    
    if (!modal) {
        modal = criarModalSucesso();
        document.body.appendChild(modal);
    }
    
    atualizarConteudoModal(modal, tipoFormulario);
    modal.style.display = 'flex';
    configurarEventosModal(modal);
}

/**
 * Cria modal de sucesso
 */
function criarModalSucesso() {
    const modal = document.createElement('div');
    modal.id = 'successModal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <i class="fas fa-check-circle success-icon"></i>
                <h2>Candidatura Enviada com Sucesso!</h2>
            </div>
            <div class="modal-body">
                <p>Sua candidatura foi enviada com sucesso!</p>
                <p>Nossa equipe analisará seu perfil e entrará em contato em breve para marcar o dia do seu <strong>treinamento obrigatório</strong>.</p>
                <div class="next-steps">
                    <h3>Próximos passos:</h3>
                    <ul>
                        <li>Análise do seu perfil profissional</li>
                        <li>Verificação de documentos e referências</li>
                        <li>Agendamento do treinamento no Centro de Treinamento</li>
                        <li>Inclusão no banco de candidatos qualificados</li>
                        <li>Indicação para vagas compatíveis</li>
                    </ul>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-primary modal-close-btn">
                    <i class="fas fa-home"></i>
                    Voltar ao Início
                </button>
            </div>
        </div>
    `;
    return modal;
}

/**
 * Atualiza conteúdo do modal
 */
function atualizarConteudoModal(modal, tipoFormulario) {
    const nomesTipos = {
        'candi-baba': 'Babá',
        'candi-copeiro': 'Copeiro',
        'candi-caseiro': 'Caseiro',
        'candi-cozinheira': 'Cozinheira(o)',
        'candi-governanta': 'Governanta',
        'candi-arrumadeira': 'Arrumadeira',
        'candi-casal': 'Casal de Caseiros'
    };
    
    const nomeAmigavel = nomesTipos[tipoFormulario] || 'Profissional';
    const textoBody = modal.querySelector('.modal-body p');
    if (textoBody) {
        textoBody.innerHTML = `Sua candidatura para <strong>${nomeAmigavel}</strong> foi enviada com sucesso!`;
    }
}

/**
 * Configura eventos do modal
 */
function configurarEventosModal(modal) {
    const closeBtn = modal.querySelector('.modal-close-btn');
    if (closeBtn) {
        closeBtn.onclick = () => fecharModal(modal);
    }
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            fecharModal(modal);
        }
    };
}

/**
 * Fecha modal
 */
function fecharModal(modal) {
    modal.style.display = 'none';
    setTimeout(() => {
        window.location.href = '../../index.html';
    }, 500);
}

// ========================================
// 🛠️ FUNÇÕES AUXILIARES
// ========================================

/**
 * Array seguro (evita problemas com undefined)
 */
function arraySeguro(valor) {
    if (Array.isArray(valor)) return valor;
    if (valor) return [valor];
    return [];
}

/**
 * Valida regime de trabalho
 */
function validarRegimeTrabalho(valor) {
    const regimesValidos = ['clt', 'mei', 'freelancer'];
    return regimesValidos.includes(valor) ? valor : null;
}

/**
 * Converte salário para número
 */
function converterSalario(valor) {
    if (!valor) return null;
    try {
        const numero = valor.replace(/[^\d,]/g, '').replace(',', '.');
        return parseFloat(numero) || null;
    } catch {
        return null;
    }
}

/**
 * Extrai cidade do endereço
 */
function extrairCidadeEndereco(endereco) {
    if (!endereco) return null;
    // Lógica simples: pega a palavra antes do estado (última palavra)
    const partes = endereco.split(',').map(p => p.trim());
    return partes.length >= 2 ? partes[partes.length - 2] : null;
}

/**
 * Valida email
 */
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Controla estado de loading
 */
function setEstadoLoading(form, isLoading) {
    const submitBtn = form.querySelector('.btn-submit, button[type="submit"]');
    
    if (isLoading) {
        form.classList.add('form-loading');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.setAttribute('data-texto-original', submitBtn.innerHTML);
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        }
    } else {
        form.classList.remove('form-loading');
        if (submitBtn) {
            submitBtn.disabled = false;
            const textoOriginal = submitBtn.getAttribute('data-texto-original');
            if (textoOriginal) {
                submitBtn.innerHTML = textoOriginal;
            }
        }
    }
}

/**
 * Mostra erros de validação
 */
function mostrarErrosValidacao(erros) {
    const mensagem = 'Por favor, corrija os seguintes erros:\n\n' + erros.join('\n');
    alert(mensagem);
}

/**
 * Mostra erro genérico
 */
function mostrarErro(mensagem) {
    alert(`❌ Erro ao enviar candidatura:\n\n${mensagem}\n\nTente novamente ou entre em contato conosco.`);
}

// ========================================
// 🚀 INICIALIZAÇÃO PRINCIPAL
// ========================================

/**
 * Aguarda seções serem carregadas
 */
function aguardarCarregamentoSecoes() {
    return new Promise((resolve) => {
        const containers = document.querySelectorAll('[id$="-container"]');
        if (containers.length === 0) {
            resolve();
            return;
        }
        
        const verificar = setInterval(() => {
            const secoesCarregadasAtual = document.querySelectorAll('[id$="-container"] .form-section');
            if (secoesCarregadasAtual.length > 0 || secoesCarregadas >= totalSecoes) {
                clearInterval(verificar);
                resolve();
            }
        }, 100);
        
        // Timeout de segurança
        setTimeout(() => {
            clearInterval(verificar);
            resolve();
        }, 5000);
    });
}

/**
 * Inicialização principal do sistema
 */
async function inicializarSistema() {
    console.log('🚀 Inicializando sistema global...');
    
    try {
        await aguardarCarregamentoSecoes();
        inicializarSistemaEnvio();
        console.log('🎉 Sistema inicializado com sucesso!');
    } catch (error) {
        console.error('💥 Erro na inicialização:', error);
    }
}

// ========================================
// 🔄 AUTO-INICIALIZAÇÃO
// ========================================

// Auto-inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(inicializarSistema, 100);
    });
} else {
    setTimeout(inicializarSistema, 100);
}

// ========================================
// 🌐 FUNÇÕES GLOBAIS (compatibilidade)
// ========================================

// Expor funções principais globalmente
window.carregarSecao = carregarSecao;
window.carregarTodasSecoesPadrao = carregarTodasSecoesPadrao;
window.isTreinamentoAceito = isTreinamentoAceito;
window.fecharModal = fecharModal;

// Aliases para compatibilidade com código existente
window.loadFormSection = carregarSecao;
window.loadAllStandardSections = carregarTodasSecoesPadrao;
window.isTrainingAccepted = isTreinamentoAceito;
window.closeModal = fecharModal;
window.showSuccessModal = mostrarModalSucesso;

/* ===================================
   📋 SISTEMA COMPLETO E FUNCIONAL
   =================================== 

   ✅ Sistema limpo e otimizado
   ✅ 100% Supabase (sem API antiga)
   ✅ Estruturação automática por tipo
   ✅ Validações robustas
   ✅ Modal de sucesso universal
   ✅ Máscaras de input automáticas
   ✅ Campos condicionais inteligentes
    ✅ Tratamento de erros abrangente
   ✅ Preparado para futuras implementações
   ✅ Compatibilidade com código existente
   ✅ Sistema de loading responsivo
   ✅ Logs detalhados para debug

   🚀 PRÓXIMOS PASSOS:
   - Implementar outros tipos (copeiro, cozinheira, etc.)
   - Adicionar validações específicas por tipo
   - Sistema de upload de arquivos
   - Notificações por email
   - Dashboard administrativo

   📝 ESTRUTURA DE DADOS SUPABASE:
   - Dados universais: campos comuns a todos
   - dados_especificos: JSON com campos únicos por tipo
   - referencias: Array JSON com referências profissionais

   =================================== */