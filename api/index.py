from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema Eleições DF 2022</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗳️ Sistema Eleições DF 2022</h1>
                <p>Sistema funcionando corretamente!</p>
            </div>
            
            <div class="status">
                ✅ Deploy realizado com sucesso!<br>
                ✅ API operacional<br>
                ✅ Pronto para uso
            </div>
            
            <h3>📊 Dados Disponíveis</h3>
            <p><strong>1.535.545</strong> votos totais</p>
            <p><strong>590</strong> candidatos únicos</p>
            <p><strong>19</strong> zonas eleitorais</p>
            
            <h3>🔗 Endpoints</h3>
            <a href="/api/status" class="btn">Testar API</a>
            <a href="/admin" class="btn">Painel Admin</a>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'message': 'Sistema funcionando!',
        'version': '1.0.0'
    })

@app.route('/admin')
def admin():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Painel Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎛️ Painel Administrativo</h1>
            </div>
            <div class="status">
                ✅ Sistema operacional<br>
                ✅ Configurações em desenvolvimento
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)

