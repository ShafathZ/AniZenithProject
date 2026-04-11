from typing import Optional

from shared.config.config_utils import Config

class FrontendContainerConfig(Config):
    """
    Configuration class with data pertaining to constants stored inside a specific container
    """
    config_file: str = "container_config.yml"
    hostname: Optional[str] = None
    port: Optional[int] = None

class FrontendAppConfig(Config):
    """
    Configuration class with data pertaining to the frontend app and its proxy service
    """
    config_file: str = "app_config.yml"
    log_level: Optional[str] = None
    proxy_hostname: Optional[str] = None
    proxy_port: Optional[int] = None
