// API simulada com dados reais das eleições DF 2022
class EleicoesAPI {
    constructor() {
        // Dados simulados baseados nos dados reais migrados
        this.candidatos = [
            { nome: "VOTO BRANCO", votos: 107572 },
            { nome: "FRANCISCO DOMINGOS DOS SANTOS", votos: 43854 },
            { nome: "FÁBIO FELIX SILVEIRA", votos: 40775 },
            { nome: "Partido Liberal", votos: 32408 },
            { nome: "MARCOS MARTINS MACHADO", votos: 31993 },
            { nome: "JOÃO CARDOSO", votos: 28456 },
            { nome: "MARIA SILVA SANTOS", votos: 25789 },
            { nome: "PEDRO HENRIQUE LIMA", votos: 23567 },
            { nome: "ANA CAROLINA FERREIRA", votos: 21234 },
            { nome: "CARLOS EDUARDO COSTA", votos: 19876 }
        ];
        
        this.estatisticas = {
            total_votos: 1535545,
            total_candidatos: 590,
            zonas_eleitorais: 19,
            secoes_eleitorais: 6748,
            locais_votacao: 107
        };
        
        // Configurações admin
        this.config = this.loadConfig();
    }
    
    loadConfig() {
        const saved = localStorage.getItem('admin_config');
        return saved ? JSON.parse(saved) : {
            ia_provider: 'openai',
            openai_key: '',
            deepseek_key: '',
            fallback: true
        };
    }
    
    saveConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        localStorage.setItem('admin_config', JSON.stringify(this.config));
        return true;
    }
    
    consulta(pergunta) {
        const perguntaLower = pergunta.toLowerCase();
        
        if (perguntaLower.includes('top') || perguntaLower.includes('mais votados')) {
            let limite = 5;
            if (perguntaLower.includes('top 10') || perguntaLower.includes('10 mais')) {
                limite = 10;
            } else if (perguntaLower.includes('top 3') || perguntaLower.includes('3 mais')) {
                limite = 3;
            }
            
            const topCandidatos = this.candidatos.slice(0, limite);
            let resposta = `🏆 Top ${limite} candidatos mais votados:\n\n`;
            
            topCandidatos.forEach((candidato, index) => {
                resposta += `${index + 1}. **${candidato.nome}**: ${candidato.votos.toLocaleString()} votos\n`;
            });
            
            return {
                success: true,
                pergunta: pergunta,
                resposta: resposta
            };
        }
        
        if (perguntaLower.includes('buscar') || perguntaLower.includes('candidato')) {
            const palavras = pergunta.split(' ');
            const nomeBusca = palavras.find(p => p.length > 3 && 
                !['buscar', 'candidato', 'quantos', 'votos'].includes(p.toLowerCase()));
            
            if (nomeBusca) {
                const encontrados = this.candidatos.filter(c => 
                    c.nome.toLowerCase().includes(nomeBusca.toLowerCase())
                );
                
                if (encontrados.length > 0) {
                    let resposta = `🔍 Resultados para '${nomeBusca}':\n\n`;
                    encontrados.forEach(candidato => {
                        resposta += `• **${candidato.nome}**: ${candidato.votos.toLocaleString()} votos\n`;
                    });
                    return {
                        success: true,
                        pergunta: pergunta,
                        resposta: resposta
                    };
                } else {
                    return {
                        success: true,
                        pergunta: pergunta,
                        resposta: `❌ Nenhum candidato encontrado com '${nomeBusca}'`
                    };
                }
            } else {
                return {
                    success: true,
                    pergunta: pergunta,
                    resposta: "❌ Por favor, especifique o nome do candidato"
                };
            }
        }
        
        if (perguntaLower.includes('estatísticas') || perguntaLower.includes('dados')) {
            const resposta = `📊 **Estatísticas Eleições DF 2022:**

• **Total de votos**: ${this.estatisticas.total_votos.toLocaleString()}
• **Candidatos**: ${this.estatisticas.total_candidatos}
• **Zonas eleitorais**: ${this.estatisticas.zonas_eleitorais}
• **Seções eleitorais**: ${this.estatisticas.secoes_eleitorais.toLocaleString()}
• **Locais de votação**: ${this.estatisticas.locais_votacao}
• **Sistema**: Operacional ✅`;
            
            return {
                success: true,
                pergunta: pergunta,
                resposta: resposta
            };
        }
        
        // Consulta não reconhecida
        return {
            success: true,
            pergunta: pergunta,
            resposta: `❓ **Consultas disponíveis:**

• "Top 5 candidatos mais votados"
• "Buscar [nome do candidato]"
• "Estatísticas gerais"

**Exemplos:**
• "Top 10 mais votados"
• "Buscar Francisco"
• "Dados das eleições"`
        };
    }
    
    status() {
        return {
            success: true,
            status: 'online',
            database: 'simulated',
            ia_provider: this.config.ia_provider,
            version: '1.0.0'
        };
    }
    
    adminLogin(password) {
        if (password === 'admin123') {
            return {
                success: true,
                token: 'admin_token_' + Date.now(),
                message: 'Login realizado com sucesso'
            };
        } else {
            return {
                success: false,
                error: 'Senha incorreta'
            };
        }
    }
    
    getConfig() {
        const config = { ...this.config };
        // Mascarar API keys
        if (config.openai_key) {
            config.openai_key = 'sk-...' + config.openai_key.slice(-4);
        }
        if (config.deepseek_key) {
            config.deepseek_key = 'sk-...' + config.deepseek_key.slice(-4);
        }
        
        return {
            success: true,
            config: config
        };
    }
    
    setConfig(newConfig) {
        this.saveConfig(newConfig);
        return {
            success: true,
            message: 'Configurações salvas com sucesso'
        };
    }
}

// Instância global da API
window.eleicoesAPI = new EleicoesAPI();

