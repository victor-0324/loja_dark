"""
SaaS - Gestão de Loja de Roupas (VendeMais)
Ponto de entrada: cria a app via application factory e sobe o servidor de dev.

Em produção, use um WSGI server apontando para `app:app`, ex:
    gunicorn 'app:app'
"""

from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
