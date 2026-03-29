from .configurations import FrontendContainerConfig, FrontendAppConfig

# Python context manager global variable
frontend_container_config: FrontendContainerConfig = FrontendContainerConfig.load()
frontend_app_config: FrontendAppConfig = FrontendAppConfig.load()