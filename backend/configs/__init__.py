from .backend_config import BackendAppConfig, BackendContainerConfig, ModelConfig

# Python context manager global variable
backend_app_config: BackendAppConfig = BackendAppConfig.load()
backend_container_config: BackendContainerConfig = BackendContainerConfig.load()
model_config: ModelConfig = ModelConfig.load()