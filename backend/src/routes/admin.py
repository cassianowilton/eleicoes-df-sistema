"""
Rotas do painel administrativo simplificado
"""
from flask import Blueprint, request, jsonify, session
import os
import hashlib

admin_bp = Blueprint('admin', __name__)

# Senha simples para acesso admin (em produção usar hash)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def verificar_autenticacao():
    """Verifica se o usuário está autenticado"""
    return session.get('admin_authenticated', False)

@admin_bp.route('/login', methods=['POST'])
def login():
    """Login simples para o painel admin"""
    data = request.get_json()
    
    if not data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Senha é obrigatória'
        }), 400
    
    password = data['password']
    
    if password == ADMIN_PASSWORD:
        session['admin_authenticated'] = True
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Senha incorreta'
        }), 401

@admin_bp.route('/logout', methods=['POST'])
def logout():
    """Logout do painel admin"""
    session.pop('admin_authenticated', None)
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso'
    })

@admin_bp.route('/status', methods=['GET'])
def status_auth():
    """Verifica status de autenticação"""
    return jsonify({
        'authenticated': verificar_autenticacao()
    })

@admin_bp.route('/config/llm', methods=['GET'])
def get_config_llm():
    """Obtém configuração atual dos LLMs"""
    if not verificar_autenticacao():
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Configuração atual (sem expor API keys completas)
    config = {
        'provider_ativo': os.environ.get('PREFERRED_LLM', 'openai'),
        'fallback_habilitado': os.environ.get('ENABLE_LLM_FALLBACK', 'true').lower() == 'true',
        'openai_configurado': bool(os.environ.get('OPENAI_API_KEY')),
        'deepseek_configurado': bool(os.environ.get('DEEPSEEK_API_KEY')),
        'openai_key_preview': '***' + os.environ.get('OPENAI_API_KEY', '')[-4:] if os.environ.get('OPENAI_API_KEY') else '',
        'deepseek_key_preview': '***' + os.environ.get('DEEPSEEK_API_KEY', '')[-4:] if os.environ.get('DEEPSEEK_API_KEY') else ''
    }
    
    return jsonify({
        'success': True,
        'config': config
    })

@admin_bp.route('/config/llm', methods=['POST'])
def set_config_llm():
    """Configura LLMs (apenas para sessão atual)"""
    if not verificar_autenticacao():
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Dados são obrigatórios'
        }), 400
    
    try:
        # Importar LLM service para atualizar configurações
        from src.services.llm_service import llm_service
        
        # Atualizar provedor preferido
        if 'provider_ativo' in data:
            provider = data['provider_ativo']
            if provider in ['openai', 'deepseek']:
                llm_service.preferred_provider = provider
        
        # Atualizar fallback
        if 'fallback_habilitado' in data:
            llm_service.enable_fallback = bool(data['fallback_habilitado'])
        
        # Atualizar API keys (temporariamente na sessão)
        if 'openai_api_key' in data and data['openai_api_key']:
            os.environ['OPENAI_API_KEY'] = data['openai_api_key']
            # Reconfigurar OpenAI
            llm_service._setup_providers()
        
        if 'deepseek_api_key' in data and data['deepseek_api_key']:
            os.environ['DEEPSEEK_API_KEY'] = data['deepseek_api_key']
            # Reconfigurar DeepSeek
            llm_service._setup_providers()
        
        return jsonify({
            'success': True,
            'message': 'Configuração atualizada com sucesso',
            'config': {
                'provider_ativo': llm_service.preferred_provider,
                'fallback_habilitado': llm_service.enable_fallback,
                'providers_disponiveis': llm_service.get_available_providers()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao atualizar configuração: {str(e)}'
        }), 500

@admin_bp.route('/test/llm', methods=['POST'])
def testar_llm():
    """Testa configuração atual dos LLMs"""
    if not verificar_autenticacao():
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        from src.services.llm_service import llm_service
        
        # Testar provedor específico ou todos
        data = request.get_json() or {}
        provider = data.get('provider')
        
        if provider:
            # Testar provedor específico
            result = llm_service.chat_completion(
                messages=[{"role": "user", "content": "Responda apenas 'OK' para testar."}],
                provider=provider,
                max_tokens=10
            )
            
            return jsonify({
                'success': True,
                'provider': provider,
                'resultado': result
            })
        else:
            # Testar todos os provedores
            results = llm_service.test_providers()
            
            return jsonify({
                'success': True,
                'resultados': results
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao testar LLMs: {str(e)}'
        }), 500

@admin_bp.route('/stats', methods=['GET'])
def estatisticas_simples():
    """Estatísticas básicas do sistema"""
    if not verificar_autenticacao():
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        from src.services.llm_service import llm_service
        
        status = llm_service.get_status()
        
        stats = {
            'providers_ativos': len(status['available_providers']),
            'provider_preferido': status['preferred_provider'],
            'fallback_ativo': status['fallback_enabled'],
            'total_providers': status['total_providers'],
            'sistema_funcionando': len(status['available_providers']) > 0
        }
        
        return jsonify({
            'success': True,
            'estatisticas': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao obter estatísticas: {str(e)}'
        }), 500

