/* ===================================
   R.O RECRUTAMENTO - PROPRIETÁRIOS
   Seções globais + Funções Supabase
   =================================== */

const ownerFormSections = {
    'aceitar-termos': `
        <section class="form-section treinamento-section">
            <h2 class="section-title">
                <i class="fas fa-handshake"></i>
                Termos de Serviço
            </h2>
            
            <div class="treinamento-info">
                <div class="info-box">
                    <i class="fas fa-info-circle"></i>
                    <div>
                        <h3>Bem-vindo à R.O Recrutamento!</h3>
                        <p>Para utilizar nossos serviços de recrutamento de profissionais domésticos, é necessário aceitar nossos <u style="cursor: pointer;" onclick="openTermosModal()">termos de serviço e política de privacidade</u>.</p>
                        <p><i class="fas fa-shield-alt"></i> <strong>Garantimos:</strong> Total discrição e confidencialidade dos seus dados</p>
                        
                        <div style="margin-top: 15px;">
                            <button type="button" class="btn-info-agencia" onclick="toggleInfoAgencia()">
                                <i class="fas fa-question-circle"></i>
                                Não conhece como funciona nossa agência? Clique aqui
                            </button>
                        </div>
                        
                        <div class="info-agencia" style="display: none; margin-top: 15px; padding: 15px; background: rgba(52, 152, 219, 0.1); border-radius: 8px;">
                            <h4>Como funciona a R.O Recrutamento:</h4>
                            <ul style="margin: 10px 0; padding-left: 20px; color: var(--text-light);">
                                <li>Análise detalhada do seu perfil e necessidades</li>
                                <li>Pré-seleção rigorosa de candidatos qualificados</li>
                                <li>Verificação de referências e documentos</li>
                                <li>Apresentação apenas de profissionais compatíveis</li>
                                <li>Suporte durante todo o processo de contratação</li>
                                <li>Acompanhamento pós-contratação</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-grid">
                <div class="form-group full-width">
                    <label class="treinamento-question">Você aceita nossos termos de serviço e política de privacidade? <span class="required-asterisk">*</span></label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="aceitaTermos" value="sim" required>
                            <span>Sim, aceito os termos de serviço</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="aceitaTermos" value="nao" required>
                            <span>Não aceito</span>
                        </label>
                    </div>
                </div>
            </div>

            <div class="rejection-message">
                <div class="alert-box">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>
                        <h4>Termos Obrigatórios</h4>
                        <p>Para utilizar nossos serviços, é <strong>obrigatório</strong> aceitar os termos de serviço.</p>
                        <p>Os termos garantem a segurança e qualidade do processo de recrutamento para ambas as partes.</p>
                        <p><strong>Reconsidere sua decisão para continuar o cadastro da vaga.</strong></p>
                    </div>
                </div>
            </div>
        </section>

        <div id="termosModal" class="modal-overlay" onclick="closeTermosModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2><i class="fas fa-file-contract"></i> Termos de Serviço e Política de Privacidade</h2>
                    <button class="modal-close" onclick="closeTermosModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="termos-content">
                        <h3>1. DEFINIÇÕES E OBJETO</h3>
                        <p>A R.O Recrutamento é uma empresa especializada em recrutamento e seleção de profissionais domésticos. Estes termos regem a prestação de serviços de intermediação entre proprietários e profissionais.</p>
                        
                        <h3>2. SERVIÇOS OFERECIDOS</h3>
                        <p>• Análise de perfil e necessidades do cliente<br>
                        • Pré-seleção e triagem de candidatos<br>
                        • Verificação de referências e documentação<br>
                        • Apresentação de profissionais qualificados<br>
                        • Suporte no processo de contratação</p>
                        
                        <h3>3. OBRIGAÇÕES DO CLIENTE</h3>
                        <p>• Fornecer informações verdadeiras e atualizadas<br>
                        • Cumprir a legislação trabalhista vigente<br>
                        • Efetuar o pagamento dos serviços conforme acordado<br>
                        • Tratar os candidatos com respeito e profissionalismo</p>
                        
                        <h3>4. POLÍTICA DE PRIVACIDADE</h3>
                        <p>Todos os dados pessoais coletados são tratados conforme a Lei Geral de Proteção de Dados (LGPD). Garantimos sigilo absoluto das informações fornecidas.</p>
                        
                        <h3>5. LIMITAÇÃO DE RESPONSABILIDADE</h3>
                        <p>A R.O Recrutamento atua como intermediadora. A relação de trabalho estabelecida é de responsabilidade exclusiva entre o empregador e o empregado.</p>
                        
                        <h3>6. VIGÊNCIA</h3>
                        <p>Estes termos entram em vigor no momento da aceitação e permanecem válidos durante toda a prestação dos serviços.</p>
                        
                        <div class="termos-footer">
                            <p><strong>Última atualização:</strong> Janeiro de 2025</p>
                            <p><strong>Contato:</strong> contato@rorecrutamento.com.br</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn-modal-close" onclick="closeTermosModal()">
                        <i class="fas fa-check"></i>
                        Entendi
                    </button>
                </div>
            </div>
        </div>
    `,
    
    'dados-proprietario': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-user"></i>
                Dados para Contato
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="nome">Nome <span class="required-asterisk">*</span></label>
                    <input type="text" id="nome" name="nome" required>
                </div>
                
                <div class="form-group">
                    <label for="sobrenome">Sobrenome <span class="required-asterisk">*</span></label>
                    <input type="text" id="sobrenome" name="sobrenome" required>
                </div>
                
                <div class="form-group full-width">
                    <label for="email">E-mail <span class="required-asterisk">*</span></label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="cidade">Cidade <span class="required-asterisk">*</span></label>
                    <input type="text" id="cidade" name="cidade" placeholder="Ex: São Paulo" required>
                </div>
                
                <div class="form-group">
                    <label for="condominio">Condomínio</label>
                    <input type="text" id="condominio" name="condominio" placeholder="Nome do condomínio (se houver)">
                </div>
                
                <div class="form-group full-width">
                    <label for="ruaNumero">Rua e Número <span class="required-asterisk">*</span></label>
                    <input type="text" id="ruaNumero" name="ruaNumero" placeholder="Ex: Rua das Flores, 123" required>
                </div>
                
                <div class="form-group">
                    <label for="telefonePrincipal">Telefone Principal <span class="required-asterisk">*</span></label>
                    <input type="tel" id="telefonePrincipal" name="telefonePrincipal" placeholder="(11) 99999-9999" required>
                </div>
                
                <div class="form-group">
                    <label for="telefoneOpcional">Telefone Adicional</label>
                    <input type="tel" id="telefoneOpcional" name="telefoneOpcional" placeholder="(11) 99999-9999">
                </div>
            </div>
        </section>
    `,
    
    'caracteristicas-residencia': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-home"></i>
                Características da Residência
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label>Tipo de residência</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="tipoResidencia" value="residencia-fixa" required>
                            <span>Residência principal</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="tipoResidencia" value="casa-verao" required>
                            <span>Casa de veraneio</span>
                        </label>
                    </div>
                </div>
                
                <div class="frequencia-veraneio">
                    <div class="form-group">
                        <label>Frequência de uso da casa de veraneio</label>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input type="radio" name="frequenciaVeraneio" value="todos-fins-semana" required>
                                <span>Todos os fins de semana</span>
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="frequenciaVeraneio" value="pelo-menos-3" required>
                                <span>Pelo menos 3 fins de semana por mês</span>
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="frequenciaVeraneio" value="2-ou-menos" required>
                                <span>2 fins de semana ou menos por mês</span>
                            </label>
                            <p>Obs: essa informação é para selecionarmos o candidato ideal para você!</p>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Possui pets?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="temPets" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="temPets" value="sim" required>
                            <span>Sim</span>
                        </label>
                    </div>
                </div>
                
                <div class="pets-details">
                    <div class="form-grid">
                        <div class="form-group full-width">
                            <label for="tiposPets">Tipos e quantidade de pets</label>
                            <input type="text" id="tiposPets" name="tiposPets" placeholder="Ex: 2 cães de grande porte, 1 gato">
                        </div>
                        
                        <div class="form-group full-width">
                            <label for="cuidadosPets">Cuidados especiais necessários</label>
                            <input type="text" id="cuidadosPets" name="cuidadosPets" placeholder="Ex: medicação diária, passeios específicos, alimentação especial">
                        </div>
                    </div>
                </div>
                
                <div class="form-group full-width">
                    <label>Estilo da casa</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="estiloCasa" value="familiar" required>
                            <span>Casa familiar (mais reservada)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="estiloCasa" value="eventos" required>
                            <span>Recebe muitos convidados/eventos</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="estiloCasa" value="misto" required>
                            <span>Misto (familiar e eventos ocasionais)</span>
                        </label>
                    </div>
                </div>
            </div>
        </section>
    `,
    
    'detalhes-vaga': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-calendar-check"></i>
                Detalhes da Vaga
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label>Necessidade de início</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="inicioUrgente" value="imediato" required>
                            <span>Imediato</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="inicioUrgente" value="ate-15-dias" required>
                            <span>Até 15 dias</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="inicioUrgente" value="ate-30-dias" required>
                            <span>Até 30 dias</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="inicioUrgente" value="mais-30-dias" required>
                            <span>Mais de 30 dias</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Regime de trabalho desejado</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="regimeTrabalho" value="clt" required>
                            <span>CLT (Carteira Assinada)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="regimeTrabalho" value="mei" required>
                            <span>MEI</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="regimeTrabalho" value="ambos" required>
                            <span>Ambos (flexível)</span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Quantas folgas por semana?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="folgasSemana" value="1-folga" required>
                            <span>1 folga por semana</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="folgasSemana" value="2-folgas" required>
                            <span>2 folgas por semana</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="folgasSemana" value="flexivel" required>
                            <span>Flexível</span>
                        </label>
                    </div>
                </div>

                <div class="form-group full-width">
                    <label for="horarioTrabalho">Horário previsto de trabalho (dias úteis | seg - sex)</label>
                    <input type="text" id="horarioTrabalho" name="horarioTrabalho" placeholder="Ex: 7h às 16h, 8h às 17h" required>
                </div>

                <div class="form-group full-width">
                    <label for="horarioFimSemana">Horário previsto aos fins de semana (se aplicável)</label>
                    <input type="text" id="horarioFimSemana" name="horarioFimSemana" placeholder="Ex: 8h às 14h, 9h às 15h">
                </div>

                <div class="form-group">
                    <label>Oferece um fim de semana mensal como folga?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="fimSemanaMensalFolga" value="sim" required>
                            <span>Sim</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="fimSemanaMensalFolga" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="fimSemanaMensalFolga" value="negociavel" required>
                            <span>Negociável</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Necessário dormir no trabalho (fins de semana)?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="dormirTrabalho" value="sim" required>
                            <span>Sim</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="dormirTrabalho" value="nao" required>
                            <span>Não</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="dormirTrabalho" value="ocasional" required>
                            <span>Ocasionalmente</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group full-width">
                    <label for="restricoesVaga">Alguma restrição para a vaga?</label>
                    <textarea id="restricoesVaga" name="restricoesVaga" rows="3" placeholder="Ex: O que te deixaria desconfortável no candidato(a), situações, atitudes que você não gostaria de ver no dia a dia da casa, etc..."></textarea>
                </div>

                <div class="form-group full-width">
                    <label for="obrigacoesPrincipais"> Quais serão as principais obrigações desse colaborador (a)?</label>
                    <textarea id="obrigacoesPrincipais" name="obrigacoesPrincipais" rows="3" placeholder="Ex: Cuidar de cômodos especifícos, cuidar das manutenções, atender fins de semana, etc..."></textarea>
                </div>
            </div>
        </section>
    `,
    
    'oferta-salarial': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-dollar-sign"></i>
                Oferta Salarial
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="salarioOferecido">Salário oferecido (mensal/bruto) <span class="required-asterisk">*</span></label>
                    <input type="text" id="salarioOferecido" name="salarioOferecido" placeholder="R$ 0.000,00" required>
                </div>
                
                <div class="form-group full-width">
                    <div class="alert-box" style="background: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107;">
                        <i class="fas fa-exclamation-triangle" style="color: #ffc107;"></i>
                        <div>
                            <h4 style="color: #ffc107;">ATENÇÃO:</h4>
                            <p>Lembrando que profissionais que realmente se preocupam em entregar um bom trabalho, também se preocupam com o retorno dele!</p>
                        </div>
                    </div>
                </div>
                
                <div class="form-group full-width">
                    <label>Benefícios inclusos</label>
                    <div class="checkbox-grid">
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="vale-transporte">
                            <span>Vale Transporte</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="vale-alimentacao">
                            <span>Vale Alimentação</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="plano-saude">
                            <span>Plano de Saúde</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="moradia">
                            <span>Moradia</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="ajuda-custo">
                            <span>Ajuda de custo</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="outros">
                            <span>Outros</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="beneficios" value="nenhum">
                            <span>Nenhum</span>
                        </label>
                    </div>
                </div>
                
                <div class="outros-beneficios">
                    <div class="form-group full-width">
                        <label for="outrosBeneficios">Especifique outros benefícios</label>
                        <input type="text" id="outrosBeneficios" name="outrosBeneficios" placeholder="Descreva outros benefícios">
                    </div>
                </div>
            </div>
        </section>
    `,
    
    'requisitos-basicos': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-clipboard-check"></i>
                Requisitos Básicos
            </h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label>CNH obrigatória?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="cnhObrigatoria" value="sim" required>
                            <span>Sim, obrigatória</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="cnhObrigatoria" value="nao" required>
                            <span>Não obrigatória</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="cnhObrigatoria" value="desejavel" required>
                            <span>Desejável</span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Experiência anterior obrigatória?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="experienciaObrigatoria" value="sim" required>
                            <span>Sim, obrigatória</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="experienciaObrigatoria" value="nao" required>
                            <span>Não obrigatória</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="experienciaObrigatoria" value="desejavel" required>
                            <span>Desejável</span>
                        </label>
                    </div>
                </div>
                
                <div class="experiencia-details">
                    <div class="form-group">
                        <label>Experiência mínima exigida</label>
                        <select id="experienciaMinima" name="experienciaMinima" required>
                            <option value="">Selecione</option>
                            <option value="6-meses">6 meses</option>
                            <option value="1-ano">1 ano</option>
                            <option value="2-anos">2 anos</option>
                            <option value="3-anos">3 anos</option>
                            <option value="5-anos">5 anos ou mais</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Faixa etária mínima exigida?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="temIdadeMinima" value="nao" required>
                            <span>Não há restrição de idade</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="temIdadeMinima" value="sim" required>
                            <span>Sim, tenho preferência</span>
                        </label>
                    </div>
                </div>
                
                <div class="idade-minima-details">
                    <div class="form-group">
                        <label for="idadeMinima">Idade mínima desejada</label>
                        <select id="idadeMinima" name="idadeMinima">
                            <option value="">Selecione</option>
                            <option value="18-25">18 a 25 anos</option>
                            <option value="25-35">25 a 35 anos</option>
                            <option value="35-45">35 a 45 anos</option>
                            <option value="45-55">45 a 55 anos</option>
                            <option value="acima-55">Acima de 55 anos</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Referências obrigatórias?</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="referenciasObrigatorias" value="sim" required>
                            <span>Sim, obrigatórias</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="referenciasObrigatorias" value="nao" required>
                            <span>Não obrigatórias</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="referenciasObrigatorias" value="desejaveis" required>
                            <span>Desejáveis</span>
                        </label>
                    </div>
                </div>
            </div>
        </section>
    `,
    
    'treinamento-personalizado': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-graduation-cap"></i>
                Treinamento Personalizado
            </h2>
            
            <div class="treinamento-info">
                <div class="info-box">
                    <i class="fas fa-star"></i>
                    <div>
                        <h3>Treinamento Personalizado R.O</h3>
                        <p>Oferecemos treinamento personalizado para profissionais de acordo com suas necessidades específicas e rotina da sua residência.</p>
                        
                        <div style="margin-top: 15px;">
                            <button type="button" class="btn-info-treinamento" onclick="toggleInfoTreinamento()">
                                <i class="fas fa-info-circle"></i>
                                Saber mais sobre o treinamento personalizado
                            </button>
                        </div>
                        
                        <div class="info-treinamento" style="display: none; margin-top: 15px; padding: 15px; background: rgba(52, 152, 219, 0.1); border-radius: 8px;">
                            <h4>O que inclui o treinamento personalizado:</h4>
                            <ul style="margin: 10px 0; padding-left: 20px; color: var(--text-light);">
                                <li>Análise da rotina específica da sua residência</li>
                                <li>Treinamento adaptado às suas necessidades</li>
                                <li>Protocolos personalizados de atendimento</li>
                                <li>Orientações sobre equipamentos específicos</li>
                                <li>Padrões de qualidade customizados</li>
                                <li>Acompanhamento durante período de adaptação</li>
                            </ul>
                            <p><strong>Investimento:</strong> Consulte valores conforme complexidade</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-grid">
                <div class="form-group full-width">
                    <label>Interesse no treinamento personalizado</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="interesseTreinamento" value="tenho-interesse" required>
                            <span>Tenho interesse</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="interesseTreinamento" value="nao-tenho-interesse" required>
                            <span>Não tenho interesse</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="interesseTreinamento" value="quero-conversar" required>
                            <span>Quero conversar sobre</span>
                        </label>
                    </div>
                </div>
            </div>
        </section>
    `,
    
    'observacoes-adicionais': `
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-comment-dots"></i>
                Observações Adicionais
            </h2>
            
            <div class="form-grid">
                <div class="form-group full-width">
                    <label for="observacoes">Informações adicionais sobre a vaga</label>
                    <textarea id="observacoes" name="observacoes" rows="4" placeholder="Descreva qualquer informação adicional relevante sobre a vaga, expectativas ou requisitos específicos..."></textarea>
                </div>
                
                <div class="form-group">
                    <label for="contatoPreferido">Forma de contato preferida</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="contatoPreferido" value="telefone" required>
                            <span>Telefone</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="contatoPreferido" value="whatsapp" required>
                            <span>WhatsApp</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="contatoPreferido" value="email" required>
                            <span>E-mail</span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Melhor horário para contato</label>
                    <div class="radio-group">
                        <label class="checkbox-label">
                            <input type="checkbox" name="horarioContato" value="manha">
                            <span>Manhã (8h às 12h)</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="horarioContato" value="tarde">
                            <span>Tarde (12h às 18h)</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="horarioContato" value="noite">
                            <span>Noite (18h às 22h)</span>
                        </label>
                        <p><i>(Pode marcar mais de um.)</i></p>
                    </div>
                </div>
            </div>
        </section>
    `
};

