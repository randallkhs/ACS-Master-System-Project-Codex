from app.adapters.base import IntegrationAdapter


class VerizonConnectAdapter(IntegrationAdapter):
    def __init__(self, is_configured: bool = False) -> None:
        super().__init__(name="verizon_connect", is_configured=is_configured)
