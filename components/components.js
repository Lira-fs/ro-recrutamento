// components/components.js
class ComponentLoader {
    static getBasePath() {
         const path = window.location.pathname;
    
    // Lista de subpastas que precisam voltar um nível
    const subFolders = ['/formularios/', '/forms/', '/colab-forms/', '/vaga-forms/'];
    
    // Verificar se estamos em alguma subpasta
    const isInSubFolder = subFolders.some(folder => path.includes(folder));
    
    if (isInSubFolder) {
        console.log(`📍 Detectada subpasta. Usando caminho: ../../components/`);
        return '../../components/';  // ← MUDANÇA AQUI: 2 níveis em vez de 1
    } else {
        console.log(`📍 Pasta raiz detectada. Usando caminho: components/`);
        return 'components/';
    }
    }

    static async loadComponent(elementId, componentPath) {
        try {
            const response = await fetch(componentPath);
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            const html = await response.text();
            
            const container = document.getElementById(elementId);
            if (container) {
                container.innerHTML = html;
                console.log(`✅ Componente ${elementId} carregado de: ${componentPath}`);
                return true;
            } else {
                console.warn(`⚠️ Elemento com ID '${elementId}' não encontrado`);
                return false;
            }
        } catch (error) {
            console.error(`❌ Erro ao carregar ${componentPath}:`, error);
            return false;
        }
    }

    static async loadAllComponents() {
        const basePath = this.getBasePath();
        
        // Lista de componentes para carregar
        const components = [
            { id: 'header-container', path: `${basePath}header.html` },
            { id: 'footer-container', path: `${basePath}footer.html` }
        ];

        try {
            console.log('🔄 Iniciando carregamento dos componentes...');
            
            // Carregar todos os componentes
            const loadPromises = components.map(comp => 
                this.loadComponent(comp.id, comp.path)
            );
            
            await Promise.all(loadPromises);
            
            // Inicializar funcionalidades após carregar
            this.initializeComponents();
            
            console.log('✅ Todos os componentes carregados com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao carregar componentes:', error);
        }
    }

    static initializeComponents() {
        // Aguardar um pouco para o DOM se estabilizar
        setTimeout(() => {
            this.initMobileMenu();
            this.initNewsletter();
            this.initWhatsApp();
            this.initScrollHeader();
            console.log('🎯 Funcionalidades dos componentes inicializadas');
        }, 100);
    }

    static initMobileMenu() {
        const hamburger = document.getElementById('hamburger');
        const nav = document.getElementById('nav');
        
        if (hamburger && nav) {
            // Toggle menu mobile
            hamburger.addEventListener('click', (e) => {
                e.stopPropagation();
                hamburger.classList.toggle('active');
                nav.classList.toggle('active');
            });

            // Fechar menu ao clicar em link
            nav.addEventListener('click', (e) => {
                if (e.target.classList.contains('nav__link')) {
                    hamburger.classList.remove('active');
                    nav.classList.remove('active');
                }
            });

            // Fechar menu ao clicar fora
            document.addEventListener('click', (e) => {
                if (!nav.contains(e.target) && !hamburger.contains(e.target)) {
                    hamburger.classList.remove('active');
                    nav.classList.remove('active');
                }
            });

            console.log('📱 Menu mobile inicializado');
        } else {
            console.log('ℹ️ Elementos do menu mobile não encontrados (normal para formulários)');
        }
    }

    static initNewsletter() {
        const form = document.querySelector('.footer__newsletter-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const emailInput = form.querySelector('input[type="email"]');
                const email = emailInput.value.trim();
                
                if (email) {
                    // Aqui você pode integrar com sua API de newsletter
                    console.log('📧 Newsletter signup:', email);
                    
                    // Feedback visual
                    const btn = form.querySelector('.footer__newsletter-btn');
                    const originalText = btn.textContent;
                    
                    btn.textContent = 'Inscrito!';
                    btn.style.background = '#28a745';
                    
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.style.background = '';
                        emailInput.value = '';
                    }, 2000);
                    
                    alert('✅ Obrigado! Você receberá nossas novidades em breve.');
                }
            });
            
            console.log('📧 Newsletter inicializada');
        } else {
            console.log('ℹ️ Formulário de newsletter não encontrado');
        }
    }

    static initWhatsApp() {
        // Função global para WhatsApp
        window.openWhatsApp = function(message = 'Olá! Gostaria de saber mais sobre a R.O Recrutamento.') {
            const phone = '5511951072131';
            const encodedMessage = encodeURIComponent(message);
            const url = `https://wa.me/${phone}?text=${encodedMessage}`;
            window.open(url, '_blank');
        };

        // Adicionar evento aos links de WhatsApp
        document.addEventListener('click', (e) => {
            if (e.target.closest('[href*="wa.me"]') || e.target.closest('.header__whatsapp-btn')) {
                e.preventDefault();
                window.openWhatsApp();
            }
        });

        console.log('💬 WhatsApp inicializado');
    }

    static initScrollHeader() {
        const header = document.querySelector('.header');
        if (header) {
            let lastScrollY = window.scrollY;
            
            window.addEventListener('scroll', () => {
                const currentScrollY = window.scrollY;
                
                if (currentScrollY > lastScrollY && currentScrollY > 100) {
                    header.classList.add('header--hidden');
                } else {
                    header.classList.remove('header--hidden');
                }
                
                lastScrollY = currentScrollY;
            });
            
            console.log('📜 Scroll header inicializado');
        } else {
            console.log('ℹ️ Header não encontrado (pode ser formulário com header customizado)');
        }
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando carregador de componentes...');
    console.log(`📂 Caminho atual: ${window.location.pathname}`);
    ComponentLoader.loadAllComponents();
});

// Função global para rastreamento de eventos (opcional)
window.trackEvent = function(eventName, data = {}) {
    console.log('📊 Event tracked:', eventName, data);
    // Aqui você pode integrar com Google Analytics, etc.
};