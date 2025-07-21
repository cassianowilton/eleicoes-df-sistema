"""
Rotas da API para consultas eleitorais DF 2022
"""

from flask import Blueprint, jsonify, request, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import re
from src.services import ia_service

eleicoes_bp = Blueprint('eleicoes', __name__)

def get_db_connection():
    """Obtém conexão com o banco PostgreSQL"""
    try:
        config = current_app.config['SUPABASE_DB']
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def executar_consulta(sql, params=None):
    """Executa uma consulta SQL e retorna os resultados"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql, params or ())
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Erro na consulta: {e}")
        if conn:
            conn.close()
        return None

@eleicoes_bp.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar status da API"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({
            'status': 'online',
            'message': 'API de Eleições DF 2022 funcionando',
            'database': 'conectado'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Erro de conexão com banco de dados',
            'database': 'desconectado'
        }), 500

@eleicoes_bp.route('/candidatos/mais-votados', methods=['GET'])
def candidatos_mais_votados():
    """Retorna os candidatos mais votados"""
    limite = request.args.get('limite', 10, type=int)
    zona = request.args.get('zona', type=int)
    
    sql = """
        SELECT 
            c.nm_votavel as nome,
            c.nr_votavel as numero,
            SUM(v.qt_votos) as total_votos,
            COUNT(DISTINCT v.nr_zona) as zonas_com_votos,
            COUNT(DISTINCT CONCAT(v.nr_zona, '-', v.nr_secao)) as secoes_com_votos
        FROM candidatos c
        JOIN votacao v ON c.sq_candidato = v.sq_candidato
    """
    
    params = []
    if zona:
        sql += " WHERE v.nr_zona = %s"
        params.append(zona)
    
    sql += """
        GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
        ORDER BY total_votos DESC
        LIMIT %s
    """
    params.append(limite)
    
    resultados = executar_consulta(sql, params)
    
    if resultados is None:
        return jsonify({'error': 'Erro ao consultar banco de dados'}), 500
    
    return jsonify({
        'candidatos': resultados,
        'total_encontrados': len(resultados),
        'filtros': {
            'limite': limite,
            'zona': zona
        }
    })

@eleicoes_bp.route('/candidatos/buscar', methods=['GET'])
def buscar_candidatos():
    """Busca candidatos por nome"""
    nome = request.args.get('nome', '').strip()
    limite = request.args.get('limite', 20, type=int)
    
    if not nome:
        return jsonify({'error': 'Parâmetro nome é obrigatório'}), 400
    
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
        LIMIT %s
    """
    
    nome_busca = f"%{nome}%"
    resultados = executar_consulta(sql, [nome_busca, limite])
    
    if resultados is None:
        return jsonify({'error': 'Erro ao consultar banco de dados'}), 500
    
    return jsonify({
        'candidatos': resultados,
        'total_encontrados': len(resultados),
        'termo_busca': nome
    })

@eleicoes_bp.route('/zonas', methods=['GET'])
def listar_zonas():
    """Lista todas as zonas eleitorais"""
    sql = """
        SELECT 
            z.nr_zona as numero,
            z.regiao_administrativa,
            COUNT(DISTINCT s.nr_secao) as total_secoes,
            COUNT(DISTINCT s.nr_local_votacao) as total_locais,
            SUM(v.qt_votos) as total_votos
        FROM zonas_eleitorais z
        LEFT JOIN secoes_eleitorais s ON z.nr_zona = s.nr_zona
        LEFT JOIN votacao v ON z.nr_zona = v.nr_zona
        GROUP BY z.nr_zona, z.regiao_administrativa
        ORDER BY z.nr_zona
    """
    
    resultados = executar_consulta(sql)
    
    if resultados is None:
        return jsonify({'error': 'Erro ao consultar banco de dados'}), 500
    
    return jsonify({
        'zonas': resultados,
        'total_zonas': len(resultados)
    })