// ===================================
// FUNÇÕES UNIVERSAIS PARA BANCO DE DADOS
// ===================================

function checkSupabaseConnection() {
    if (!window.supabase) {
        console.error('❌ Supabase não está disponível. Verifique se supabase-config.js foi carregado.');
        return false;
    }
    console.log('✅ Supabase conectado e disponível');
    return true;
}

// ===================================
// CORREÇÃO COMPLETA: collectBasicVagaFormData
// Substitua completamente no global-section-prop.js
// ===================================

function collectBasicVagaFormData(formId) {
    console.log('📝 Coletando dados básicos do formulário:', formId);
    
    const form = document.getElementById(formId);
    if (!form) {
        console.error('❌ Formulário não encontrado:', formId);
        return null;
    }
    
    const formData = new FormData(form);
    const data = {};
    
    // 🔥 MAPEAMENTO CORRETO HTML -> BANCO
    const fieldMapping = {
        // Dados do proprietário
        'nome': 'nome',
        'sobrenome': 'sobrenome', 
        'email': 'email',
        'cidade': 'cidade',
        'condominio': 'condominio',
        'ruaNumero': 'rua_numero',
        'telefonePrincipal': 'telefone_principal',
        'telefoneOpcional': 'telefone_opcional',
        
        // Características da residência
        'tipoResidencia': 'tipo_residencia',
        'frequenciaVeraneio': 'frequencia_veraneio',
        'temPets': 'tem_pets',
        'tiposPets': 'tipos_pets', 
        'cuidadosPets': 'cuidados_pets',
        'estiloCasa': 'estilo_casa',
        
        // Detalhes da vaga
        'inicioUrgente': 'inicio_urgente',
        'regimeTrabalho': 'regime_trabalho',
        'folgasSemana': 'folgas_semana',
        'horarioTrabalho': 'horario_trabalho',
        'horarioFimSemana': 'horario_fim_semana',
        'fimSemanaMensalFolga': 'fim_semana_mensal_folga',
        'dormirTrabalho': 'dormir_trabalho',
        'restricoesVaga': 'restricoes_vaga',
        
        // Oferta salarial
        'salarioOferecido': 'salario_oferecido',
        'outrosBeneficios': 'outros_beneficios',
        
        // Requisitos básicos
        'cnhObrigatoria': 'cnh_obrigatoria',
        'experienciaObrigatoria': 'experiencia_obrigatoria', 
        'experienciaMinima': 'experiencia_minima',
        'temIdadeMinima': 'tem_idade_minima',
        'idadeMinima': 'idade_minima',
        'referenciasObrigatorias': 'referencias_obrigatorias',
        
        // Observações e treinamento
        'interesseTreinamento': 'interesse_treinamento',
        'observacoes': 'observacoes',
        'contatoPreferido': 'contato_preferido',
        
        // Aceitar termos
        'aceitaTermos': 'aceita_termos'
    };
    
    // Coletar campos com mapeamento
    Object.keys(fieldMapping).forEach(htmlName => {
        const dbName = fieldMapping[htmlName];
        const value = formData.get(htmlName);
        if (value !== null && value !== '') {
            data[dbName] = value;
        }
    });
    
    // 🔥 COLETAR ARRAYS (checkboxes múltiplos)
    data.beneficios = collectArrayFields(form, 'beneficios');
    data.horario_contato = collectArrayFields(form, 'horarioContato');
    
    // 🔥 CONVERSÕES PARA BOOLEAN
    data.tem_pets = data.tem_pets === 'sim';
    data.tem_idade_minima = data.tem_idade_minima === 'sim'; 
    data.aceita_termos = data.aceita_termos === 'sim';
    
    // 🔥 LIMPEZA DE FORMATAÇÃO
    data.telefone_principal = cleanPhoneFormat(data.telefone_principal);
    data.telefone_opcional = cleanPhoneFormat(data.telefone_opcional);
    data.salario_oferecido = cleanSalaryFormat(data.salario_oferecido);
    
    // 🔥 VALIDAÇÕES CRÍTICAS
    if (!data.nome) {
        console.error('❌ Nome é obrigatório');
        return null;
    }
    
    if (!data.sobrenome) {
        console.error('❌ Sobrenome é obrigatório');
        return null;
    }
    
    if (!data.email) {
        console.error('❌ Email é obrigatório');
        return null;
    }
    
    if (!data.aceita_termos) {
        console.error('❌ Aceitar termos é obrigatório');
        return null;
    }
    
    console.log('✅ Dados básicos coletados:', data);
    return data;
}

