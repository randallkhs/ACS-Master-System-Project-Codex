from dataclasses import dataclass


@dataclass(frozen=True)
class ServicePlaceholder:
    module_name: str
    implements_business_logic: bool = False
