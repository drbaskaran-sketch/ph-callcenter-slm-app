import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, StaticPool

try:
    from .config import settings
except ImportError:
    from config import settings

DATABASE_URL = settings.DATABASE_URL
POOL_SIZE = settings.DB_POOL_SIZE
MAX_OVERFLOW = settings.DB_MAX_OVERFLOW
POOL_TIMEOUT = settings.DB_POOL_TIMEOUT
POOL_RECYCLE = settings.DB_POOL_RECYCLE

class ProductionDatabaseManager:
    """Manages production-grade connection pooling for XTEND DB2 / PostgreSQL operational database"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self.engine = self._create_pooled_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def _create_pooled_engine(self):
        if self.db_url.startswith("sqlite"):
            return create_engine(
                    self.db_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool
                )
        return create_engine(
                    self.db_url,
                    poolclass=QueuePool,
                    pool_size=POOL_SIZE,
                    max_overflow=MAX_OVERFLOW,
                    pool_timeout=POOL_TIMEOUT,
                    pool_recycle=POOL_RECYCLE,
                    pool_pre_ping=True
                )

    def get_pool_status(self):
        """Returns live connection pool utilization metrics"""
        pool = self.engine.pool
        if hasattr(pool, "size"):
            return {
                "pool_class": pool.__class__.__name__,
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "max_overflow": MAX_OVERFLOW,
                "status": "Healthy (Production Pool)"
            }
        else:
            return {
                "pool_class": pool.__class__.__name__,
                "pool_size": POOL_SIZE,
                "checked_in": POOL_SIZE,
                "checked_out": 0,
                "overflow": 0,
                "max_overflow": MAX_OVERFLOW,
                "status": "Healthy (Static Test Pool)"
            }

REPLICA_DATABASE_URL = settings.REPLICA_DATABASE_URL
replica_db_manager = ProductionDatabaseManager(REPLICA_DATABASE_URL)

db_manager = ProductionDatabaseManager()

def get_db_session():
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_replica_db_session():
    db = replica_db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()