// ===================================
// CORREÇÃO: Script da Arrumadeira
// Também precisa ser atualizado
// ===================================

function collectSpecificFormData(form) {
    const formData = new FormData(form);
    
    const specificData = {
        organizacao_closet: formData.get('organizacaoCloset'),
        lavar_passar: formData.get('lavarPassar'),
        perfil_desejado: formData.get('perfilDesejadoArrumadeira'),
        caracteristicas_evitar: formData.get('caracteristicasEvitarArrumadeira')
    };
    
    console.log('📋 Dados específicos da arrumadeira:', specificData);
    return specificData;
}

function collectArrayFields(form, fieldName) {
    const checkboxes = form.querySelectorAll(`input[name="${fieldName}"]:checked`);
    const values = Array.from(checkboxes).map(cb => cb.value);
    console.log(`📋 Array coletado [${fieldName}]:`, values);
    return values;
}

function cleanPhoneFormat(phone) {
    if (!phone) return null;
    return phone.replace(/\D/g, '');
}

function cleanSalaryFormat(salary) {
    if (!salary) return null;
    return salary.replace(/[R$\s.]/g, '').replace(',', '.');
}

function validateRequiredFields(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidField = null;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
        } else {
            field.classList.remove('error');
        }
    });
    
    if (!isTermsAccepted()) {
        isValid = false;
        console.error('❌ Termos de serviço não foram aceitos');
    }
    
    if (!isValid && firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    return isValid;
}

