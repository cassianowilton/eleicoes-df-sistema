"""
Rotas para gerenciamento de LLMs (OpenAI, DeepSeek)
"""
from flask import Blueprint, request, jsonify
from src.services.llm_service import llm_service
from src.services import ia_service

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/status', methods=['GET'])
def status_llm():
    """Retorna status de todos os provedores de LLM"""
    try:
        status = llm_service.get_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/providers', methods=['GET'])
def listar_provedores():
    """Lista todos os provedores disponíveis"""
    try:
        providers = llm_service.get_available_providers()
        provider_info = llm_service.get_provider_info()
        
        return jsonify({
            'success': True,
            'available_providers': providers,
            'provider_details': provider_info,
            'total_available': len(providers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/test', methods=['POST'])
def testar_provedores():
    """Testa todos os provedores de LLM"""
    try:
        results = llm_service.test_providers()
        return jsonify({
            'success': True,
            'test_results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/test/<provider>', methods=['POST'])
def testar_provedor_especifico(provider):
    """Testa um provedor específico"""
    try:
        if provider not in llm_service.get_available_providers():
            return jsonify({
                'success': False,
                'error': f'Provedor {provider} não disponível'
            }), 400
        
        # Teste simples
        result = llm_service.chat_completion(
            messages=[{"role": "user", "content": "Responda apenas 'OK' para testar."}],
            provider=provider,
            max_tokens=10
        )
        
        return jsonify({
            'success': True,
            'provider': provider,
            'test_result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/consulta-comparativa', methods=['POST'])
def consulta_comparativa():
    """Executa a mesma consulta em múltiplos provedores para comparação"""
    data = request.get_json()
    
    if not data or 'pergunta' not in data:
        return jsonify({
            'success': False,
            'error': 'Campo pergunta é obrigatório'
        }), 400
    
    pergunta = data['pergunta']
    providers_solicitados = data.get('providers', llm_service.get_available_providers())
    
    try:
        resultados = {}
        
        for provider in providers_solicitados:
            if provider in llm_service.get_available_providers():
                try:
                    resultado = ia_service.processar_pergunta(pergunta, provider=provider)
                    resultados[provider] = {
                        'success': True,
                        'resultado': resultado,
                        'provider_info': resultado.get('provider_info', {})
                    }
                except Exception as e:
                    resultados[provider] = {
                        'success': False,
                        'error': str(e)
                    }
        
        return jsonify({
            'success': True,
            'pergunta': pergunta,
            'resultados': resultados,
            'total_testados': len(resultados)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/configurar-preferido', methods=['POST'])
def configurar_provedor_preferido():
    """Configura o provedor preferido (apenas para sessão atual)"""
    data = request.get_json()
    
    if not data or 'provider' not in data:
        return jsonify({
            'success': False,
            'error': 'Campo provider é obrigatório'
        }), 400
    
    provider = data['provider']
    
    try:
        if provider not in llm_service.get_available_providers():
            return jsonify({
                'success': False,
                'error': f'Provedor {provider} não disponível'
            }), 400
        
        # Atualizar provedor preferido (apenas para esta sessão)
        llm_service.preferred_provider = provider
        
        return jsonify({
            'success': True,
            'message': f'Provedor preferido alterado para {provider}',
            'provider': provider
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/custos', methods=['GET'])
def comparar_custos():
    """Compara custos entre provedores"""
    try:
        provider_info = llm_service.get_provider_info()
        
        custos = {}
        for provider, info in provider_info.items():
            if info.get('available'):
                custos[provider] = {
                    'model': info.get('model'),
                    'cost_per_1k_tokens_usd': info.get('cost_per_1k_tokens'),
                    'cost_per_1k_tokens_brl': round(info.get('cost_per_1k_tokens', 0) * 5.5, 6),
                    'available': info.get('available')
                }
        
        # Calcular economia
        if 'openai' in custos and 'deepseek' in custos:
            economia_usd = custos['openai']['cost_per_1k_tokens_usd'] - custos['deepseek']['cost_per_1k_tokens_usd']
            economia_percentual = (economia_usd / custos['openai']['cost_per_1k_tokens_usd']) * 100
            
            custos['comparacao'] = {
                'economia_usd_por_1k_tokens': round(economia_usd, 6),
                'economia_brl_por_1k_tokens': round(economia_usd * 5.5, 6),
                'economia_percentual': round(economia_percentual, 2)
            }
        
        return jsonify({
            'success': True,
            'custos': custos
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/estatisticas', methods=['GET'])
def estatisticas_uso():
    """Retorna estatísticas de uso dos LLMs (placeholder)"""
    try:
        # Em uma implementação real, isso viria de um banco de dados
        # Por agora, retornamos dados simulados
        
        stats = {
            'total_consultas': 0,
            'consultas_por_provider': {},
            'custo_total_estimado': {
                'usd': 0.0,
                'brl': 0.0
            },
            'uptime': '100%',
            'provider_preferido': llm_service.preferred_provider,
            'fallback_habilitado': llm_service.enable_fallback
        }
        
        return jsonify({
            'success': True,
            'estatisticas': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

