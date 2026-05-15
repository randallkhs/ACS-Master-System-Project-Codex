from app.adapters.ai.client import AIAdapter
from app.adapters.fastfield.client import FastFieldAdapter
from app.adapters.google_calendar.client import GoogleCalendarAdapter
from app.adapters.google_sheets.client import GoogleSheetsAdapter
from app.adapters.verizon_connect.client import VerizonConnectAdapter


def test_integration_adapters_are_placeholders_not_live_clients() -> None:
    adapters = [
        GoogleCalendarAdapter(),
        GoogleSheetsAdapter(),
        FastFieldAdapter(),
        VerizonConnectAdapter(),
        AIAdapter(),
    ]

    assert [adapter.name for adapter in adapters] == [
        "google_calendar",
        "google_sheets",
        "fastfield",
        "verizon_connect",
        "ai",
    ]
    assert all(not adapter.is_configured for adapter in adapters)