async function submitVagaToSupabase(vagaData) {
    console.log('📤 Enviando vaga para Supabase:', vagaData);
    
    if (!checkSupabaseConnection()) {
        return { success: false, error: 'Supabase não disponível' };
    }
    
    try {
        showLoadingState(true);
        
        const { data, error } = await window.supabase
            .from('vagas')
            .insert([vagaData])
            .select();
        
        if (error) {
            console.error('❌ Erro do Supabase:', error);
            throw error;
        }
        
        console.log('✅ Vaga cadastrada com sucesso:', data);
        return { success: true, data: data[0] };
        
    } catch (error) {
        console.error('❌ Erro ao enviar vaga:', error);
        return { 
            success: false, 
            error: error.message || 'Erro desconhecido ao cadastrar vaga' 
        };
    } finally {
        showLoadingState(false);
    }
}

function showLoadingState(show) {
    const submitButton = document.querySelector('.btn-submit');
    if (!submitButton) return;
    
    if (show) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando vaga...';
    } else {
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Cadastrar Vaga';
    }
}

function showSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function showErrorModal(errorMessage) {
    if (!document.getElementById('errorModal')) {
        alert(`❌ Erro ao cadastrar vaga:\n\n${errorMessage}\n\nTente novamente ou entre em contato conosco.`);
        return;
    }
    
    const modal = document.getElementById('errorModal');
    const errorText = modal.querySelector('.error-message');
    if (errorText) {
        errorText.textContent = errorMessage;
    }
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const successModal = document.getElementById('successModal');
    const errorModal = document.getElementById('errorModal');
    
    if (successModal) {
        successModal.style.display = 'none';
        window.location.href = '/';
    }
    
    if (errorModal) {
        errorModal.style.display = 'none';
    }
    
    document.body.style.overflow = 'auto';
}

