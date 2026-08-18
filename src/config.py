"""
Configuração da aplicação SaaS VendeMais.
Define diferentes ambientes: development, testing, production.
"""

import os
from datetime import timedelta

class Config:
    """Configuração base para todos os ambientes"""

    # Flask
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    DEBUG = False
    TESTING = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 24)))
    JWT_ALGORITHM = 'HS256'

    # O token é aceito tanto no header Authorization (uso via API/fetch)
    # quanto em cookies (para que a navegação normal do navegador entre
    # as páginas HTML do painel funcione sem precisar reenviar o header).
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = os.getenv('JWT_COOKIE_SECURE', 'false').lower() == 'true'
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_SESSION_COOKIE = True

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://localhost:3000').split(',')

    # Database
    DB_DRIVER = os.getenv('DB_DRIVER', 'mysql')
    DB_USER = os.getenv('DB_USER', 'g-krypta')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '3G[cewzH]Faf^^~OnhAe')
    DB_HOST = os.getenv('DB_HOST', '147.79.106.72')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'loja_dark')

    if DB_DRIVER == 'mysql':
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    elif DB_DRIVER == 'postgresql':
        SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:  # sqlite
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Email
    # MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    # MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    # MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    # MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    # MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@vendemais.com')

    # Paginação
    PAGINATE_BY = int(os.getenv('PAGINATE_BY', 20))
    MAX_PAGINATE_BY = int(os.getenv('MAX_PAGINATE_BY', 100))

    # Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'xlsx', 'csv'}

    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')

    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    SECRET_KEY = os.getenv('SECRET_KEY')

    @staticmethod
    def validar():
        """Valida configurações críticas"""
        if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError('SECRET_KEY não configurada. Defina a variável de ambiente SECRET_KEY.')
        if not Config.JWT_SECRET_KEY or Config.JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
            raise ValueError('JWT_SECRET_KEY não configurada. Defina a variável de ambiente JWT_SECRET_KEY.')


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    TESTING = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # Mais tempo em dev


class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://g-krypta:3G[cewzH]Faf^^~OnhAe@147.79.106.72:3306/loja_dark'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    @classmethod
    def validar(cls):
        """Validações extras para produção"""
        Config.validar()
        # Adicionar validações extras


# Dicionário de configurações
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
