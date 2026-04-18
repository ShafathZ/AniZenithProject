from pathlib import Path
from typing import Dict
import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv(".env")

# Base config file (must be included)
BASE_CONFIG_PATH = Path(__file__).parent / "base_config.yml"

# Base config dataclass
class Config(BaseModel):
    """
    Base Configuration class.

    Shared defaults are loaded from base_config.yaml.
    Mode-specific overrides are applied based on 'mode'.
    """
    # Force subclasses to define a config file
    config_file: str | Path = None
    mode: str = os.getenv("APP_ENV", "LOCAL")

    # Load method to load the data class from yaml files
    @classmethod
    def load(cls):
        """
        Load a dataclass instance by detecting the config_path and retrieving relevant data values matching fields
        """
        # 1. Create instance of the config class
        cfg_instance = cls()

        # 2. Load shared base config
        cfg_instance, _ = _load_yaml_data(BASE_CONFIG_PATH, cfg_instance)

        # Throw error if config file not set (Forces subclasses to define a config file)
        if cfg_instance.config_file is None:
            raise NotImplementedError(f"{cfg_instance.__class__.__name__} must define 'config_file' variable in {cfg_instance.__module__}.py")

        # 3. Load subclass-specific config
        # Assumes the config path is relative to the file where the path is written
        config_file_path = Path(cls.__module__.replace(".", "/")).parent / Path(cfg_instance.config_file)
        cfg_instance, set_fields = _load_yaml_data(config_file_path, cfg_instance)

        # 4. Compute what is missing at the end to warn user
        # Pydantic model_fields references the string names of all fields inside the pydantic class
        all_fields = set(cfg_instance.__class__.model_fields)
        base_fields = set(getattr(cfg_instance.__class__.__base__, "model_fields", {})) # Ignores fields in base config
        # Note: .env variable and Pydantic variable must be identical in name and capitalization
        missing = all_fields - set_fields - base_fields - os.environ.keys()
        if missing:
            print(f"Warning: Missing fields {missing} in YAML: {config_file_path}.")

        return cfg_instance

# Converter dictionary for special types that are not supported by default python/pydantic
# ex. {"torch_dtype": lambda e: torch.dtype(e)}
# TODO: Make this responsibility of sub-classes
type_converters: Dict[str, callable] = {}

# Loads a yaml file into the config object
def _load_yaml_data(path: str | Path, cfg_obj):
    path = Path(path)
    if not path.exists():
        print(f"Warning: Config file not found: {path}. Using defaults only.")
        return cfg_obj

    # Open yaml file
    with open(path, "r") as f:
        yaml_cfg = yaml.safe_load(f) or {}

    # Set an attribute inside a config file
    cfg_keys_set = set()

    def _set_attr(key, value):
        nonlocal cfg_obj
        if hasattr(cfg_obj, key):
            if key in type_converters:
                value = type_converters[key](value)
            setattr(cfg_obj, key, value)
            cfg_keys_set.add(key)
        else:
            print(f"Warning: Config key '{key}' in {path} is not registered in the {cfg_obj.__module__}.py")
    # Return if empty config
    if not yaml_cfg.get("default", {}):
        return cfg_obj, cfg_keys_set

    # 1. Load default section
    for key, value in yaml_cfg.get("default", {}).items():
        _set_attr(key, value)

    # 2. Load mode-specific section
    mode = getattr(cfg_obj, "mode", None)
    if mode:
        mode_key = mode.lower()
        for key, value in yaml_cfg.get(mode_key, {}).items():
            _set_attr(key, value)
    return cfg_obj, cfg_keys_set