"""
Rotas para integração com WhatsApp
Suporta Twilio WhatsApp API e Meta WhatsApp Business API
"""

from flask import Blueprint, request, jsonify
import json
import requests
from src.services.ia_service import IAService
from src.routes.eleicoes import executar_consulta

whatsapp_bp = Blueprint('whatsapp', __name__)
ia_service = IAService()

# Configurações do WhatsApp (serão definidas via variáveis de ambiente)
WHATSAPP_CONFIG = {
    'provider': 'twilio',  # 'twilio' ou 'meta'
    'twilio': {
        'account_sid': '',  # Será configurado pelo usuário
        'auth_token': '',   # Será configurado pelo usuário
        'phone_number': ''  # Número do WhatsApp Business
    },
    'meta': {
        'access_token': '',     # Token da Meta
        'phone_number_id': '',  # ID do número de telefone
        'verify_token': ''      # Token de verificação do webhook
    }
}

def processar_mensagem_whatsapp(mensagem: str, numero_remetente: str) -> str:
    """
    Processa uma mensagem recebida via WhatsApp e retorna a resposta
    """
    try:
        # Usar IA para processar a pergunta
        analise = ia_service.processar_pergunta(mensagem)
        
        # Executar consulta baseada na análise
        resultado_dados = None
        
        if analise['tipo_consulta'] == 'mais_votados':
            limite = analise['parametros'].get('limite', 10)
            sql = """
                SELECT 
                    c.nm_votavel as nome,
                    c.nr_votavel as numero,
                    SUM(v.qt_votos) as total_votos
                FROM candidatos c
                JOIN votacao v ON c.sq_candidato = v.sq_candidato
                GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
                ORDER BY total_votos DESC
                LIMIT %s
            """
            resultados = executar_consulta(sql, [limite])
            if resultados:
                resposta = f"🏆 *Top {limite} Candidatos Mais Votados:*\n\n"
                for i, candidato in enumerate(resultados, 1):
                    resposta += f"{i}. *{candidato['nome']}*\n"
                    resposta += f"   📊 {candidato['total_votos']:,} votos\n"
                    resposta += f"   🔢 Número: {candidato['numero']}\n\n"
                return resposta
        
        elif analise['tipo_consulta'] == 'candidatos_zona':
            zona = analise['parametros'].get('zona')
            limite = analise['parametros'].get('limite', 10)
            regiao = analise['parametros'].get('regiao', f'Zona {zona}')
            
            if zona:
                sql = """
                    SELECT 
                        c.nm_votavel as nome,
                        c.nr_votavel as numero,
                        SUM(v.qt_votos) as total_votos
                    FROM candidatos c
                    JOIN votacao v ON c.sq_candidato = v.sq_candidato
                    WHERE v.nr_zona = %s
                    GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
                    ORDER BY total_votos DESC
                    LIMIT %s
                """
                resultados = executar_consulta(sql, [zona, limite])
                if resultados:
                    resposta = f"🗳️ *Top {limite} Candidatos em {regiao.title()}:*\n\n"
                    for i, candidato in enumerate(resultados, 1):
                        resposta += f"{i}. *{candidato['nome']}*\n"
                        resposta += f"   📊 {candidato['total_votos']:,} votos\n"
                        resposta += f"   🔢 Número: {candidato['numero']}\n\n"
                    return resposta
        
        elif analise['tipo_consulta'] == 'buscar_candidato':
            nome = analise['parametros'].get('nome_candidato')
            if nome:
                sql = """
                    SELECT 
                        c.nm_votavel as nome,
                        c.nr_votavel as numero,
                        SUM(v.qt_votos) as total_votos,
                        COUNT(DISTINCT v.nr_zona) as zonas_com_votos
                    FROM candidatos c
                    LEFT JOIN votacao v ON c.sq_candidato = v.sq_candidato
                    WHERE UPPER(c.nm_votavel) LIKE UPPER(%s)
                    GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
                    ORDER BY total_votos DESC NULLS LAST
                    LIMIT 5
                """
                nome_busca = f"%{nome}%"
                resultados = executar_consulta(sql, [nome_busca])
                if resultados:
                    resposta = f"🔍 *Resultados para '{nome}':*\n\n"
                    for candidato in resultados:
                        resposta += f"👤 *{candidato['nome']}*\n"
                        resposta += f"   📊 {candidato['total_votos']:,} votos\n"
                        resposta += f"   🔢 Número: {candidato['numero']}\n"
                        resposta += f"   🗺️ Presente em {candidato['zonas_com_votos']} zonas\n\n"
                    return resposta
                else:
                    return f"❌ Nenhum candidato encontrado com o nome '{nome}'"
        
        elif analise['tipo_consulta'] == 'estatisticas':
            # Buscar estatísticas gerais
            sql_votos = "SELECT SUM(qt_votos) as total_votos FROM votacao"
            sql_candidatos = "SELECT COUNT(*) as total_candidatos FROM candidatos"
            sql_zonas = "SELECT COUNT(*) as total_zonas FROM zonas_eleitorais"
            
            total_votos = executar_consulta(sql_votos)
            total_candidatos = executar_consulta(sql_candidatos)
            total_zonas = executar_consulta(sql_zonas)
            
            resposta = "📊 *Estatísticas Eleições DF 2022:*\n\n"
            resposta += f"🗳️ Total de votos: {total_votos[0]['total_votos']:,}\n"
            resposta += f"👥 Total de candidatos: {total_candidatos[0]['total_candidatos']}\n"
            resposta += f"🗺️ Total de zonas: {total_zonas[0]['total_zonas']}\n\n"
            resposta += "💡 *Dica:* Digite 'top 5' para ver os mais votados!"
            return resposta
        
        # Resposta padrão se não conseguir processar
        return """❓ *Não entendi sua pergunta.*

🤖 *Exemplos do que posso fazer:*
• "Top 10 candidatos mais votados"
• "Candidatos mais votados em Ceilândia"
• "Buscar João Silva"
• "Estatísticas gerais"
• "Top 5 na zona 9"

💬 *Digite sua pergunta sobre as eleições DF 2022!*"""
        
    except Exception as e:
        print(f"Erro ao processar mensagem WhatsApp: {e}")
        return "❌ *Erro interno.* Tente novamente em alguns instantes."

