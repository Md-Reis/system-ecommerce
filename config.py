"""
Configurações do Sistema E-Commerce Flask
"""

import os
from datetime import timedelta

class Config:
    """Configurações base do sistema"""
    
    # Configurações básicas do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui-2025'

    # Configurações do banco de dados
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://MarceloReis:pythonany@MarceloReis.mysql.pythonanywhere-services.com/MarceloReis$ecommerce'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Sessão expira em 2 horas
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de segurança
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Configurações de upload (para futuras implementações)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo para upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    
    # Configurações de paginação
    ANUNCIOS_POR_PAGINA = 12
    COMPRAS_POR_PAGINA = 10
    VENDAS_POR_PAGINA = 10
    
    # Configurações de email (para futuras implementações)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações específicas do e-commerce
    MOEDA = 'BRL'
    SIMBOLO_MOEDA = 'R$'
    LOCALE = 'pt_BR'
    TIMEZONE = 'America/Sao_Paulo'
    
    @staticmethod
    def init_app(app):
        """Inicializar configurações específicas da aplicação"""
        pass

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    TESTING = False
    
    # Logs mais verbosos em desenvolvimento
    LOG_LEVEL = 'DEBUG'
    
    # Desabilitar CSRF em desenvolvimento (apenas para testes)
    # WTF_CSRF_ENABLED = False  # Descomente apenas se necessário

class TestingConfig(Config):
    """Configurações para ambiente de testes"""
    TESTING = True
    DEBUG = True
    
    # Banco de dados em memória para testes
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://MarceloReis:pythonany@MarceloReis.mysql.pythonanywhere-services.com/MarceloReis$ecommerce'
    
    # Desabilitar proteções para facilitar testes
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'chave-de-teste-nao-segura'

class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança mais rígidas
    SESSION_COOKIE_SECURE = True
    
    # Logs apenas de erros em produção
    LOG_LEVEL = 'ERROR'
    
    @classmethod
    def init_app(cls, app):
        """Configurações específicas de produção"""
        Config.init_app(app)
        
        # Log para syslog em produção
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.ERROR)
        app.logger.addHandler(syslog_handler)

# Mapeamento de configurações por ambiente
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(environment=None):
    """
    Obter configuração baseada no ambiente
    
    Args:
        environment (str): Nome do ambiente (development, testing, production)
        
    Returns:
        Config: Classe de configuração apropriada
    """
    if environment is None:
        environment = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(environment, config['default'])