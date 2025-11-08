from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    github_token: str = ""
    
    # Feature Flags
    use_mock_data: bool = True
    fraud_detection_strict_mode: bool = True
    
    # LLM Config
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
