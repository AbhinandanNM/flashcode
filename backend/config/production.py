"""
Production configuration for CodeCrafts MVP
"""

import os
from typing import List, Optional

class ProductionConfig:
    """Production configuration settings"""
    
    # Environment
    ENV: str = "production"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://codecrafts:password@db:5432/codecrafts_prod"
    )
    
    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://:password@redis:6379/0"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "https://codecrafts.app,https://www.codecrafts.app"
    ).split(",")
    
    # External Services
    JUDGE0_API_URL: str = os.getenv("JUDGE0_API_URL", "http://judge0:2358")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "/app/logs/codecrafts.log"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "/app/uploads"
    ALLOWED_EXTENSIONS: set = {'.py', '.cpp', '.c', '.java', '.js', '.txt'}
    
    # Code Execution
    CODE_EXECUTION_TIMEOUT: int = 30  # seconds
    MAX_CODE_LENGTH: int = 10000  # characters
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@codecrafts.app")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001
    
    # Performance
    WORKER_PROCESSES: int = int(os.getenv("WORKER_PROCESSES", "4"))
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", "1000"))
    KEEPALIVE_TIMEOUT: int = int(os.getenv("KEEPALIVE_TIMEOUT", "65"))
    
    # Caching
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # Database Connection Pool
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # Feature Flags
    ENABLE_REGISTRATION: bool = os.getenv("ENABLE_REGISTRATION", "true").lower() == "true"
    ENABLE_DUELS: bool = os.getenv("ENABLE_DUELS", "true").lower() == "true"
    ENABLE_CODE_EXECUTION: bool = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    
    # Backup Configuration
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_SCHEDULE: str = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    
    # AWS Configuration (for backups and file storage)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: Optional[str] = os.getenv("AWS_S3_BUCKET")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Health Check
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate required configuration values"""
        required_vars = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "DATABASE_URL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required configuration variables: {', '.join(missing_vars)}")
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration for SQLAlchemy"""
        return {
            "url": cls.DATABASE_URL,
            "pool_size": cls.DB_POOL_SIZE,
            "max_overflow": cls.DB_MAX_OVERFLOW,
            "pool_timeout": cls.DB_POOL_TIMEOUT,
            "pool_recycle": cls.DB_POOL_RECYCLE,
            "pool_pre_ping": True,
            "echo": False  # Set to True for SQL debugging
        }
    
    @classmethod
    def get_redis_config(cls) -> dict:
        """Get Redis configuration"""
        return {
            "url": cls.REDIS_URL,
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
    
    @classmethod
    def get_logging_config(cls) -> dict:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": cls.LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": cls.LOG_LEVEL,
                    "formatter": "default",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": cls.LOG_LEVEL,
                    "formatter": "json",
                    "filename": cls.LOG_FILE,
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {
                "codecrafts": {
                    "level": cls.LOG_LEVEL,
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False
                },
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "handlers": ["file"],
                    "propagate": False
                }
            },
            "root": {
                "level": cls.LOG_LEVEL,
                "handlers": ["console", "file"]
            }
        }

# Create config instance
config = ProductionConfig()

# Validate configuration on import
config.validate_config()