// API com integração real de IA (OpenAI e DeepSeek)
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
        
        // Mapeamento de regiões para zonas
        this.regioes = {
            'ceilândia': 9,
            'taguatinga': 3,
            'brasília': 1,
            'plano piloto': 1,
            'gama': 2,
            'sobradinho': 4,
            'planaltina': 5,
            'paranoá': 6,
            'núcleo bandeirante': 7,
            'riacho fundo': 8,
            'santa maria': 10,
            'são sebastião': 11,
            'recanto das emas': 12,
            'lago sul': 13,
            'riacho fundo ii': 14,
            'samambaia': 15,
            'águas claras': 16,
            'vicente pires': 17,
            'sudoeste': 18,
            'varjão': 19
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
    
    // Função para chamar API OpenAI
    async callOpenAI(prompt) {
        const config = this.loadConfig();
        if (!config.openai_key) {
            throw new Error('API Key OpenAI não configurada');
        }
        
        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.openai_key}`
                },
                body: JSON.stringify({
                    model: 'gpt-4o-mini',
                    messages: [
                        {
                            role: 'system',
                            content: `Você é um assistente especializado em análise de dados eleitorais do DF 2022.
                            
DADOS DISPONÍVEIS:
- 1.535.545 votos totais
- 590 candidatos
- 19 zonas eleitorais
- 6.748 seções eleitorais

CANDIDATOS MAIS VOTADOS:
1. VOTO BRANCO: 107.572 votos
2. FRANCISCO DOMINGOS DOS SANTOS: 43.854 votos  
3. FÁBIO FELIX SILVEIRA: 40.775 votos
4. Partido Liberal: 32.408 votos
5. MARCOS MARTINS MACHADO: 31.993 votos

MAPEAMENTO REGIÕES → ZONAS:
- Ceilândia: Zona 9
- Taguatinga: Zona 3  
- Brasília/Plano Piloto: Zona 1
- Gama: Zona 2
- Samambaia: Zona 15

INSTRUÇÕES:
- Responda APENAS sobre eleições DF 2022
- Use dados reais fornecidos
- Seja preciso e objetivo
- Formate com emojis e markdown`
                        },
                        {
                            role: 'user',
                            content: prompt
                        }
                    ],
                    max_tokens: 500,
                    temperature: 0.3
                })
            });
            
            if (!response.ok) {
                throw new Error(`OpenAI API Error: ${response.status}`);
            }
            
            const data = await response.json();
            return data.choices[0].message.content;
            
        } catch (error) {
            throw new Error(`Erro OpenAI: ${error.message}`);
        }
    }
    
    // Função para chamar API DeepSeek
    async callDeepSeek(prompt) {
        const config = this.loadConfig();
        if (!config.deepseek_key) {
            throw new Error('API Key DeepSeek não configurada');
        }
        
        try {
            const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${config.deepseek_key}`
                },
                body: JSON.stringify({
                    model: 'deepseek-chat',
                    messages: [
                        {
                            role: 'system',
                            content: `Você é um assistente especializado em análise de dados eleitorais do DF 2022.
                            
DADOS DISPONÍVEIS:
- 1.535.545 votos totais
- 590 candidatos  
- 19 zonas eleitorais
- 6.748 seções eleitorais

CANDIDATOS MAIS VOTADOS:
1. VOTO BRANCO: 107.572 votos
2. FRANCISCO DOMINGOS DOS SANTOS: 43.854 votos
3. FÁBIO FELIX SILVEIRA: 40.775 votos
4. Partido Liberal: 32.408 votos
5. MARCOS MARTINS MACHADO: 31.993 votos

MAPEAMENTO REGIÕES → ZONAS:
- Ceilândia: Zona 9
- Taguatinga: Zona 3
- Brasília/Plano Piloto: Zona 1  
- Gama: Zona 2
- Samambaia: Zona 15

INSTRUÇÕES:
- Responda APENAS sobre eleições DF 2022
- Use dados reais fornecidos
- Seja preciso e objetivo
- Formate com emojis e markdown`
                        },
                        {
                            role: 'user', 
                            content: prompt
                        }
                    ],
                    max_tokens: 500,
                    temperature: 0.3
                })
            });
            
            if (!response.ok) {
                throw new Error(`DeepSeek API Error: ${response.status}`);
            }
            
            const data = await response.json();
            return data.choices[0].message.content;
            
        } catch (error) {
            throw new Error(`Erro DeepSeek: ${error.message}`);
        }
    }
    
    // Função principal de consulta com IA real
    async consulta(pergunta) {
        const config = this.loadConfig();
        
        try {
            let resposta;
            
            // Tentar com o provedor preferido
            if (config.ia_provider === 'openai' && config.openai_key) {
                try {
                    resposta = await this.callOpenAI(pergunta);
                } catch (error) {
                    console.log('Erro OpenAI:', error.message);
                    
                    // Fallback para DeepSeek se habilitado
                    if (config.fallback && config.deepseek_key) {
                        console.log('Tentando fallback para DeepSeek...');
                        resposta = await this.callDeepSeek(pergunta);
                    } else {
                        throw error;
                    }
                }
            } else if (config.ia_provider === 'deepseek' && config.deepseek_key) {
                try {
                    resposta = await this.callDeepSeek(pergunta);
                } catch (error) {
                    console.log('Erro DeepSeek:', error.message);
                    
                    // Fallback para OpenAI se habilitado
                    if (config.fallback && config.openai_key) {
                        console.log('Tentando fallback para OpenAI...');
                        resposta = await this.callOpenAI(pergunta);
                    } else {
                        throw error;
                    }
                }
            } else {
                // Nenhuma API configurada, usar consulta local
                return this.consultaLocal(pergunta);
            }
            
            return {
                success: true,
                pergunta: pergunta,
                resposta: resposta,
                provider: config.ia_provider,
                fallback_used: false
            };
            
        } catch (error) {
            console.log('Erro na consulta IA:', error.message);
            
            // Fallback para consulta local se tudo falhar
            return this.consultaLocal(pergunta);
        }
    }
    
    // Consulta local (fallback final)
    consultaLocal(pergunta) {
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
            
            resposta += `\n💡 *Consulta processada localmente*`;
            
            return {
                success: true,
                pergunta: pergunta,
                resposta: resposta,
                provider: 'local',
                fallback_used: true
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
                    resposta += `\n💡 *Consulta processada localmente*`;
                    
                    return {
                        success: true,
                        pergunta: pergunta,
                        resposta: resposta,
                        provider: 'local',
                        fallback_used: true
                    };
                } else {
                    return {
                        success: true,
                        pergunta: pergunta,
                        resposta: `❌ Nenhum candidato encontrado com '${nomeBusca}'\n\n💡 *Consulta processada localmente*`,
                        provider: 'local',
                        fallback_used: true
                    };
                }
            }
        }
        
        if (perguntaLower.includes('estatísticas') || perguntaLower.includes('dados')) {
            const resposta = `📊 **Estatísticas Eleições DF 2022:**

• **Total de votos**: ${this.estatisticas.total_votos.toLocaleString()}
• **Candidatos**: ${this.estatisticas.total_candidatos}
• **Zonas eleitorais**: ${this.estatisticas.zonas_eleitorais}
• **Seções eleitorais**: ${this.estatisticas.secoes_eleitorais.toLocaleString()}
• **Locais de votação**: ${this.estatisticas.locais_votacao}
• **Sistema**: Operacional ✅

💡 *Consulta processada localmente*`;
            
            return {
                success: true,
                pergunta: pergunta,
                resposta: resposta,
                provider: 'local',
                fallback_used: true
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
• "Quantos votos [candidato] teve em [região]?"
• "Comparar [região1] com [região2]"

**Exemplos com IA:**
• "Quantos votos Fábio Felix teve em Ceilândia?"
• "Comparar votação entre Taguatinga e Gama"

💡 *Para consultas avançadas, configure API Keys no painel admin*`,
            provider: 'local',
            fallback_used: true
        };
    }
    
    status() {
        const config = this.loadConfig();
        return {
            success: true,
            status: 'online',
            database: 'simulated',
            ia_provider: config.ia_provider,
            openai_configured: !!config.openai_key,
            deepseek_configured: !!config.deepseek_key,
            fallback_enabled: config.fallback,
            version: '2.0.0'
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

