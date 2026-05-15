from app.adapters.base import IntegrationAdapter


class GoogleCalendarAdapter(IntegrationAdapter):
    def __init__(self, is_configured: bool = False) -> None:
        super().__init__(name="google_calendar", is_configured=is_configured)
