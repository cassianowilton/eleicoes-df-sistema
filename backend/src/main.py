import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.routes.eleicoes import eleicoes_bp
from src.routes.whatsapp import whatsapp_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eleicoes-df-2022-api-secret-key')

# Habilitar CORS para todas as rotas
CORS(app, origins=["*"])

# Registrar blueprints
app.register_blueprint(eleicoes_bp, url_prefix='/api')
app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')

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
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'candidatos_mais_votados': '/api/candidatos/mais-votados',
            'buscar_candidato': '/api/candidatos/buscar?nome=X',
            'consulta_natural': '/api/consulta-natural',
            'estatisticas': '/api/estatisticas',
            'whatsapp_status': '/api/whatsapp/status'
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