// ===================================
// FUNÇÕES EXISTENTES
// ===================================

function openTermosModal() {
    const modal = document.getElementById('termosModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeTermosModal() {
    const modal = document.getElementById('termosModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        const aceitarRadio = document.querySelector('input[name="aceitaTermos"][value="sim"]');
        if (aceitarRadio) {
            aceitarRadio.checked = true;
            
            const rejectionMessage = document.querySelector('.rejection-message');
            if (rejectionMessage) {
                rejectionMessage.classList.remove('show');
            }
            unlockOwnerFormSections();
        }
    }
}

function loadOwnerFormSection(sectionName, containerId) {
    try {
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`❌ Container ${containerId} não encontrado`);
            return;
        }
        
        if (!ownerFormSections[sectionName]) {
            console.error(`❌ Seção ${sectionName} não existe`);
            container.innerHTML = `
                <div style="padding: 20px; background: rgba(231, 76, 60, 0.1); border: 2px solid #e74c3c; border-radius: 10px; text-align: center; color: #e74c3c;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Seção "${sectionName}" não encontrada</p>
                    <small>Seções disponíveis: aceitar-termos, dados-proprietario, caracteristicas-residencia, etc.</small>
                </div>
            `;
            return;
        }
        
        container.innerHTML = ownerFormSections[sectionName];
        console.log(`✅ Seção ${sectionName} carregada com sucesso`);
        
        initializeOwnerSectionFunctionality(sectionName);
        
    } catch (error) {
        console.error(`❌ Erro ao carregar seção ${sectionName}:`, error);
    }
}