def enviar_mensagem_twilio(numero_destino: str, mensagem: str) -> bool:
    """
    Envia mensagem via Twilio WhatsApp API
    """
    try:
        from twilio.rest import Client
        
        account_sid = WHATSAPP_CONFIG['twilio']['account_sid']
        auth_token = WHATSAPP_CONFIG['twilio']['auth_token']
        from_number = WHATSAPP_CONFIG['twilio']['phone_number']
        
        if not all([account_sid, auth_token, from_number]):
            print("Configurações do Twilio não definidas")
            return False
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=mensagem,
            from_=f'whatsapp:{from_number}',
            to=f'whatsapp:{numero_destino}'
        )
        
        print(f"Mensagem enviada via Twilio: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar mensagem via Twilio: {e}")
        return False

def enviar_mensagem_meta(numero_destino: str, mensagem: str) -> bool:
    """
    Envia mensagem via Meta WhatsApp Business API
    """
    try:
        access_token = WHATSAPP_CONFIG['meta']['access_token']
        phone_number_id = WHATSAPP_CONFIG['meta']['phone_number_id']
        
        if not all([access_token, phone_number_id]):
            print("Configurações da Meta não definidas")
            return False
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messaging_product': 'whatsapp',
            'to': numero_destino,
            'type': 'text',
            'text': {'body': mensagem}
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Mensagem enviada via Meta: {response.json()}")
            return True
        else:
            print(f"Erro ao enviar via Meta: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro ao enviar mensagem via Meta: {e}")
        return False

