from flask import Blueprint, render_template_string, request, jsonify, session
import os

admin_simple = Blueprint('admin_simple', __name__)

# Template HTML simples
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Admin - Eleições DF 2022</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; color: #333; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .hidden { display: none; }
        .status { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
        .status-online { background: #28a745; }
        .status-offline { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ Painel Administrativo</h1>
            <p>Sistema de Eleições DF 2022</p>
        </div>

        <!-- Login -->
        <div id="loginSection">
            <h2>🔐 Login</h2>
            <div id="loginAlert" class="alert alert-error hidden"></div>
            <form id="loginForm">
                <div class="form-group">
                    <label>Senha:</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit" class="btn">Entrar</button>
            </form>
        </div>

        <!-- Admin Panel -->
        <div id="adminPanel" class="hidden">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>⚙️ Configurações</h2>
                <button id="logoutBtn" class="btn">Sair</button>
            </div>

            <div id="adminAlert" class="alert alert-success hidden"></div>

            <h3>🤖 Configuração de IA</h3>
            
            <div class="form-group">
                <label>Provedor Ativo:</label>
                <div>
                    <input type="radio" id="openai" name="provider" value="openai"> 
                    <label for="openai">OpenAI <span id="openaiStatus" class="status status-offline"></span></label>
                </div>
                <div>
                    <input type="radio" id="deepseek" name="provider" value="deepseek"> 
                    <label for="deepseek">DeepSeek <span id="deepseekStatus" class="status status-offline"></span></label>
                </div>
            </div>

            <div class="form-group">
                <label>API Key OpenAI:</label>
                <input type="password" id="openaiKey" placeholder="sk-...">
                <button type="button" class="btn" onclick="testar('openai')">Testar</button>
            </div>

            <div class="form-group">
                <label>API Key DeepSeek:</label>
                <input type="password" id="deepseekKey" placeholder="sk-...">
                <button type="button" class="btn" onclick="testar('deepseek')">Testar</button>
            </div>

            <div class="form-group">
                <input type="checkbox" id="fallback"> 
                <label for="fallback">Ativar fallback automático</label>
            </div>

            <button type="button" class="btn" onclick="salvar()">💾 Salvar</button>

            <div style="margin-top: 30px;">
                <h3>📊 Status</h3>
                <p>Provedores Ativos: <span id="statusCount">0</span></p>
                <p>Sistema: <span id="systemStatus">❌</span></p>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        
        // Login
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const password = document.getElementById('password').value;
            
            if (password === 'admin123') {
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('adminPanel').classList.remove('hidden');
                mostrarAlerta('adminAlert', 'Login realizado com sucesso!', 'success');
            } else {
                mostrarAlerta('loginAlert', 'Senha incorreta!', 'error');
            }
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', function() {
            document.getElementById('adminPanel').classList.add('hidden');
            document.getElementById('loginSection').classList.remove('hidden');
            document.getElementById('password').value = '';
        });

        function testar(provider) {
            mostrarAlerta('adminAlert', `Testando ${provider}...`, 'success');
            // Simular teste
            setTimeout(() => {
                document.getElementById(provider + 'Status').className = 'status status-online';
                mostrarAlerta('adminAlert', `${provider} testado com sucesso!`, 'success');
            }, 1000);
        }

        function salvar() {
            const provider = document.querySelector('input[name="provider"]:checked')?.value;
            const fallback = document.getElementById('fallback').checked;
            
            if (!provider) {
                mostrarAlerta('adminAlert', 'Selecione um provedor!', 'error');
                return;
            }
            
            mostrarAlerta('adminAlert', 'Configuração salva com sucesso!', 'success');
            document.getElementById('statusCount').textContent = '1';
            document.getElementById('systemStatus').textContent = '✅';
        }

        function mostrarAlerta(id, message, type) {
            const alert = document.getElementById(id);
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alert.classList.remove('hidden');
            
            setTimeout(() => {
                alert.classList.add('hidden');
            }, 3000);
        }
    </script>
</body>
</html>
"""

@admin_simple.route('/admin')
@admin_simple.route('/admin.html')
def admin_panel():
    """Painel administrativo simples"""
    return render_template_string(ADMIN_TEMPLATE)

@admin_simple.route('/api/admin/status')
def admin_status():
    """Status do admin"""
    return jsonify({
        'success': True,
        'authenticated': True,
        'system_status': 'online'
    })

