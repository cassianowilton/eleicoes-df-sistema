"""
Serviço unificado para gerenciar múltiplos LLMs (OpenAI, DeepSeek)
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.providers = {
            'openai': {
                'client': None,
                'api_key': os.environ.get('OPENAI_API_KEY'),
                'api_base': os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
                'model': 'gpt-4o-mini',
                'cost_per_1k_tokens': 0.00015,  # USD
                'available': False
            },
            'deepseek': {
                'client': None,
                'api_key': os.environ.get('DEEPSEEK_API_KEY'),
                'api_base': os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
                'model': 'deepseek-chat',
                'cost_per_1k_tokens': 0.00014,  # USD (mais barato)
                'available': False
            }
        }
        
        # Configurar clientes disponíveis
        self._setup_providers()
        
        # Provider preferido (configurável via env)
        self.preferred_provider = os.environ.get('PREFERRED_LLM', 'openai')
        
        # Fallback automático
        self.enable_fallback = os.environ.get('ENABLE_LLM_FALLBACK', 'true').lower() == 'true'
        
    def _setup_providers(self):
        """Configura os provedores de LLM disponíveis"""
        
        # Configurar OpenAI
        if self.providers['openai']['api_key']:
            try:
                self.providers['openai']['client'] = OpenAI(
                    api_key=self.providers['openai']['api_key'],
                    base_url=self.providers['openai']['api_base']
                )
                self.providers['openai']['available'] = True
                print("✅ OpenAI configurado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao configurar OpenAI: {e}")
        
        # Configurar DeepSeek
        if self.providers['deepseek']['api_key']:
            try:
                self.providers['deepseek']['client'] = OpenAI(
                    api_key=self.providers['deepseek']['api_key'],
                    base_url=self.providers['deepseek']['api_base']
                )
                self.providers['deepseek']['available'] = True
                print("✅ DeepSeek configurado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao configurar DeepSeek: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        return [name for name, config in self.providers.items() if config['available']]
    
    def get_provider_info(self, provider: str = None) -> Dict[str, Any]:
        """Retorna informações sobre um provedor específico ou todos"""
        if provider:
            if provider in self.providers:
                config = self.providers[provider].copy()
                # Remove informações sensíveis
                config.pop('client', None)
                config.pop('api_key', None)
                return config
            return {}
        
        # Retorna info de todos os provedores
        info = {}
        for name, config in self.providers.items():
            provider_info = config.copy()
            provider_info.pop('client', None)
            provider_info.pop('api_key', None)
            info[name] = provider_info
        
        return info
    
    def chat_completion(self, messages: List[Dict], provider: str = None, **kwargs) -> Dict[str, Any]:
        """
        Executa chat completion com fallback automático
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            provider: Provedor específico ou None para usar o preferido
            **kwargs: Parâmetros adicionais (temperature, max_tokens, etc.)
        
        Returns:
            Dict com resposta e metadados
        """
        
        # Determinar ordem de tentativa
        providers_to_try = []
        
        if provider and provider in self.providers and self.providers[provider]['available']:
            providers_to_try.append(provider)
        elif self.preferred_provider in self.providers and self.providers[self.preferred_provider]['available']:
            providers_to_try.append(self.preferred_provider)
        
        # Adicionar outros provedores para fallback
        if self.enable_fallback:
            for name in self.providers:
                if name not in providers_to_try and self.providers[name]['available']:
                    providers_to_try.append(name)
        
        if not providers_to_try:
            return {
                'error': 'Nenhum provedor de LLM disponível',
                'success': False
            }
        
        # Tentar cada provedor
        last_error = None
        for provider_name in providers_to_try:
            try:
                result = self._execute_completion(provider_name, messages, **kwargs)
                if result['success']:
                    return result
                last_error = result.get('error', 'Erro desconhecido')
            except Exception as e:
                last_error = str(e)
                continue
        
        return {
            'error': f'Todos os provedores falharam. Último erro: {last_error}',
            'success': False,
            'providers_tried': providers_to_try
        }
    
    def _execute_completion(self, provider: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Executa completion em um provedor específico"""
        
        if provider not in self.providers or not self.providers[provider]['available']:
            return {
                'error': f'Provedor {provider} não disponível',
                'success': False
            }
        
        config = self.providers[provider]
        client = config['client']
        
        # Parâmetros padrão
        params = {
            'model': config['model'],
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.1),
            'max_tokens': kwargs.get('max_tokens', 1000)
        }
        
        try:
            response = client.chat.completions.create(**params)
            
            # Calcular custo estimado
            total_tokens = response.usage.total_tokens if response.usage else 0
            estimated_cost = (total_tokens / 1000) * config['cost_per_1k_tokens']
            
            return {
                'success': True,
                'provider': provider,
                'model': config['model'],
                'content': response.choices[0].message.content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                    'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                    'total_tokens': total_tokens
                },
                'cost': {
                    'estimated_usd': round(estimated_cost, 6),
                    'estimated_brl': round(estimated_cost * 5.5, 4)  # Conversão aproximada
                }
            }
            
        except Exception as e:
            return {
                'error': f'Erro no {provider}: {str(e)}',
                'success': False,
                'provider': provider
            }
    
    def test_providers(self) -> Dict[str, Any]:
        """Testa todos os provedores disponíveis"""
        results = {}
        test_messages = [
            {"role": "user", "content": "Responda apenas 'OK' para testar a conexão."}
        ]
        
        for provider in self.get_available_providers():
            result = self._execute_completion(provider, test_messages, max_tokens=10)
            results[provider] = {
                'available': result['success'],
                'response_time': None,  # Poderia medir tempo de resposta
                'error': result.get('error') if not result['success'] else None
            }
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do serviço"""
        return {
            'providers': self.get_provider_info(),
            'available_providers': self.get_available_providers(),
            'preferred_provider': self.preferred_provider,
            'fallback_enabled': self.enable_fallback,
            'total_providers': len(self.providers),
            'active_providers': len(self.get_available_providers())
        }

# Instância global do serviço
llm_service = LLMService()

