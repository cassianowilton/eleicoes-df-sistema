"""
Serviço de IA para processamento de linguagem natural
Integrado com múltiplos LLMs via LLMService
"""
import json
import re
from typing import Dict, Any, List
from .llm_service import llm_service

def processar_pergunta(pergunta: str, provider: str = None) -> Dict[str, Any]:
    """
    Processa pergunta em linguagem natural usando IA
    
    Args:
        pergunta: Pergunta do usuário
        provider: Provedor específico de LLM (opcional)
    
    Returns:
        Dict com análise da pergunta
    """
    
    # Prompt melhorado para análise de consultas eleitorais
    prompt = f"""
Você é um assistente especializado em análise de dados eleitorais do Distrito Federal 2022.

CONTEXTO DOS DADOS:
- 590 candidatos a deputado distrital
- 19 zonas eleitorais
- 6.748 seções eleitorais  
- 107 locais de votação
- 1.535.545 votos totais

MAPEAMENTO DE REGIÕES → ZONAS:
- Brasília/Plano Piloto → Zona 1
- Gama → Zona 2  
- Taguatinga → Zona 3
- Brazlândia → Zona 4
- Sobradinho → Zona 5
- Planaltina → Zona 6
- Núcleo Bandeirante → Zona 8
- Ceilândia → Zona 9
- Guará → Zona 10
- Cruzeiro → Zona 11
- Sobradinho II → Zona 13
- Samambaia → Zona 14
- São Sebastião → Zona 15
- Recanto das Emas → Zona 16
- Lago Sul → Zona 17
- Riacho Fundo → Zona 18
- Águas Claras → Zona 19
- Vicente Pires → Zona 20
- Paranoá → Zona 21

TIPOS DE CONSULTA DISPONÍVEIS:
1. mais_votados - Top candidatos geral
2. candidatos_zona - Candidatos por zona/região
3. buscar_candidato - Buscar por nome
4. votos_candidato_regiao - Votos de candidato por região(ões)
5. votos_candidato_secao - Votos de candidato por seção
6. comparar_regioes - Comparar votação entre regiões
7. ranking_local - Ranking por local de votação
8. estatisticas - Estatísticas gerais
9. zonas - Listar zonas
10. locais - Listar locais

EXEMPLOS DE ANÁLISE:
- "Top 5 candidatos" → tipo: mais_votados, limite: 5
- "Candidatos em Ceilândia" → tipo: candidatos_zona, zona: 9, regiao: "ceilândia"
- "Buscar João Silva" → tipo: buscar_candidato, nome_candidato: "João Silva"
- "Quantos votos Fábio Felix teve em Taguatinga?" → tipo: votos_candidato_regiao, candidato_especifico: "Fábio Felix", regiao: "taguatinga"
- "Votos de Marcos na seção 123" → tipo: votos_candidato_secao, candidato_especifico: "Marcos", secao: 123
- "Comparar Ceilândia e Samambaia" → tipo: comparar_regioes, regioes_comparar: ["ceilândia", "samambaia"]

PERGUNTA DO USUÁRIO: "{pergunta}"

Analise a pergunta e retorne APENAS um JSON válido com:
{{
    "tipo_consulta": "tipo_identificado",
    "parametros": {{
        "limite": numero_se_aplicavel,
        "zona": numero_zona_se_aplicavel,
        "regiao": "nome_regiao_se_aplicavel",
        "nome_candidato": "nome_se_busca",
        "candidato_especifico": "nome_candidato_se_consulta_especifica",
        "secao": numero_secao_se_aplicavel,
        "regioes_comparar": ["regiao1", "regiao2"],
        "local_votacao": "nome_local_se_aplicavel"
    }},
    "explicacao": "breve_explicacao_da_analise"
}}

Se não conseguir identificar, retorne:
{{
    "tipo_consulta": "erro",
    "parametros": {{}},
    "explicacao": "Não foi possível entender a pergunta"
}}
"""

    messages = [
        {"role": "system", "content": "Você é um assistente especializado em análise de consultas eleitorais. Responda sempre em JSON válido."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        # Usar LLM service com fallback automático
        result = llm_service.chat_completion(
            messages=messages,
            provider=provider,
            temperature=0.1,
            max_tokens=500
        )
        
        if not result['success']:
            return {
                'tipo_consulta': 'erro',
                'parametros': {},
                'explicacao': f'Erro na IA: {result.get("error", "Erro desconhecido")}',
                'provider_info': result
            }
        
        # Tentar parsear JSON da resposta
        try:
            analise = json.loads(result['content'])
            
            # Adicionar informações do provedor usado
            analise['provider_info'] = {
                'provider': result['provider'],
                'model': result['model'],
                'cost': result.get('cost', {}),
                'usage': result.get('usage', {})
            }
            
            return analise
            
        except json.JSONDecodeError:
            # Fallback: tentar extrair JSON da resposta
            json_match = re.search(r'\{.*\}', result['content'], re.DOTALL)
            if json_match:
                try:
                    analise = json.loads(json_match.group())
                    analise['provider_info'] = {
                        'provider': result['provider'],
                        'model': result['model']
                    }
                    return analise
                except:
                    pass
            
            return {
                'tipo_consulta': 'erro',
                'parametros': {},
                'explicacao': 'Resposta da IA não está em formato JSON válido',
                'raw_response': result['content'],
                'provider_info': result
            }
    
    except Exception as e:
        return {
            'tipo_consulta': 'erro',
            'parametros': {},
            'explicacao': f'Erro ao processar pergunta: {str(e)}'
        }

def gerar_resposta_natural(pergunta: str, dados: Dict[str, Any], provider: str = None) -> str:
    """
    Gera resposta em linguagem natural baseada nos dados
    
    Args:
        pergunta: Pergunta original do usuário
        dados: Dados retornados pela consulta
        provider: Provedor específico de LLM (opcional)
    
    Returns:
        Resposta em linguagem natural
    """
    
    prompt = f"""
Você é um assistente especializado em eleições do DF 2022.

PERGUNTA DO USUÁRIO: "{pergunta}"

DADOS ENCONTRADOS: {json.dumps(dados, ensure_ascii=False, indent=2)}

Gere uma resposta natural, clara e informativa baseada nos dados. 

DIRETRIZES:
- Use linguagem brasileira informal mas profissional
- Destaque os números mais importantes
- Se houver muitos resultados, foque nos principais
- Use emojis moderadamente (📊, 🗳️, 🏆)
- Seja conciso mas completo
- Se não houver dados, explique de forma amigável

FORMATO DA RESPOSTA:
- Resposta direta à pergunta
- Principais resultados com números
- Contexto adicional se relevante
"""

    messages = [
        {"role": "system", "content": "Você é um assistente especializado em dados eleitorais. Responda de forma natural e informativa."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        result = llm_service.chat_completion(
            messages=messages,
            provider=provider,
            temperature=0.3,
            max_tokens=800
        )
        
        if result['success']:
            return result['content']
        else:
            return f"Encontrei os dados solicitados, mas tive dificuldade para formatá-los. Consulte os dados retornados para mais detalhes."
    
    except Exception as e:
        return f"Dados encontrados com sucesso. Erro na formatação da resposta: {str(e)}"

def obter_status_ia() -> Dict[str, Any]:
    """Retorna status completo do serviço de IA"""
    return llm_service.get_status()

def testar_provedores() -> Dict[str, Any]:
    """Testa todos os provedores de LLM"""
    return llm_service.test_providers()