@eleicoes_bp.route('/zona/<int:nr_zona>/candidatos', methods=['GET'])
def candidatos_por_zona(nr_zona):
    """Retorna candidatos mais votados em uma zona específica"""
    limite = request.args.get('limite', 10, type=int)
    
    sql = """
        SELECT 
            c.nm_votavel as nome,
            c.nr_votavel as numero,
            SUM(v.qt_votos) as total_votos,
            COUNT(DISTINCT v.nr_secao) as secoes_com_votos
        FROM candidatos c
        JOIN votacao v ON c.sq_candidato = v.sq_candidato
        WHERE v.nr_zona = %s
        GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
        ORDER BY total_votos DESC
        LIMIT %s
    """
    
    resultados = executar_consulta(sql, [nr_zona, limite])
    
    if resultados is None:
        return jsonify({'error': 'Erro ao consultar banco de dados'}), 500
    
    # Buscar informações da zona
    sql_zona = """
        SELECT 
            nr_zona as numero,
            regiao_administrativa,
            COUNT(DISTINCT s.nr_secao) as total_secoes
        FROM zonas_eleitorais z
        LEFT JOIN secoes_eleitorais s ON z.nr_zona = s.nr_zona
        WHERE z.nr_zona = %s
        GROUP BY z.nr_zona, z.regiao_administrativa
    """
    
    info_zona = executar_consulta(sql_zona, [nr_zona])
    
    return jsonify({
        'zona': info_zona[0] if info_zona else {'numero': nr_zona},
        'candidatos': resultados,
        'total_encontrados': len(resultados)
    })

@eleicoes_bp.route('/locais', methods=['GET'])
def listar_locais():
    """Lista locais de votação"""
    limite = request.args.get('limite', 50, type=int)
    busca = request.args.get('busca', '').strip()
    
    sql = """
        SELECT 
            l.nr_local_votacao as numero,
            l.nm_local_votacao as nome,
            l.ds_endereco as endereco,
            COUNT(DISTINCT s.nr_secao) as total_secoes,
            COUNT(DISTINCT s.nr_zona) as zonas_atendidas
        FROM locais_votacao l
        LEFT JOIN secoes_eleitorais s ON l.nr_local_votacao = s.nr_local_votacao
    """
    
    params = []
    if busca:
        sql += " WHERE UPPER(l.nm_local_votacao) LIKE UPPER(%s)"
        params.append(f"%{busca}%")
    
    sql += """
        GROUP BY l.nr_local_votacao, l.nm_local_votacao, l.ds_endereco
        ORDER BY l.nm_local_votacao
        LIMIT %s
    """
    params.append(limite)
    
    resultados = executar_consulta(sql, params)
    
    if resultados is None:
        return jsonify({'error': 'Erro ao consultar banco de dados'}), 500
    
    return jsonify({
        'locais': resultados,
        'total_encontrados': len(resultados),
        'filtros': {
            'limite': limite,
            'busca': busca
        }
    })

@eleicoes_bp.route('/estatisticas', methods=['GET'])
def estatisticas_gerais():
    """Retorna estatísticas gerais das eleições"""
    
    # Total de votos
    sql_votos = "SELECT SUM(qt_votos) as total_votos FROM votacao"
    total_votos = executar_consulta(sql_votos)
    
    # Total de candidatos
    sql_candidatos = "SELECT COUNT(*) as total_candidatos FROM candidatos"
    total_candidatos = executar_consulta(sql_candidatos)
    
    # Total de zonas
    sql_zonas = "SELECT COUNT(*) as total_zonas FROM zonas_eleitorais"
    total_zonas = executar_consulta(sql_zonas)
    
    # Total de seções
    sql_secoes = "SELECT COUNT(*) as total_secoes FROM secoes_eleitorais"
    total_secoes = executar_consulta(sql_secoes)
    
    # Total de locais
    sql_locais = "SELECT COUNT(*) as total_locais FROM locais_votacao"
    total_locais = executar_consulta(sql_locais)
    
    # Candidato mais votado
    sql_mais_votado = """
        SELECT 
            c.nm_votavel as nome,
            SUM(v.qt_votos) as total_votos
        FROM candidatos c
        JOIN votacao v ON c.sq_candidato = v.sq_candidato
        GROUP BY c.sq_candidato, c.nm_votavel
        ORDER BY total_votos DESC
        LIMIT 1
    """
    mais_votado = executar_consulta(sql_mais_votado)
    
    return jsonify({
        'estatisticas': {
            'total_votos': total_votos[0]['total_votos'] if total_votos else 0,
            'total_candidatos': total_candidatos[0]['total_candidatos'] if total_candidatos else 0,
            'total_zonas': total_zonas[0]['total_zonas'] if total_zonas else 0,
            'total_secoes': total_secoes[0]['total_secoes'] if total_secoes else 0,
            'total_locais': total_locais[0]['total_locais'] if total_locais else 0,
            'candidato_mais_votado': mais_votado[0] if mais_votado else None
        }
    })

