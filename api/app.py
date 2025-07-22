from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import json
import hashlib

app = Flask(__name__)
CORS(app)

# Configurações do banco
DB_CONFIG = {
    'host': os.environ.get('SUPABASE_HOST', 'aws-0-sa-east-1.pooler.supabase.com'),
    'port': os.environ.get('SUPABASE_PORT', '6543'),
    'database': os.environ.get('SUPABASE_DB', 'postgres'),
    'user': os.environ.get('SUPABASE_USER', 'postgres.ixnxgfkgcdfimdkvtqzk'),
    'password': os.environ.get('SUPABASE_PASSWORD', 'SdR3deS#2025')
}

# Configurações admin (simples)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
CONFIG_FILE = '/tmp/admin_config.json'

def get_db_connection():
    """Conecta ao banco Supabase"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro conexão DB: {e}")
        return None

def load_config():
    """Carrega configurações salvas"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'ia_provider': 'openai',
        'openai_key': '',
        'deepseek_key': '',
        'fallback': True
    }

def save_config(config):
    """Salva configurações"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return True
    except:
        return False

@app.route('/api/consulta', methods=['POST'])
def consulta_ia():
    """Endpoint para consultas com IA"""
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '').strip()
        
        if not pergunta:
            return jsonify({'error': 'Pergunta não fornecida'}), 400
        
        # Conectar ao banco
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Erro de conexão com banco'}), 500
        
        cursor = conn.cursor()
        
        # Análise simples da pergunta para determinar consulta
        pergunta_lower = pergunta.lower()
        
        if 'top' in pergunta_lower or 'mais votados' in pergunta_lower:
            # Top candidatos
            limite = 5
            if 'top 10' in pergunta_lower or '10 mais' in pergunta_lower:
                limite = 10
            elif 'top 3' in pergunta_lower or '3 mais' in pergunta_lower:
                limite = 3
                
            cursor.execute("""
                SELECT c.nome_candidato, SUM(v.qtd_votos) as total_votos
                FROM votacao v
                JOIN candidatos c ON v.candidato_id = c.id
                GROUP BY c.nome_candidato
                ORDER BY total_votos DESC
                LIMIT %s
            """, (limite,))
            
            resultados = cursor.fetchall()
            
            resposta = f"🏆 Top {limite} candidatos mais votados:\n\n"
            for i, (nome, votos) in enumerate(resultados, 1):
                resposta += f"{i}. **{nome}**: {votos:,} votos\n"
                
        elif 'buscar' in pergunta_lower or 'candidato' in pergunta_lower:
            # Buscar candidato específico
            # Extrair nome do candidato da pergunta
            palavras = pergunta.split()
            nome_busca = ' '.join([p for p in palavras if len(p) > 3 and p.lower() not in ['buscar', 'candidato', 'quantos', 'votos']])
            
            if nome_busca:
                cursor.execute("""
                    SELECT c.nome_candidato, SUM(v.qtd_votos) as total_votos
                    FROM votacao v
                    JOIN candidatos c ON v.candidato_id = c.id
                    WHERE UPPER(c.nome_candidato) LIKE UPPER(%s)
                    GROUP BY c.nome_candidato
                    ORDER BY total_votos DESC
                """, (f'%{nome_busca}%',))
                
                resultados = cursor.fetchall()
                
                if resultados:
                    resposta = f"🔍 Resultados para '{nome_busca}':\n\n"
                    for nome, votos in resultados:
                        resposta += f"• **{nome}**: {votos:,} votos\n"
                else:
                    resposta = f"❌ Nenhum candidato encontrado com '{nome_busca}'"
            else:
                resposta = "❌ Por favor, especifique o nome do candidato"
                
        elif 'estatísticas' in pergunta_lower or 'dados' in pergunta_lower:
            # Estatísticas gerais
            cursor.execute("SELECT COUNT(*) FROM candidatos")
            total_candidatos = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(qtd_votos) FROM votacao")
            total_votos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT zona_eleitoral) FROM secoes_eleitorais")
            total_zonas = cursor.fetchone()[0]
            
            resposta = f"""📊 **Estatísticas Eleições DF 2022:**

• **Total de votos**: {total_votos:,}
• **Candidatos**: {total_candidatos}
• **Zonas eleitorais**: {total_zonas}
• **Sistema**: Operacional ✅"""
            
        else:
            resposta = """❓ **Consultas disponíveis:**

• "Top 5 candidatos mais votados"
• "Buscar [nome do candidato]"
• "Estatísticas gerais"

**Exemplo**: "Top 10 mais votados" ou "Buscar João Silva" """
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'pergunta': pergunta,
            'resposta': resposta
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Login do administrador"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password == ADMIN_PASSWORD:
            # Gerar token simples
            token = hashlib.md5(f"{password}_{ADMIN_PASSWORD}".encode()).hexdigest()
            return jsonify({
                'success': True,
                'token': token,
                'message': 'Login realizado com sucesso'
            })
        else:
            return jsonify({'error': 'Senha incorreta'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Erro no login: {str(e)}'}), 500

@app.route('/api/admin/config', methods=['GET', 'POST'])
def admin_config():
    """Gerenciar configurações do admin"""
    try:
        if request.method == 'GET':
            # Retornar configurações atuais
            config = load_config()
            # Mascarar API keys para segurança
            if config.get('openai_key'):
                config['openai_key'] = 'sk-...' + config['openai_key'][-4:]
            if config.get('deepseek_key'):
                config['deepseek_key'] = 'sk-...' + config['deepseek_key'][-4:]
            
            return jsonify({
                'success': True,
                'config': config
            })
            
        elif request.method == 'POST':
            # Salvar novas configurações
            data = request.get_json()
            
            config = load_config()
            config.update({
                'ia_provider': data.get('ia_provider', config.get('ia_provider', 'openai')),
                'openai_key': data.get('openai_key', config.get('openai_key', '')),
                'deepseek_key': data.get('deepseek_key', config.get('deepseek_key', '')),
                'fallback': data.get('fallback', config.get('fallback', True))
            })
            
            if save_config(config):
                return jsonify({
                    'success': True,
                    'message': 'Configurações salvas com sucesso'
                })
            else:
                return jsonify({'error': 'Erro ao salvar configurações'}), 500
                
    except Exception as e:
        return jsonify({'error': f'Erro nas configurações: {str(e)}'}), 500

@app.route('/api/status')
def status():
    """Status da API"""
    try:
        # Testar conexão com banco
        conn = get_db_connection()
        db_status = "online" if conn else "offline"
        if conn:
            conn.close()
            
        config = load_config()
        
        return jsonify({
            'success': True,
            'status': 'online',
            'database': db_status,
            'ia_provider': config.get('ia_provider', 'openai'),
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({'error': f'Erro no status: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

