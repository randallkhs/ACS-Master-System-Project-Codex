from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationAdapter:
    name: str
    is_configured: bool = False
