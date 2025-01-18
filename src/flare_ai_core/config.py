import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def load_env_var(var_name: str) -> str:
    """Loads and validates environment variables."""
    env_var = os.getenv(var_name, default="")
    if not env_var:
        msg = f"'{var_name}' not found in env"
        raise ValueError(msg)
    return env_var


@dataclass(frozen=True)
class Config:
    simulate_attestation: bool


config = Config(simulate_attestation=load_env_var("SIMULATE_ATTESTATION"))