function initializeOwnerSectionFunctionality(sectionName) {
    switch(sectionName) {
        case 'aceitar-termos':
            initializeAceitarTermos();
            break;
        case 'dados-proprietario':
            initializeDadosProprietario();
            break;
        case 'caracteristicas-residencia':
            initializeCaracteristicasResidencia();
            break;
        case 'detalhes-vaga':
            initializeDetalhesVaga();
            break;
        case 'oferta-salarial':
            initializeOfertaSalarial();
            break;
        case 'requisitos-basicos':
            initializeRequisitosBasicos();
            break;
    }
}

function toggleInfoAgencia() {
    const infoDiv = document.querySelector('.info-agencia');
    if (infoDiv) {
        infoDiv.style.display = infoDiv.style.display === 'none' ? 'block' : 'none';
    }
}

function toggleInfoTreinamento() {
    const infoDiv = document.querySelector('.info-treinamento');
    if (infoDiv) {
        infoDiv.style.display = infoDiv.style.display === 'none' ? 'block' : 'none';
    }
}

function initializeAceitarTermos() {
    const aceitaTermos = document.querySelectorAll('input[name="aceitaTermos"]');
    const rejectionMessage = document.querySelector('.rejection-message');
    
    blockOwnerFormSections();
    
    document.body.classList.add('owner-form');
    aceitaTermos.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'sim') {
                rejectionMessage.classList.remove('show');
                unlockOwnerFormSections();
            } else {
                rejectionMessage.classList.add('show');
                blockOwnerFormSections();
            }
        });
    });
}

function initializeDadosProprietario() {
    const telefonePrincipal = document.getElementById('telefonePrincipal');
    const telefoneOpcional = document.getElementById('telefoneOpcional');
    
    function aplicarMascaraTelefone(campo) {
        if (campo) {
            campo.addEventListener('input', function(e) {
                let valor = e.target.value.replace(/\D/g, '');
                let valorFormatado = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                e.target.value = valorFormatado;
            });
        }
    }
    
    aplicarMascaraTelefone(telefonePrincipal);
    aplicarMascaraTelefone(telefoneOpcional);
}

function initializeCaracteristicasResidencia() {
    const temPets = document.querySelectorAll('input[name="temPets"]');
    const petsDetails = document.querySelector('.pets-details');
    
    temPets.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'sim') {
                petsDetails.classList.add('show');
            } else {
                petsDetails.classList.remove('show');
            }
        });
    });
    
    const tipoResidencia = document.querySelectorAll('input[name="tipoResidencia"]');
    const frequenciaVeraneio = document.querySelector('.frequencia-veraneio');
    
    tipoResidencia.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'casa-verao' || this.value === 'ambas') {
                frequenciaVeraneio.classList.add('show');
            } else {
                frequenciaVeraneio.classList.remove('show');
            }
        });
    });
}

function initializeDetalhesVaga() {
    console.log('Detalhes da vaga inicializados');
}

