from dataclasses import dataclass

from flare_ai_core.config import Config, load_env_var
from flare_ai_core.config import config as base_config


@dataclass(frozen=True)
class OnchainConfig(Config):
    rpc_url: str


config = OnchainConfig(
    **vars(base_config),
    rpc_url=load_env_var("RPC_URL"),
)
