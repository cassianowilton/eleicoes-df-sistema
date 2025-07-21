"""
Serviço de IA para processamento de linguagem natural
Converte perguntas em linguagem natural para consultas SQL
"""

import openai
import json
import re
from typing import Dict, Any, Optional

class IAService:
    def __init__(self):
        # A API key já está configurada no ambiente
        self.client = openai.OpenAI()
        
    def processar_pergunta(self, pergunta: str) -> Dict[str, Any]:
        """
        Processa uma pergunta em linguagem natural e retorna parâmetros para consulta
        """
        try:
            # Prompt para a IA entender a pergunta e extrair parâmetros
            prompt = f"""
Você é um assistente especializado em eleições do Distrito Federal de 2022 para Deputado Distrital.

Analise a pergunta do usuário e extraia os parâmetros necessários para fazer uma consulta no banco de dados.

PERGUNTA: "{pergunta}"

CONTEXTO DO BANCO DE DADOS:
- Tabela 'candidatos': nm_votavel (nome), nr_votavel (número), sq_candidato
- Tabela 'votacao': qt_votos (quantidade de votos), nr_zona, nr_secao
- Tabela 'zonas_eleitorais': nr_zona (1-21, exceto 7 e 12)
- Tabela 'locais_votacao': nm_local_votacao, ds_endereco
- Tabela 'secoes_eleitorais': nr_secao, nr_zona, nr_local_votacao

REGIÕES ADMINISTRATIVAS DO DF (Mapeamento Completo):
- Zona 1: Brasília/Plano Piloto (RA I - Brasília)
- Zona 2: Gama (RA II - Gama)  
- Zona 3: Taguatinga (RA III - Taguatinga)
- Zona 4: Brazlândia (RA IV - Brazlândia)
- Zona 5: Sobradinho (RA V - Sobradinho)
- Zona 6: Planaltina (RA VI - Planaltina)
- Zona 8: Núcleo Bandeirante (RA VIII - Núcleo Bandeirante)
- Zona 9: Ceilândia (RA IX - Ceilândia)
- Zona 10: Guará (RA X - Guará)
- Zona 11: Cruzeiro (RA XI - Cruzeiro)
- Zona 13: Sobradinho II (RA XXVI - Sobradinho II)
- Zona 14: Samambaia (RA XII - Samambaia)
- Zona 15: São Sebastião (RA XIV - São Sebastião)
- Zona 16: Recanto das Emas (RA XV - Recanto das Emas)
- Zona 17: Lago Sul (RA XVI - Lago Sul)
- Zona 18: Riacho Fundo (RA XVII - Riacho Fundo)
- Zona 19: Águas Claras (RA XX - Águas Claras)
- Zona 20: Vicente Pires (RA XXX - Vicente Pires)
- Zona 21: Paranoá (RA VII - Paranoá)

SINÔNIMOS E VARIAÇÕES:
- Brasília = Plano Piloto = Asa Norte = Asa Sul = RA I
- Ceilândia = Ceilandia = RA IX
- Taguatinga = Taguatinga Norte = Taguatinga Sul = RA III
- Águas Claras = Aguas Claras = RA XX
- São Sebastião = Sao Sebastiao = RA XIV
- Núcleo Bandeirante = Nucleo Bandeirante = Candangolândia = RA VIII

Retorne APENAS um JSON válido com os seguintes campos:
{{
    "tipo_consulta": "mais_votados|buscar_candidato|candidatos_zona|candidatos_regiao|votos_candidato_regiao|votos_candidato_secao|comparar_regioes|ranking_local|estatisticas|zonas|locais|erro",
    "parametros": {{
        "limite": número (padrão 10),
        "nome_candidato": "string ou null",
        "zona": número ou null,
        "regiao": "string ou null",
        "secao": número ou null,
        "local_votacao": "string ou null",
        "regioes_comparar": ["lista de regiões"] ou null,
        "candidato_especifico": "string ou null"
    }},
    "sql_sugerido": "consulta SQL sugerida ou null",
    "explicacao": "explicação da interpretação"
}}

EXEMPLOS DE CONSULTAS COMPLEXAS:
- "Quantos votos Fábio Felix teve em cada cidade?" → tipo: "votos_candidato_regiao", candidato_especifico: "Fábio Felix"
- "Votos do deputado João na seção 123" → tipo: "votos_candidato_secao", candidato_especifico: "João", secao: 123
- "Comparar votação entre Ceilândia e Taguatinga" → tipo: "comparar_regioes", regioes_comparar: ["Ceilândia", "Taguatinga"]
- "Candidato mais votado no Colégio X" → tipo: "ranking_local", local_votacao: "Colégio X"
- "Votos de Francisco Domingos em Samambaia" → tipo: "votos_candidato_regiao", candidato_especifico: "Francisco Domingos", regiao: "Samambaia"
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de dados eleitorais. Retorne apenas JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            resposta_ia = response.choices[0].message.content.strip()
            
            # Tentar extrair JSON da resposta
            try:
                # Remover possíveis marcadores de código
                resposta_ia = re.sub(r'```json\s*', '', resposta_ia)
                resposta_ia = re.sub(r'```\s*$', '', resposta_ia)
                
                resultado = json.loads(resposta_ia)
                return resultado
                
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON da IA: {e}")
                print(f"Resposta da IA: {resposta_ia}")
                return self._fallback_analysis(pergunta)
                
        except Exception as e:
            print(f"Erro na consulta à IA: {e}")
            return self._fallback_analysis(pergunta)
    
    def _fallback_analysis(self, pergunta: str) -> Dict[str, Any]:
        """
        Análise de fallback usando regex quando a IA falha
        """
        pergunta_lower = pergunta.lower()
        
        # Detectar números
        numeros = re.findall(r'\d+', pergunta)
        limite = int(numeros[0]) if numeros else 10
        
        # Detectar regiões/zonas (mapeamento completo)
        mapa_regioes = {
            'ceilândia': 9, 'ceilandia': 9,
            'taguatinga': 3, 'taguatinga norte': 3, 'taguatinga sul': 3,
            'samambaia': 14,
            'gama': 2,
            'planaltina': 6,
            'sobradinho': 5, 'sobradinho ii': 13,
            'brasília': 1, 'brasilia': 1, 'plano piloto': 1, 'asa norte': 1, 'asa sul': 1,
            'guará': 10, 'guara': 10,
            'águas claras': 19, 'aguas claras': 19,
            'vicente pires': 20,
            'são sebastião': 15, 'sao sebastiao': 15,
            'recanto das emas': 16,
            'paranoá': 21, 'paranoa': 21,
            'núcleo bandeirante': 8, 'nucleo bandeirante': 8, 'candangolândia': 8, 'candangolandia': 8,
            'cruzeiro': 11,
            'lago sul': 17,
            'riacho fundo': 18,
            'brazlândia': 4, 'brazlandia': 4
        }
        
        zona = None
        regiao = None
        for nome_regiao, nr_zona in mapa_regioes.items():
            if nome_regiao in pergunta_lower:
                zona = nr_zona
                regiao = nome_regiao
                break
        
        # Detectar zona por número
        zona_match = re.search(r'zona (\d+)', pergunta_lower)
        if zona_match:
            zona = int(zona_match.group(1))
        
        # Determinar tipo de consulta
        if 'mais votado' in pergunta_lower or 'top' in pergunta_lower:
            if zona:
                return {
                    "tipo_consulta": "candidatos_zona",
                    "parametros": {"limite": limite, "zona": zona, "regiao": regiao},
                    "explicacao": f"Buscar {limite} candidatos mais votados na zona {zona}"
                }
            else:
                return {
                    "tipo_consulta": "mais_votados",
                    "parametros": {"limite": limite},
                    "explicacao": f"Buscar {limite} candidatos mais votados geral"
                }
        
        elif 'buscar' in pergunta_lower or 'candidato' in pergunta_lower:
            # Extrair nome do candidato
            palavras = pergunta.split()
            nome_candidato = ' '.join([p for p in palavras if p.lower() not in ['buscar', 'candidato', 'por', 'nome', 'deputado']])
            
            return {
                "tipo_consulta": "buscar_candidato",
                "parametros": {"nome_candidato": nome_candidato.strip()},
                "explicacao": f"Buscar candidato com nome '{nome_candidato}'"
            }
        
        elif 'estatística' in pergunta_lower or 'resumo' in pergunta_lower:
            return {
                "tipo_consulta": "estatisticas",
                "parametros": {},
                "explicacao": "Mostrar estatísticas gerais das eleições"
            }
        
        elif 'zona' in pergunta_lower:
            return {
                "tipo_consulta": "zonas",
                "parametros": {},
                "explicacao": "Listar zonas eleitorais"
            }
        
        elif 'local' in pergunta_lower:
            return {
                "tipo_consulta": "locais",
                "parametros": {},
                "explicacao": "Listar locais de votação"
            }
        
        return {
            "tipo_consulta": "erro",
            "parametros": {},
            "explicacao": "Não foi possível entender a pergunta"
        }
    
    def gerar_resposta_natural(self, pergunta: str, dados: Dict[str, Any]) -> str:
        """
        Gera uma resposta em linguagem natural baseada nos dados retornados
        """
        try:
            prompt = f"""
Você é um assistente especializado em eleições do DF 2022.

PERGUNTA ORIGINAL: "{pergunta}"

DADOS RETORNADOS: {json.dumps(dados, ensure_ascii=False, indent=2)}

Gere uma resposta natural, amigável e informativa em português brasileiro.

DIRETRIZES:
- Use linguagem clara e acessível
- Destaque os números mais importantes
- Se houver candidatos, mencione os nomes e votos
- Se houver zonas, mencione as regiões
- Seja conciso mas informativo
- Use emojis quando apropriado (🗳️ 📊 🏆 etc.)

Retorne apenas a resposta em texto, sem formatação JSON.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente amigável especializado em dados eleitorais."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Erro ao gerar resposta natural: {e}")
            return "Encontrei os dados solicitados, mas tive dificuldade para formatá-los. Consulte os dados retornados para mais detalhes."

