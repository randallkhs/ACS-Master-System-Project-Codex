from app.adapters.base import IntegrationAdapter


class GoogleSheetsAdapter(IntegrationAdapter):
    def __init__(self, is_configured: bool = False) -> None:
        super().__init__(name="google_sheets", is_configured=is_configured)