function initializeOfertaSalarial() {
    const salarioInput = document.getElementById('salarioOferecido');
    if (salarioInput) {
        salarioInput.addEventListener('input', function(e) {
            let valor = e.target.value.replace(/\D/g, '');
            let valorFormatado = 'R$ ' + valor.replace(/(\d)(\d{3})(\d{2})$/, '$1.$2,$3');
            e.target.value = valorFormatado;
        });
    }
    
    const outrosCheckbox = document.querySelector('input[name="beneficios"][value="outros"]');
    const outrosBeneficios = document.querySelector('.outros-beneficios');
    
    if (outrosCheckbox) {
        outrosCheckbox.addEventListener('change', function() {
            if (this.checked) {
                outrosBeneficios.classList.add('show');
            } else {
                outrosBeneficios.classList.remove('show');
            }
        });
    }
}

function initializeRequisitosBasicos() {
    const temIdadeMinima = document.querySelectorAll('input[name="temIdadeMinima"]');
    const idadeMinimaDetails = document.querySelector('.idade-minima-details');
    
    temIdadeMinima.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'sim') {
                idadeMinimaDetails.classList.add('show');
            } else {
                idadeMinimaDetails.classList.remove('show');
            }
        });
    });

    const experienciaObrigatoria = document.querySelectorAll('input[name="experienciaObrigatoria"]');
    const experienciaDetails = document.querySelector('.experiencia-details');
    
    experienciaObrigatoria.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'sim') {
                experienciaDetails.classList.add('show');
            } else {
                experienciaDetails.classList.remove('show');
            }
        });
    });
}

function isTermsAccepted() {
    const aceita = document.querySelector('input[name="aceitaTermos"]:checked');
    return aceita && aceita.value === 'sim';
}

function blockOwnerFormSections() {
    const staticSections = document.querySelectorAll('.form-section:not(.treinamento-section)');
    const dynamicContainers = document.querySelectorAll('#dados-proprietario-container, #caracteristicas-residencia-container, #detalhes-vaga-container, #oferta-salarial-container, #requisitos-basicos-container, #treinamento-personalizado-container, #observacoes-adicionais-container');
    const dynamicSections = document.querySelectorAll('#dados-proprietario-container .form-section, #caracteristicas-residencia-container .form-section, #detalhes-vaga-container .form-section, #oferta-salarial-container .form-section, #requisitos-basicos-container .form-section, #treinamento-personalizado-container .form-section, #observacoes-adicionais-container .form-section');
    const submitBtn = document.querySelector('.btn-submit');
    
    staticSections.forEach(section => {
        section.classList.add('form-locked');
        section.classList.remove('form-unlocked');
    });
    
    dynamicContainers.forEach(container => {
        container.classList.add('form-locked');
        container.classList.remove('form-unlocked');
    });
    
    dynamicSections.forEach(section => {
        section.classList.add('form-locked');
        section.classList.remove('form-unlocked');
    });
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
    }
    
    console.log('🔒 Formulário bloqueado - Aceite os termos para continuar');
}

function unlockOwnerFormSections() {
    const staticSections = document.querySelectorAll('.form-section:not(.treinamento-section)');
    const dynamicContainers = document.querySelectorAll('#dados-proprietario-container, #caracteristicas-residencia-container, #detalhes-vaga-container, #oferta-salarial-container, #requisitos-basicos-container, #treinamento-personalizado-container, #observacoes-adicionais-container');
    const dynamicSections = document.querySelectorAll('#dados-proprietario-container .form-section, #caracteristicas-residencia-container .form-section, #detalhes-vaga-container .form-section, #oferta-salarial-container .form-section, #requisitos-basicos-container .form-section, #treinamento-personalizado-container .form-section, #observacoes-adicionais-container .form-section');
    const submitBtn = document.querySelector('.btn-submit');
    
    staticSections.forEach(section => {
        section.classList.remove('form-locked');
        section.classList.add('form-unlocked');
    });
    
    dynamicContainers.forEach(container => {
        container.classList.remove('form-locked');
        container.classList.add('form-unlocked');
    });
    
    dynamicSections.forEach(section => {
        section.classList.remove('form-locked');
        section.classList.add('form-unlocked');
    });
    
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    }
    
    console.log('✅ Formulário desbloqueado! Termos aceitos.');
}

// CORREÇÃO ESPECÍFICA PARA global-section-prop.js
// ADICIONE ESTA FUNÇÃO NO FINAL DO ARQUIVO global-section-prop.js

// ========================================
// CORREÇÃO CAMPOS CONDICIONAIS PROPRIETÁRIOS
// ========================================

