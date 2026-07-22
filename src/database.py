"""
Gerenciamento de conexão com banco de dados.
Usa SQLAlchemy ORM com session manager.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# Base para todos os models
Base = declarative_base()


class DBConnectionHendler:
    """Gerenciador de conexão com banco de dados"""

    def __init__(self, config=None):
        """
        Inicializa o handler com configuração.
        
        Args:
            config: Objeto de configuração com atributos de BD
        """
        self.config = config
        self._engine = None
        self._session_factory = None
        self._session = None

    def get_engine(self):
        """Retorna engine SQLAlchemy (singleton)"""
        if not self._engine:
            if not self.config:
                from src.config import DevelopmentConfig
                self.config = DevelopmentConfig

            database_uri = self.config.SQLALCHEMY_DATABASE_URI
            
            # Configurar engine baseado no tipo de banco
            if 'sqlite' in database_uri:
                self._engine = create_engine(
                    database_uri,
                    connect_args={'check_same_thread': False},
                    echo=self.config.SQLALCHEMY_ECHO
                )
            else:
                # MySQL e PostgreSQL
                self._engine = create_engine(
                    database_uri,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_recycle=3600,
                    echo=self.config.SQLALCHEMY_ECHO
                )

        return self._engine

    def get_session_factory(self):
        """Retorna session factory (singleton)"""
        if not self._session_factory:
            engine = self.get_engine()
            self._session_factory = sessionmaker(
                bind=engine,
                expire_on_commit=False
            )
        return self._session_factory

    def get_session(self):
        """Retorna nova sessão"""
        session_factory = self.get_session_factory()
        self._session = session_factory()
        return self._session

    def remove_session(self):
        """Remove sessão atual"""
        if self._session:
            self._session.close()
            self._session = None

    def create_all_tables(self):
        """Cria todas as tabelas no banco"""
        engine = self.get_engine()
        Base.metadata.create_all(bind=engine)

    def drop_all_tables(self):
        """Deleta todas as tabelas (CUIDADO!)"""
        engine = self.get_engine()
        Base.metadata.drop_all(bind=engine)

    def close(self):
        """Fecha todas as conexões"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
        self.remove_session()
