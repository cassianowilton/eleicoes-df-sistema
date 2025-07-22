import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.routes.eleicoes import eleicoes_bp
from src.routes.whatsapp import whatsapp_bp
from src.routes.llm import llm_bp
from src.routes.admin_simple import admin_simple
from src.static_routes import register_static_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eleicoes-df-2022-api-secret-key')

# Configuração de sessão
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Habilitar CORS para todas as rotas
CORS(app, origins=["*"])

# Registrar blueprints
app.register_blueprint(eleicoes_bp, url_prefix='/api')
app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')
app.register_blueprint(llm_bp, url_prefix='/api/llm')
app.register_blueprint(admin_simple)

# Registrar rotas estáticas
register_static_routes(app)

# Configuração do banco PostgreSQL (Supabase)
app.config['SUPABASE_DB'] = {
    'host': os.environ.get('SUPABASE_HOST', 'db.ixnxgfkgcdfimdkvtqzk.supabase.co'),
    'port': os.environ.get('SUPABASE_PORT', '6543'),
    'database': os.environ.get('SUPABASE_DB', 'postgres'),
    'user': os.environ.get('SUPABASE_USER', 'postgres.ixnxgfkgcdfimdkvtqzk'),
    'password': os.environ.get('SUPABASE_PASSWORD', 'SdR3deS#2025')
}

@app.route('/')
def home():
    return jsonify({
        'message': 'API Eleições DF 2022',
        'version': '2.0.0',
        'status': 'online',
        'features': ['Multi-LLM Support', 'DeepSeek Integration', 'Fallback System', 'Admin Panel'],
        'endpoints': {
            'candidatos_mais_votados': '/api/candidatos/mais-votados',
            'buscar_candidato': '/api/candidatos/buscar?nome=X',
            'consulta_natural': '/api/consulta-natural',
            'estatisticas': '/api/estatisticas',
            'whatsapp_status': '/api/whatsapp/status',
            'llm_status': '/api/llm/status',
            'llm_providers': '/api/llm/providers',
            'llm_test': '/api/llm/test',
            'llm_custos': '/api/llm/custos',
            'admin_panel': '/admin.html',
            'admin_login': '/api/admin/login'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': os.environ.get('VERCEL_DEPLOYMENT_ID', 'local')})

# Para Vercel
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
