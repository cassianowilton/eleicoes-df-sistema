# 🤖 Guia de Configuração - DeepSeek API

## 📋 Visão Geral

O sistema agora suporta múltiplos provedores de LLM:
- **OpenAI GPT-4o-mini** (padrão)
- **DeepSeek Chat** (alternativa mais barata)
- **Fallback automático** entre provedores

## 💰 Comparação de Custos

| Provedor | Modelo | Custo por 1K tokens | Economia vs OpenAI |
|----------|--------|-------------------|-------------------|
| OpenAI | gpt-4o-mini | $0.00015 | - |
| DeepSeek | deepseek-chat | $0.00014 | ~7% mais barato |

## 🔑 Configuração da API DeepSeek

### 1. Obter API Key
1. Acesse: https://platform.deepseek.com
2. Crie uma conta
3. Vá em "API Keys"
4. Gere uma nova chave

### 2. Configurar no Vercel
Adicione as variáveis de ambiente:

```bash
DEEPSEEK_API_KEY=sua_chave_deepseek_aqui
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
PREFERRED_LLM=deepseek
ENABLE_LLM_FALLBACK=true
```

### 3. Configurar Localmente
Crie arquivo `.env`:

```bash
# DeepSeek Configuration
DEEPSEEK_API_KEY=sua_chave_deepseek_aqui
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# LLM Preferences
PREFERRED_LLM=deepseek
ENABLE_LLM_FALLBACK=true

# OpenAI (Fallback)
OPENAI_API_KEY=sua_chave_openai
OPENAI_API_BASE=https://api.openai.com/v1
```

## 🔧 Endpoints da API

### Status dos LLMs
```bash
GET /api/llm/status
```

### Listar Provedores
```bash
GET /api/llm/providers
```

### Testar Provedores
```bash
POST /api/llm/test
```

### Comparar Custos
```bash
GET /api/llm/custos
```

### Consulta Comparativa
```bash
POST /api/llm/consulta-comparativa
{
  "pergunta": "Top 5 candidatos mais votados",
  "providers": ["openai", "deepseek"]
}
```

## 🎯 Funcionalidades

### 1. Fallback Automático
- Se DeepSeek falhar → OpenAI automaticamente
- Se OpenAI falhar → DeepSeek automaticamente
- Zero interrupção no serviço

### 2. Escolha de Provedor
```python
# Usar DeepSeek especificamente
ia_service.processar_pergunta("pergunta", provider="deepseek")

# Usar OpenAI especificamente  
ia_service.processar_pergunta("pergunta", provider="openai")

# Usar provedor preferido (automático)
ia_service.processar_pergunta("pergunta")
```

### 3. Monitoramento de Custos
- Custo estimado por consulta
- Comparação entre provedores
- Tracking de uso (futuro)

## 📊 Exemplo de Resposta

```json
{
  "tipo_consulta": "mais_votados",
  "parametros": {"limite": 5},
  "explicacao": "Buscar 5 candidatos mais votados",
  "provider_info": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "cost": {
      "estimated_usd": 0.000084,
      "estimated_brl": 0.0005
    },
    "usage": {
      "prompt_tokens": 450,
      "completion_tokens": 150,
      "total_tokens": 600
    }
  }
}
```

## 🔄 Deploy Automático

O sistema está configurado para deploy automático no Vercel:

1. **Push para GitHub** → Deploy automático
2. **Variáveis de ambiente** → Configuradas no Vercel
3. **Zero downtime** → Fallback garante disponibilidade

## 🛠️ Troubleshooting

### DeepSeek não funciona
1. Verificar API key válida
2. Verificar saldo na conta DeepSeek
3. Verificar conectividade com api.deepseek.com

### OpenAI como fallback
1. Sistema usa OpenAI automaticamente
2. Logs mostram qual provedor foi usado
3. Verificar `/api/llm/status` para diagnóstico

### Ambos falhando
1. Verificar conectividade de rede
2. Verificar variáveis de ambiente
3. Verificar logs do Vercel

## 📈 Próximos Passos

1. **Painel Admin** - Interface para configurar LLMs
2. **Estatísticas** - Tracking detalhado de uso
3. **Mais Provedores** - Claude, Gemini, etc.
4. **Cache** - Reduzir custos com cache inteligente

## 🎉 Benefícios

✅ **Economia de custos** com DeepSeek
✅ **Alta disponibilidade** com fallback
✅ **Flexibilidade** na escolha de provedor
✅ **Monitoramento** de custos e performance
✅ **Deploy automático** sem configuração manual