@whatsapp_bp.route('/webhook', methods=['GET'])
def webhook_verificacao():
    """
    Endpoint para verificação do webhook (Meta WhatsApp)
    """
    verify_token = WHATSAPP_CONFIG['meta']['verify_token']
    
    # Verificar token do webhook
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == verify_token and challenge:
        return challenge
    else:
        return 'Token de verificação inválido', 403

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook_mensagem():
    """
    Endpoint para receber mensagens do WhatsApp
    """
    try:
        data = request.get_json()
        
        # Processar webhook da Meta
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        
                        # Verificar se há mensagens
                        if 'messages' in value:
                            for message in value['messages']:
                                numero_remetente = message.get('from')
                                tipo_mensagem = message.get('type')
                                
                                if tipo_mensagem == 'text':
                                    texto_mensagem = message['text']['body']
                                    
                                    # Processar mensagem
                                    resposta = processar_mensagem_whatsapp(texto_mensagem, numero_remetente)
                                    
                                    # Enviar resposta
                                    if WHATSAPP_CONFIG['provider'] == 'meta':
                                        enviar_mensagem_meta(numero_remetente, resposta)
                                    elif WHATSAPP_CONFIG['provider'] == 'twilio':
                                        enviar_mensagem_twilio(numero_remetente, resposta)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@whatsapp_bp.route('/twilio/webhook', methods=['POST'])
def twilio_webhook():
    """
    Endpoint específico para webhook do Twilio
    """
    try:
        # Dados do Twilio vêm como form data
        numero_remetente = request.form.get('From', '').replace('whatsapp:', '')
        texto_mensagem = request.form.get('Body', '')
        
        if numero_remetente and texto_mensagem:
            # Processar mensagem
            resposta = processar_mensagem_whatsapp(texto_mensagem, numero_remetente)
            
            # Resposta TwiML para Twilio
            from twilio.twiml.messaging_response import MessagingResponse
            
            twiml_response = MessagingResponse()
            twiml_response.message(resposta)
            
            return str(twiml_response), 200, {'Content-Type': 'text/xml'}
        
        return '', 200
        
    except Exception as e:
        print(f"Erro no webhook Twilio: {e}")
        return '', 500

@whatsapp_bp.route('/config', methods=['POST'])
def configurar_whatsapp():
    """
    Endpoint para configurar credenciais do WhatsApp
    """
    try:
        data = request.get_json()
        provider = data.get('provider', 'twilio')
        
        if provider == 'twilio':
            WHATSAPP_CONFIG['twilio'].update({
                'account_sid': data.get('account_sid', ''),
                'auth_token': data.get('auth_token', ''),
                'phone_number': data.get('phone_number', '')
            })
        elif provider == 'meta':
            WHATSAPP_CONFIG['meta'].update({
                'access_token': data.get('access_token', ''),
                'phone_number_id': data.get('phone_number_id', ''),
                'verify_token': data.get('verify_token', '')
            })
        
        WHATSAPP_CONFIG['provider'] = provider
        
        return jsonify({
            'status': 'success',
            'message': f'Configuração {provider} atualizada',
            'provider': provider
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@whatsapp_bp.route('/test', methods=['POST'])
def testar_whatsapp():
    """
    Endpoint para testar envio de mensagem
    """
    try:
        data = request.get_json()
        numero = data.get('numero')
        mensagem = data.get('mensagem', 'Teste de conexão - API Eleições DF 2022 🗳️')
        
        if not numero:
            return jsonify({'error': 'Número é obrigatório'}), 400
        
        # Tentar enviar mensagem
        sucesso = False
        if WHATSAPP_CONFIG['provider'] == 'meta':
            sucesso = enviar_mensagem_meta(numero, mensagem)
        elif WHATSAPP_CONFIG['provider'] == 'twilio':
            sucesso = enviar_mensagem_twilio(numero, mensagem)
        
        if sucesso:
            return jsonify({
                'status': 'success',
                'message': 'Mensagem enviada com sucesso',
                'provider': WHATSAPP_CONFIG['provider']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Falha ao enviar mensagem'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@whatsapp_bp.route('/status', methods=['GET'])
def status_whatsapp():
    """
    Verifica status da configuração do WhatsApp
    """
    provider = WHATSAPP_CONFIG['provider']
    configurado = False
    
    if provider == 'twilio':
        config = WHATSAPP_CONFIG['twilio']
        configurado = all([config['account_sid'], config['auth_token'], config['phone_number']])
    elif provider == 'meta':
        config = WHATSAPP_CONFIG['meta']
        configurado = all([config['access_token'], config['phone_number_id']])
    
    return jsonify({
        'provider': provider,
        'configurado': configurado,
        'webhook_url': request.url_root + 'api/whatsapp/webhook',
        'twilio_webhook_url': request.url_root + 'api/whatsapp/twilio/webhook'
    })

