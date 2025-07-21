# 🗳️ Sistema de Análise Eleitoral DF 2022

Sistema inteligente para análise de dados eleitorais do Distrito Federal 2022, com IA integrada e suporte ao WhatsApp.

## 📊 Funcionalidades

- ✅ **API REST** para consultas eleitorais
- ✅ **Inteligência Artificial** para consultas em linguagem natural
- ✅ **Integração WhatsApp** via Evolution API
- ✅ **Dashboard Administrativo** com controle de acesso
- ✅ **Banco de Dados** Supabase PostgreSQL
- ✅ **Deploy Automático** via Vercel

## 🏗️ Arquitetura

```
├── backend/           # API Flask
│   ├── src/
│   │   ├── main.py           # Aplicação principal
│   │   ├── routes/           # Endpoints da API
│   │   └── services/         # Serviços (IA, WhatsApp)
│   └── requirements.txt
├── frontend/          # Interface web
│   └── index.html            # Dashboard principal
├── docs/             # Documentação
└── vercel.json       # Configuração de deploy
```

## 🚀 Deploy

### Pré-requisitos
- Conta no [Vercel](https://vercel.com)
- Conta no [Supabase](https://supabase.com)
- API Key OpenAI ou DeepSeek

### Variáveis de Ambiente
```bash
# Banco de Dados
SUPABASE_HOST=db.ixnxgfkgcdfimdkvtqzk.supabase.co
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=postgres.ixnxgfkgcdfimdkvtqzk
SUPABASE_PASSWORD=sua_senha

# IA
OPENAI_API_KEY=sua_chave_openai
OPENAI_API_BASE=https://api.openai.com/v1

# WhatsApp (Opcional)
EVOLUTION_API_URL=sua_url_evolution
EVOLUTION_API_KEY=sua_chave_evolution
```

### Deploy Automático
1. Conecte o repositório ao Vercel
2. Configure as variáveis de ambiente
3. Deploy automático a cada push

## 📱 Uso via WhatsApp

Exemplos de consultas:
- "Top 10 candidatos mais votados"
- "Candidatos mais votados em Ceilândia"
- "Quantos votos Fábio Felix teve em Taguatinga?"
- "Comparar votação entre Samambaia e Gama"

## 🔗 Endpoints da API

### Consultas Básicas
- `GET /api/candidatos/mais-votados` - Top candidatos
- `GET /api/candidatos/buscar?nome=X` - Buscar candidato
- `GET /api/zona/{numero}/candidatos` - Candidatos por zona
- `GET /api/estatisticas` - Estatísticas gerais

### IA e WhatsApp
- `POST /api/consulta-natural` - Consulta com IA
- `GET /api/whatsapp/status` - Status WhatsApp
- `POST /api/whatsapp/webhook` - Webhook WhatsApp

## 📊 Dados

- **1.535.545** votos totais
- **590** candidatos únicos
- **19** zonas eleitorais
- **6.748** seções eleitorais
- **107** locais de votação

## 🛠️ Desenvolvimento Local

```bash
# Backend
cd backend
pip install -r requirements.txt
python src/main.py

# Frontend
cd frontend
# Abrir index.html no navegador
```

## 📝 Licença

Este projeto é desenvolvido para análise de dados públicos eleitorais.

## 🤝 Contribuição

Desenvolvido por SD Redes para análise transparente de dados eleitorais do DF.

