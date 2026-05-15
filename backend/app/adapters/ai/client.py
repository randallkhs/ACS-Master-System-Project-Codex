from app.adapters.base import IntegrationAdapter


class AIAdapter(IntegrationAdapter):
    def __init__(self, is_configured: bool = False) -> None:
        super().__init__(name="ai", is_configured=is_configured)
