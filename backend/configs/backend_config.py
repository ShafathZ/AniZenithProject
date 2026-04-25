import os
from typing import Optional

from common.config.config_utils import Config

class BackendContainerConfig(Config):
    """
    Configuration class for backend container specifications (e.g. hostname and port)
    """
    config_file: str = "container_config.yml"

    hostname: Optional[str] = None
    port: Optional[int] = None

class BackendAppConfig(Config):
    """
    Configuration class for backend application, mainly for app-level properties
    """
    config_file: str = "app_config.yml"

    log_level: Optional[str] = None
    session_cookie_name: Optional[str] = None
    max_session_cookie_age: Optional[int] = None
    same_site_protection: Optional[str] = None

    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    MAL_CLIENT_ID: str = os.getenv("MAL_CLIENT_ID", "")
    MAL_CLIENT_SECRET: str = os.getenv("MAL_CLIENT_SECRET", "")
    BACKEND_SECRET: str = os.getenv("BACKEND_SECRET", "")
    ATLAS_URI: str = os.getenv("ATLAS_URI", "")

class ModelConfig(Config):
    """
    Configuration class for backend chatbot and associated parameters
    """
    config_file: str = "model_config.yml"

    # Chatbot parameters
    local_model_id: Optional[str] = None
    external_model_id: Optional[str] = None
    max_new_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    system_prompt: Optional[str] = None
