"""
Application configuration settings
"""

from typing import List, Optional, Any, Union
from pydantic import validator, AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "HR Performance Management System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="https://hr.gogopeaks.com,https://localhost:3000,http://localhost:3000"
    )
    
    # Security
    SECRET_KEY: str = "hr_secret_key_2024_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    ALLOWED_HOSTS: Union[str, List[str]] = Field(
        default="hr.gogopeaks.com,localhost,127.0.0.1"
    )
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://hr_user:hr_password_2024@localhost:3306/hr_performance?charset=utf8mb4"
    
    # Redis
    REDIS_URL: str = "redis://:hr_redis_2024@localhost:6379/0"
    
    # LDAP Configuration
    LDAP_SERVER: str = "ldap://192.168.1.100:389"
    LDAP_BASE_DN: str = "dc=gogopeaks,dc=com"
    LDAP_USER_BASE_DN: str = "ou=users,dc=gogopeaks,dc=com"
    LDAP_GROUP_BASE_DN: str = "ou=groups,dc=gogopeaks,dc=com"
    LDAP_BIND_DN: str = "cn=admin,dc=gogopeaks,dc=com"
    LDAP_BIND_PASSWORD: str = ""
    LDAP_USER_FILTER: str = "(objectClass=inetOrgPerson)"
    LDAP_GROUP_FILTER: str = "(objectClass=groupOfNames)"
    LDAP_USER_ID_ATTRIBUTE: str = "uid"
    LDAP_USER_NAME_ATTRIBUTE: str = "cn"
    LDAP_USER_EMAIL_ATTRIBUTE: str = "mail"
    LDAP_GROUP_NAME_ATTRIBUTE: str = "cn"
    LDAP_GROUP_MEMBER_ATTRIBUTE: str = "member"
    
    # File Storage
    SYNOLOGY_DRIVE_PATH: str = "/shared/hr-evidence"
    SYNOLOGY_DRIVE_URL: str = "https://drive.gogopeaks.com"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_EXTENSIONS: Union[str, List[str]] = Field(
        default="jpg,jpeg,png,gif,bmp,webp,pdf,doc,docx,txt,rtf,xls,xlsx,csv,ppt,pptx,zip,rar,7z,mp4,avi,mov,wmv,mp3,wav,flac"
    )
    
    # External APIs
    REDMINE_URL: str = "https://redmine.gogopeaks.com"
    REDMINE_API_KEY: str = ""
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gogopeaks.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "hr@gogopeaks.com"
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    
    # Synology Chat
    SYNOLOGY_CHAT_WEBHOOK: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Scoring Engine
    SCORING_SCHEDULE_HOUR: int = 2  # 2 AM daily recalculation
    SCORING_BATCH_SIZE: int = 1000
    SCORING_HISTORY_DAYS: int = 90  # Keep 90 days of calculation history
    
    # Performance
    CACHE_TTL: int = 300  # 5 minutes
    API_RATE_LIMIT: int = 100  # requests per minute
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["https://hr.gogopeaks.com", "https://localhost:3000", "http://localhost:3000"]
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["https://hr.gogopeaks.com", "https://localhost:3000", "http://localhost:3000"]
    
    @validator("ALLOWED_HOSTS", pre=True) 
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["hr.gogopeaks.com", "localhost", "127.0.0.1"]
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["hr.gogopeaks.com", "localhost", "127.0.0.1"]
    
    @validator("ALLOWED_FILE_EXTENSIONS", pre=True)
    def assemble_file_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v or v.strip() == "":
                return ["jpg", "jpeg", "png", "gif", "bmp", "webp", "pdf", "doc", "docx", "txt", "rtf", "xls", "xlsx", "csv", "ppt", "pptx", "zip", "rar", "7z", "mp4", "avi", "mov", "wmv", "mp3", "wav", "flac"]
            return [i.strip().lower() for i in v.split(",")]
        elif isinstance(v, list):
            return [ext.lower() for ext in v]
        return ["jpg", "jpeg", "png", "gif", "bmp", "webp", "pdf", "doc", "docx", "txt", "rtf", "xls", "xlsx", "csv", "ppt", "pptx", "zip", "rar", "7z", "mp4", "avi", "mov", "wmv", "mp3", "wav", "flac"]
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Create settings instance
settings = Settings()