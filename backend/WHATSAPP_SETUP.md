# Configuração WhatsApp - API Eleições DF 2022

## Visão Geral

A API suporta integração com WhatsApp através de dois provedores:
- **Twilio WhatsApp API** (Recomendado para iniciantes)
- **Meta WhatsApp Business API** (Mais recursos, configuração complexa)

## Opção 1: Twilio WhatsApp API

### 1. Criar Conta Twilio
1. Acesse [console.twilio.com](https://console.twilio.com)
2. Crie uma conta gratuita
3. Verifique seu número de telefone

### 2. Configurar WhatsApp Sandbox
1. No console Twilio, vá para **Messaging > Try it out > Send a WhatsApp message**
2. Siga as instruções para ativar o sandbox
3. Anote o número do sandbox (ex: +1 415 523 8886)

### 3. Obter Credenciais
No console Twilio, encontre:
- **Account SID**: Identificador da conta
- **Auth Token**: Token de autenticação
- **Phone Number**: Número do WhatsApp (sandbox)

### 4. Configurar API
```bash
curl -X POST http://localhost:5000/api/whatsapp/config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "twilio",
    "account_sid": "SEU_ACCOUNT_SID",
    "auth_token": "SEU_AUTH_TOKEN",
    "phone_number": "+14155238886"
  }'
```

### 5. Configurar Webhook
1. No console Twilio, vá para **Phone Numbers > Manage > WhatsApp senders**
2. Clique no seu número sandbox
3. Configure o webhook URL: `https://SEU_DOMINIO/api/whatsapp/twilio/webhook`
4. Método: POST

## Opção 2: Meta WhatsApp Business API

### 1. Criar App Facebook
1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Crie um novo app tipo "Business"
3. Adicione o produto "WhatsApp"

### 2. Configurar WhatsApp Business
1. Configure um número de telefone
2. Obtenha o **Phone Number ID**
3. Gere um **Access Token**

### 3. Configurar API
```bash
curl -X POST http://localhost:5000/api/whatsapp/config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "meta",
    "access_token": "SEU_ACCESS_TOKEN",
    "phone_number_id": "SEU_PHONE_NUMBER_ID",
    "verify_token": "SEU_VERIFY_TOKEN"
  }'
```

### 4. Configurar Webhook
1. No Facebook Developers, configure o webhook
2. URL: `https://SEU_DOMINIO/api/whatsapp/webhook`
3. Verify Token: O mesmo definido na configuração
4. Subscreva aos eventos: `messages`

## Testando a Integração

### 1. Verificar Status
```bash
curl http://localhost:5000/api/whatsapp/status
```

### 2. Testar Envio
```bash
curl -X POST http://localhost:5000/api/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{
    "numero": "+5561999999999",
    "mensagem": "Teste da API Eleições DF 2022!"
  }'
```

## Usando o WhatsApp

### Comandos Disponíveis

**Consultas Gerais:**
- "Top 10 candidatos mais votados"
- "Estatísticas gerais"
- "Top 5"

**Por Região:**
- "Candidatos mais votados em Ceilândia"
- "Top 10 em Taguatinga"
- "Deputados mais votados na zona 9"

**Busca por Nome:**
- "Buscar João Silva"
- "Procurar Francisco"
- "Candidato Maria"

### Exemplos de Respostas

**Pergunta:** "Top 5 candidatos mais votados"

**Resposta:**
```
🏆 Top 5 Candidatos Mais Votados:

1. VOTO BRANCO
   📊 107,572 votos
   🔢 Número: 95

2. FRANCISCO DOMINGOS DOS SANTOS
   📊 43,854 votos
   🔢 Número: 13100

3. FÁBIO FELIX SILVEIRA
   📊 40,775 votos
   🔢 Número: 50123
```

## Endpoints da API

### Configuração
- `POST /api/whatsapp/config` - Configurar credenciais
- `GET /api/whatsapp/status` - Status da configuração

### Webhooks
- `GET /api/whatsapp/webhook` - Verificação (Meta)
- `POST /api/whatsapp/webhook` - Receber mensagens (Meta)
- `POST /api/whatsapp/twilio/webhook` - Receber mensagens (Twilio)

### Testes
- `POST /api/whatsapp/test` - Testar envio de mensagem

## Limitações

### Twilio Sandbox
- Apenas números pré-aprovados podem receber mensagens
- Para produção, precisa de número próprio aprovado
- Limite de mensagens gratuitas

### Meta WhatsApp Business
- Processo de aprovação mais complexo
- Requer verificação de negócio
- Mais recursos disponíveis

## Produção

Para usar em produção:

1. **Twilio**: Compre um número dedicado e solicite aprovação
2. **Meta**: Complete o processo de verificação de negócio
3. **SSL**: Configure HTTPS para os webhooks
4. **Domínio**: Use um domínio próprio para os webhooks

## Troubleshooting

### Mensagens não chegam
1. Verifique se o webhook está configurado corretamente
2. Confirme se as credenciais estão corretas
3. Teste a conectividade do webhook

### Erro 403 no webhook
- Verifique o verify_token (Meta)
- Confirme a URL do webhook

### Erro 500 na API
- Verifique os logs do servidor
- Confirme se o banco de dados está acessível
- Teste os endpoints da API diretamente

