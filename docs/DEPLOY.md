# 🚀 Guia de Deploy - Vercel

## Passo a Passo Completo

### 1. Preparação do Repositório

#### 1.1 Criar Repositório no GitHub
```bash
# No GitHub, criar novo repositório: eleicoes-df-sistema
# Copiar URL do repositório
```

#### 1.2 Conectar Repositório Local
```bash
git remote add origin https://github.com/SEU_USUARIO/eleicoes-df-sistema.git
git add .
git commit -m "Initial commit - Sistema Eleições DF 2022"
git push -u origin main
```

### 2. Configuração no Vercel

#### 2.1 Criar Conta e Conectar GitHub
1. Acesse [vercel.com](https://vercel.com)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione o repositório `eleicoes-df-sistema`

#### 2.2 Configurações de Build
- **Framework Preset:** Other
- **Root Directory:** `./`
- **Build Command:** (deixar vazio)
- **Output Directory:** `frontend`

#### 2.3 Variáveis de Ambiente
Adicione no painel do Vercel:

```
SUPABASE_HOST=db.ixnxgfkgcdfimdkvtqzk.supabase.co
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=postgres.ixnxgfkgcdfimdkvtqzk
SUPABASE_PASSWORD=SdR3deS#2025
OPENAI_API_KEY=sua_chave_openai
OPENAI_API_BASE=https://api.openai.com/v1
SECRET_KEY=eleicoes-df-2022-secret-key-production
```

### 3. Deploy

#### 3.1 Deploy Inicial
1. Clique em "Deploy"
2. Aguarde o build completar
3. Teste a URL gerada

#### 3.2 Configurar Domínio (Opcional)
1. No painel Vercel, vá em "Domains"
2. Adicione seu domínio personalizado
3. Configure DNS conforme instruções

### 4. Configuração WhatsApp

#### 4.1 Webhook URL
Após deploy, a URL do webhook será:
```
https://seu-projeto.vercel.app/api/whatsapp/webhook
```

#### 4.2 Configurar Evolution API
1. Acesse painel da Evolution API
2. Configure webhook URL
3. Teste envio de mensagem

### 5. Monitoramento

#### 5.1 Logs
- Acesse "Functions" no painel Vercel
- Monitore logs em tempo real
- Configure alertas se necessário

#### 5.2 Analytics
- Ative Vercel Analytics
- Monitore performance
- Acompanhe uso da API

### 6. Deploy Automático

#### 6.1 Configuração
- Push para `main` = deploy automático
- Pull requests = preview deploy
- Rollback automático em caso de erro

#### 6.2 Branches
```bash
# Desenvolvimento
git checkout -b develop
git push origin develop

# Produção
git checkout main
git merge develop
git push origin main
```

### 7. Troubleshooting

#### 7.1 Erros Comuns
- **Build Error:** Verificar requirements.txt
- **Runtime Error:** Verificar variáveis de ambiente
- **Database Error:** Verificar credenciais Supabase

#### 7.2 Logs Úteis
```bash
# Ver logs do Vercel CLI
vercel logs

# Ver status do deploy
vercel ls
```

### 8. Backup e Segurança

#### 8.1 Backup do Código
- Repositório GitHub = backup automático
- Tags para versões estáveis

#### 8.2 Backup do Banco
- Supabase faz backup automático
- Export manual se necessário

#### 8.3 Segurança
- Variáveis de ambiente seguras
- HTTPS automático
- Rate limiting configurado

## ✅ Checklist Final

- [ ] Repositório GitHub criado
- [ ] Projeto Vercel configurado
- [ ] Variáveis de ambiente definidas
- [ ] Deploy realizado com sucesso
- [ ] API funcionando
- [ ] Frontend carregando
- [ ] WhatsApp configurado
- [ ] Monitoramento ativo

## 🆘 Suporte

Em caso de problemas:
1. Verificar logs no Vercel
2. Testar endpoints individualmente
3. Validar variáveis de ambiente
4. Consultar documentação Vercel