@eleicoes_bp.route('/consulta-natural', methods=['POST'])
def consulta_natural():
    """Endpoint para consultas em linguagem natural usando IA"""
    data = request.get_json()
    
    if not data or 'pergunta' not in data:
        return jsonify({'error': 'Campo pergunta é obrigatório'}), 400
    
    pergunta = data['pergunta'].strip()
    
    if not pergunta:
        return jsonify({'error': 'Pergunta não pode estar vazia'}), 400
    
    try:
        # Processar pergunta com IA
        analise = ia_service.processar_pergunta(pergunta)
        
        # Executar consulta baseada na análise da IA
        resultado_dados = None
        
        if analise['tipo_consulta'] == 'mais_votados':
            limite = analise['parametros'].get('limite', 10)
            # Chamar função diretamente com parâmetros
            sql = """
                SELECT 
                    c.nm_votavel as nome,
                    c.nr_votavel as numero,
                    SUM(v.qt_votos) as total_votos,
                    COUNT(DISTINCT v.nr_zona) as zonas_com_votos,
                    COUNT(DISTINCT CONCAT(v.nr_zona, '-', v.nr_secao)) as secoes_com_votos
                FROM candidatos c
                JOIN votacao v ON c.sq_candidato = v.sq_candidato
                GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
                ORDER BY total_votos DESC
                LIMIT %s
            """
            resultados = executar_consulta(sql, [limite])
            if resultados:
                resultado_dados = {
                    'candidatos': resultados,
                    'total_encontrados': len(resultados),
                    'filtros': {'limite': limite, 'zona': None}
                }
            
        elif analise['tipo_consulta'] == 'candidatos_zona':
            zona = analise['parametros'].get('zona')
            limite = analise['parametros'].get('limite', 10)
            if zona:
                sql = """
                    SELECT 
                        c.nm_votavel as nome,
                        c.nr_votavel as numero,
                        SUM(v.qt_votos) as total_votos,
                        COUNT(DISTINCT v.nr_secao) as secoes_com_votos
                    FROM candidatos c
                    JOIN votacao v ON c.sq_candidato = v.sq_candidato
                    WHERE v.nr_zona = %s
                    GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel
                    ORDER BY total_votos DESC
                    LIMIT %s
                """
                resultados = executar_consulta(sql, [zona, limite])
                if resultados:
                    resultado_dados = {
                        'zona': {'numero': zona},
                        'candidatos': resultados,
                        'total_encontrados': len(resultados)
                    }
            
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
                    LIMIT 20
                """
                nome_busca = f"%{nome}%"
                resultados = executar_consulta(sql, [nome_busca])
                if resultados:
                    resultado_dados = {
                        'candidatos': resultados,
                        'total_encontrados': len(resultados),
                        'termo_busca': nome
                    }
                
        elif analise['tipo_consulta'] == 'votos_candidato_regiao':
            candidato = analise['parametros'].get('candidato_especifico')
            regiao = analise['parametros'].get('regiao')
            
            if candidato:
                # Buscar votos do candidato por região
                if regiao:
                    # Região específica
                    zona = obter_zona_por_regiao(regiao)
                    if zona:
                        sql = """
                            SELECT 
                                c.nm_votavel as nome,
                                z.regiao_administrativa as regiao,
                                SUM(v.qt_votos) as total_votos,
                                COUNT(DISTINCT v.nr_secao) as secoes
                            FROM candidatos c
                            JOIN votacao v ON c.sq_candidato = v.sq_candidato
                            JOIN zonas_eleitorais z ON v.nr_zona = z.nr_zona
                            WHERE UPPER(c.nm_votavel) LIKE UPPER(%s) AND v.nr_zona = %s
                            GROUP BY c.sq_candidato, c.nm_votavel, z.regiao_administrativa
                            ORDER BY total_votos DESC
                        """
                        resultados = executar_consulta(sql, [f"%{candidato}%", zona])
                else:
                    # Todas as regiões
                    sql = """
                        SELECT 
                            c.nm_votavel as nome,
                            z.regiao_administrativa as regiao,
                            v.nr_zona as zona,
                            SUM(v.qt_votos) as total_votos,
                            COUNT(DISTINCT v.nr_secao) as secoes
                        FROM candidatos c
                        JOIN votacao v ON c.sq_candidato = v.sq_candidato
                        JOIN zonas_eleitorais z ON v.nr_zona = z.nr_zona
                        WHERE UPPER(c.nm_votavel) LIKE UPPER(%s)
                        GROUP BY c.sq_candidato, c.nm_votavel, z.regiao_administrativa, v.nr_zona
                        ORDER BY total_votos DESC
                    """
                    resultados = executar_consulta(sql, [f"%{candidato}%"])
                
                if resultados:
                    resultado_dados = {
                        'candidato_buscado': candidato,
                        'regiao_filtro': regiao,
                        'votos_por_regiao': resultados,
                        'total_encontrados': len(resultados)
                    }
        
        elif analise['tipo_consulta'] == 'votos_candidato_secao':
            candidato = analise['parametros'].get('candidato_especifico')
            secao = analise['parametros'].get('secao')
            zona = analise['parametros'].get('zona')
            
            if candidato and (secao or zona):
                sql = """
                    SELECT 
                        c.nm_votavel as nome,
                        c.nr_votavel as numero,
                        v.nr_zona as zona,
                        v.nr_secao as secao,
                        v.qt_votos as votos,
                        l.nm_local_votacao as local
                    FROM candidatos c
                    JOIN votacao v ON c.sq_candidato = v.sq_candidato
                    LEFT JOIN secoes_eleitorais s ON v.nr_zona = s.nr_zona AND v.nr_secao = s.nr_secao
                    LEFT JOIN locais_votacao l ON s.nr_local_votacao = l.nr_local_votacao
                    WHERE UPPER(c.nm_votavel) LIKE UPPER(%s)
                """
                params = [f"%{candidato}%"]
                
                if secao:
                    sql += " AND v.nr_secao = %s"
                    params.append(secao)
                if zona:
                    sql += " AND v.nr_zona = %s"
                    params.append(zona)
                
                sql += " ORDER BY v.qt_votos DESC"
                resultados = executar_consulta(sql, params)
                
                if resultados:
                    resultado_dados = {
                        'candidato_buscado': candidato,
                        'secao_filtro': secao,
                        'zona_filtro': zona,
                        'votos_por_secao': resultados,
                        'total_encontrados': len(resultados)
                    }
        
        elif analise['tipo_consulta'] == 'comparar_regioes':
            regioes = analise['parametros'].get('regioes_comparar', [])
            
            if len(regioes) >= 2:
                zonas = []
                for regiao in regioes:
                    zona = obter_zona_por_regiao(regiao)
                    if zona:
                        zonas.append(zona)
                
                if zonas:
                    placeholders = ','.join(['%s'] * len(zonas))
                    sql = f"""
                        SELECT 
                            z.regiao_administrativa as regiao,
                            z.nr_zona as zona,
                            COUNT(DISTINCT c.sq_candidato) as total_candidatos,
                            SUM(v.qt_votos) as total_votos,
                            COUNT(DISTINCT v.nr_secao) as total_secoes,
                            c.nm_votavel as candidato_mais_votado,
                            MAX(votos_candidato.total_votos) as votos_mais_votado
                        FROM zonas_eleitorais z
                        JOIN votacao v ON z.nr_zona = v.nr_zona
                        JOIN candidatos c ON v.sq_candidato = c.sq_candidato
                        JOIN (
                            SELECT 
                                v2.nr_zona,
                                c2.sq_candidato,
                                c2.nm_votavel,
                                SUM(v2.qt_votos) as total_votos,
                                ROW_NUMBER() OVER (PARTITION BY v2.nr_zona ORDER BY SUM(v2.qt_votos) DESC) as rn
                            FROM votacao v2
                            JOIN candidatos c2 ON v2.sq_candidato = c2.sq_candidato
                            WHERE v2.nr_zona IN ({placeholders})
                            GROUP BY v2.nr_zona, c2.sq_candidato, c2.nm_votavel
                        ) votos_candidato ON z.nr_zona = votos_candidato.nr_zona AND c.sq_candidato = votos_candidato.sq_candidato
                        WHERE z.nr_zona IN ({placeholders}) AND votos_candidato.rn = 1
                        GROUP BY z.regiao_administrativa, z.nr_zona, c.nm_votavel, votos_candidato.total_votos
                        ORDER BY total_votos DESC
                    """
                    resultados = executar_consulta(sql, zonas + zonas)
                    
                    if resultados:
                        resultado_dados = {
                            'regioes_comparadas': regioes,
                            'comparacao': resultados,
                            'total_regioes': len(resultados)
                        }
        
        elif analise['tipo_consulta'] == 'ranking_local':
            local = analise['parametros'].get('local_votacao')
            limite = analise['parametros'].get('limite', 10)
            
            if local:
                sql = """
                    SELECT 
                        c.nm_votavel as nome,
                        c.nr_votavel as numero,
                        SUM(v.qt_votos) as total_votos,
                        l.nm_local_votacao as local,
                        l.ds_endereco as endereco
                    FROM candidatos c
                    JOIN votacao v ON c.sq_candidato = v.sq_candidato
                    JOIN secoes_eleitorais s ON v.nr_zona = s.nr_zona AND v.nr_secao = s.nr_secao
                    JOIN locais_votacao l ON s.nr_local_votacao = l.nr_local_votacao
                    WHERE UPPER(l.nm_local_votacao) LIKE UPPER(%s)
                    GROUP BY c.sq_candidato, c.nm_votavel, c.nr_votavel, l.nm_local_votacao, l.ds_endereco
                    ORDER BY total_votos DESC
                    LIMIT %s
                """
                resultados = executar_consulta(sql, [f"%{local}%", limite])
                
                if resultados:
                    resultado_dados = {
                        'local_buscado': local,
                        'candidatos': resultados,
                        'total_encontrados': len(resultados)
                    }
                
        elif analise['tipo_consulta'] == 'estatisticas':
            response = estatisticas_gerais()
            resultado_dados = response.get_json()
            
        elif analise['tipo_consulta'] == 'zonas':
            response = listar_zonas()
            resultado_dados = response.get_json()
            
        elif analise['tipo_consulta'] == 'locais':
            response = listar_locais()
            resultado_dados = response.get_json()
        
        # Gerar resposta natural se temos dados
        resposta_natural = None
        if resultado_dados:
            resposta_natural = ia_service.gerar_resposta_natural(pergunta, resultado_dados)
        
        return jsonify({
            'pergunta': pergunta,
            'analise_ia': analise,
            'dados': resultado_dados,
            'resposta_natural': resposta_natural
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erro ao processar consulta: {str(e)}',
            'pergunta': pergunta
        }), 500

def obter_zona_por_regiao(regiao):
    """Converte nome da região para número da zona"""
    mapa_regioes = {
        'brasília': 1, 'brasilia': 1, 'plano piloto': 1, 'asa norte': 1, 'asa sul': 1,
        'gama': 2,
        'taguatinga': 3, 'taguatinga norte': 3, 'taguatinga sul': 3,
        'brazlândia': 4, 'brazlandia': 4,
        'sobradinho': 5,
        'planaltina': 6,
        'núcleo bandeirante': 8, 'nucleo bandeirante': 8, 'candangolândia': 8,
        'ceilândia': 9, 'ceilandia': 9,
        'guará': 10, 'guara': 10,
        'cruzeiro': 11,
        'samambaia': 14,
        'são sebastião': 15, 'sao sebastiao': 15,
        'recanto das emas': 16,
        'lago sul': 17,
        'riacho fundo': 18,
        'águas claras': 19, 'aguas claras': 19,
        'vicente pires': 20,
        'paranoá': 21, 'paranoa': 21,
        'sobradinho ii': 13
    }
    return mapa_regioes.get(regiao.lower())

