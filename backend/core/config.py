"""
Environment-based configuration for EcoChain Sustainability Tracker.
Handles RPC endpoints, API keys, and other environment variables.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # FastAPI Configuration
    app_name: str = Field(default="EcoChain Sustainability Tracker", env="APP_NAME")
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8002, env="PORT")
    
    # uAgents Bureau Configuration
    bureau_port: int = Field(default=8001, env="BUREAU_PORT")
    
    # Blockchain RPC Endpoints
    ethereum_rpc_url: Optional[str] = Field(default=None, env="ETHEREUM_RPC_URL")
    polygon_rpc_url: Optional[str] = Field(default=None, env="POLYGON_RPC_URL")
    arbitrum_rpc_url: Optional[str] = Field(default=None, env="ARBITRUM_RPC_URL")
    sepolia_rpc_url: Optional[str] = Field(default=None, env="SEPOLIA_RPC_URL")
    # Web3 Configuration
    private_key: Optional[str] = Field(default=None, env="PRIVATE_KEY")
    wallet_address: Optional[str] = Field(default=None, env="WALLET_ADDRESS")
    agent_address: Optional[str] = Field(default=None, env="AGENT_ADDRESS")
    
    # Contract Addresses
    eco_credit_token_address: Optional[str] = Field(default=None, env="ECO_CREDIT_TOKEN_ADDRESS")
    sustainability_proof_address: Optional[str] = Field(default=None, env="SUSTAINABILITY_PROOF_ADDRESS")
    proof_registry_address: Optional[str] = Field(default=None, env="PROOF_REGISTRY_ADDRESS")
    
    # Token Configuration
    initial_supply: str = Field(default="10000000000000000000000000", env="INITIAL_SUPPLY")
    max_supply: str = Field(default="1000000000000000000000000000", env="MAX_SUPPLY")
    base_token_uri: str = Field(default="https://gateway.lighthouse.storage/ipfs/", env="BASE_TOKEN_URI")
    
    # API Keys
    privy_app_id: Optional[str] = Field(default=None, env="PRIVY_APP_ID")
    privy_app_secret: Optional[str] = Field(default=None, env="PRIVY_APP_SECRET")
    lighthouse_api_key: Optional[str] = Field(default=None, env="LIGHTHOUSE_API_KEY")
    metta_api_key: Optional[str] = Field(default=None, env="METTA_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    
    # MeTTa Configuration
    metta_path: str = Field(default="metta", env="METTA_PATH")
    metta_wrapper_url: Optional[str] = Field(default=None, env="METTA_WRAPPER_URL")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # CORS Configuration
    cors_origins: list[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment.lower() == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment.lower() == "production"
