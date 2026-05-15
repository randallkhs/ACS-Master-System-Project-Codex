from app.adapters.base import IntegrationAdapter


class FastFieldAdapter(IntegrationAdapter):
    def __init__(self, is_configured: bool = False) -> None:
        super().__init__(name="fastfield", is_configured=is_configured)
