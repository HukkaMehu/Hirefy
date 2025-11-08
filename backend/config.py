from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import List, Dict

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

    # Fraud Detector Config
    unprofessional_titles: List[str] = ["ninja", "guru", "rockstar", "wizard"]
    skills_to_check: List[str] = ["python", "javascript", "typescript", "java", "go", "rust"]
    skill_map: Dict[str, str] = {
        "react": "javascript",
        "node.js": "javascript",
        "django": "python",
        "flask": "python"
    }
    employment_gap_threshold: int = 6
    avg_rating_threshold: float = 6.5
    rehire_concern_threshold: int = 2

    # Backend Config
    cors_allow_origins: List[str] = ["http://localhost:3000"]

    # File Paths
    transcript_output_dir: str = "./transcripts"
    email_log_base_dir: str = "./transcripts"
    template_dir: str = "templates"

    # Email Conversation Config
    poll_interval_seconds: int = 10
    completion_keywords: List[str] = ['thank you for', 'verification complete', 'all set', 'that\'s all', 'have everything']
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