function fixConditionalFieldsProprietarios() {
    console.log('🔧 Corrigindo campos condicionais proprietários...');
    
    // FUNÇÃO PARA GERENCIAR REQUIRED EM CAMPOS CONDICIONAIS
    function setupFieldToggle(radioName, containerSelector) {
        const radios = document.querySelectorAll(`input[name="${radioName}"]`);
        const container = document.querySelector(containerSelector);
        
        if (!radios.length || !container) {
            console.warn(`⚠️ Não encontrado: ${radioName} ou ${containerSelector}`);
            return;
        }
        
        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                const allFields = container.querySelectorAll('input, select, textarea');
                
                if (this.value === 'sim' && this.checked) {
                    // SIM: mostrar e tornar obrigatório
                    container.style.display = 'block';
                    container.classList.remove('hidden');
                    container.classList.add('show');
                    
                    allFields.forEach(field => {
                        if (field.dataset.originalRequired === 'true' || field.hasAttribute('data-required')) {
                            field.setAttribute('required', 'required');
                        }
                    });
                    
                    console.log(`✅ ${radioName}: Campos mostrados e required adicionado`);
                } else {
                    // NÃO: esconder e remover obrigatório
                    container.style.display = 'none';
                    container.classList.add('hidden');
                    container.classList.remove('show');
                    
                    allFields.forEach(field => {
                        field.removeAttribute('required');
                        field.value = ''; // Limpar valor
                    });
                    
                    console.log(`❌ ${radioName}: Campos escondidos e required removido`);
                }
            });
        });
    }
    
    // AGUARDAR ELEMENTOS CARREGAREM
    setTimeout(() => {
        // CAMPOS CONDICIONAIS COMUNS EM FORMULÁRIOS DE PROPRIETÁRIOS
        setupFieldToggle('experienciaMinima', '.experiencia-details');
        setupFieldToggle('experienciaMinima', '.experiencia-minima');
        setupFieldToggle('experienciaMinima', '[class*="experiencia"]');
        setupFieldToggle('temExperiencia', '.experiencia-details');
        setupFieldToggle('temPets', '.pets-details');
        setupFieldToggle('temAnimais', '.animais-details');
        setupFieldToggle('dormirTrabalho', '.dormir-detalhes');
        setupFieldToggle('cuidadosEspeciais', '.cuidados-especiais-details');
        setupFieldToggle('inicio_urgente', '.urgente-details');
        
        // CORREÇÃO IMEDIATA: Remover required de campos hidden
        document.querySelectorAll('[style*="display: none"] [required], [style*="display:none"] [required], .hidden [required]').forEach(field => {
            field.removeAttribute('required');
            field.value = '';
            console.log(`🧹 Required removido de campo hidden: ${field.name}`);
        });
        
        console.log('✅ Campos condicionais configurados para proprietários');
    }, 1000);
}

// ========================================
// VALIDAÇÃO CUSTOMIZADA PARA PROPRIETÁRIOS
// ========================================

function validateRequiredFieldsCustom(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidField = null;
    
    requiredFields.forEach(field => {
        // VERIFICAR SE O CAMPO ESTÁ REALMENTE VISÍVEL
        const isVisible = field.offsetParent !== null && 
                         getComputedStyle(field).display !== 'none' &&
                         !field.closest('[style*="display: none"]') &&
                         !field.closest('.hidden');
        
        // SÓ VALIDAR SE ESTIVER VISÍVEL
        if (isVisible && !field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            field.style.border = '2px solid red';
            
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
            
            console.error(`❌ Campo obrigatório vazio: ${field.name}`);
        } else {
            field.classList.remove('error');
            field.style.border = '';
        }
    });
    
    // VERIFICAR TERMOS DE SERVIÇO
    if (!isTermsAccepted()) {
        isValid = false;
        console.error('❌ Termos de serviço não foram aceitos');
    }
    
    if (!isValid && firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        alert('Por favor, preencha todos os campos obrigatórios destacados em vermelho.');
    }
    
    return isValid;
}

// ========================================
// SUBSTITUIR FUNÇÃO ORIGINAL
// ========================================

// Backup da função original
if (typeof window.validateRequiredFields !== 'undefined') {
    window.validateRequiredFields_original = window.validateRequiredFields;
}

// Substituir por versão corrigida
window.validateRequiredFields = validateRequiredFieldsCustom;

// ========================================
// AUTO-INICIALIZAR
// ========================================

// Inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixConditionalFieldsProprietarios);
} else {
    fixConditionalFieldsProprietarios();
}

// Também inicializar após delay (caso seções demorem para carregar)
setTimeout(fixConditionalFieldsProprietarios, 2000);

console.log('🔧 Sistema de correção de campos condicionais para proprietários carregado');

// FUNÇÃO PARA DEBUG MANUAL
window.debugFormFields = function() {
    const form = document.querySelector('form');
    const required = form.querySelectorAll('[required]');
    const hidden = form.querySelectorAll('[style*="display: none"] [required], .hidden [required]');
    
    console.log('📊 Debug Formulário:', {
        'Total required': required.length,
        'Required hidden': hidden.length,
        'Campos hidden': Array.from(hidden).map(f => f.name)
    });
    
    // Destacar campos problemáticos
    hidden.forEach(field => {
        field.style.backgroundColor = 'red';
        console.log(`🔴 Campo problemático: ${field.name}`);
    });
};

function loadAllOwnerStandardSections() {
    loadOwnerFormSection('aceitar-termos', 'aceitar-termos-container');
    loadOwnerFormSection('dados-proprietario', 'dados-proprietario-container');
    loadOwnerFormSection('caracteristicas-residencia', 'caracteristicas-residencia-container');
    loadOwnerFormSection('detalhes-vaga', 'detalhes-vaga-container');
    loadOwnerFormSection('oferta-salarial', 'oferta-salarial-container');
    loadOwnerFormSection('requisitos-basicos', 'requisitos-basicos-container');
    loadOwnerFormSection('treinamento-personalizado', 'treinamento-personalizado-container');
    loadOwnerFormSection('observacoes-adicionais', 'observacoes-adicionais-container');
}

