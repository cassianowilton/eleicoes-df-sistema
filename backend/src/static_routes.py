"""
Rotas para servir arquivos estáticos (frontend)
"""
from flask import send_from_directory, current_app
import os

def register_static_routes(app):
    """Registra rotas para servir arquivos estáticos"""
    
    @app.route('/admin.html')
    def admin_panel():
        """Serve o painel administrativo"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')
        return send_from_directory(frontend_dir, 'admin.html')
    
    @app.route('/index.html')
    @app.route('/dashboard.html')
    def dashboard():
        """Serve o dashboard principal"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')
        return send_from_directory(frontend_dir, 'index.html')
    
    @app.route('/favicon.ico')
    def favicon():
        """Serve o favicon"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')
        return send_from_directory(frontend_dir, 'favicon.ico')

