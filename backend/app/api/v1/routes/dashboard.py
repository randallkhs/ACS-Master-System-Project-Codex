from fastapi import APIRouter

from app.db.dependencies import DBSession
from app.schemas.dashboard import (
    DashboardDispatchSummaryResponse,
    DashboardOverviewResponse,
    DispatchLifecycleSummaryResponse,
    ManualReviewSummaryResponse,
)
from app.services.dashboard import DashboardReadModelService

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
def read_dashboard_overview(db_session: DBSession) -> DashboardOverviewResponse:
    read_model = DashboardReadModelService().build_overview_from_session(db_session)
    return DashboardOverviewResponse.model_validate(read_model)


@router.get("/lifecycle", response_model=DispatchLifecycleSummaryResponse)
def read_dashboard_lifecycle(db_session: DBSession) -> DispatchLifecycleSummaryResponse:
    read_model = DashboardReadModelService().build_lifecycle_from_session(db_session)
    return DispatchLifecycleSummaryResponse.model_validate(read_model)


@router.get("/review", response_model=ManualReviewSummaryResponse)
def read_dashboard_review(db_session: DBSession) -> ManualReviewSummaryResponse:
    read_model = DashboardReadModelService().build_review_from_session(db_session)
    return ManualReviewSummaryResponse.model_validate(read_model)


@router.get("/dispatch", response_model=DashboardDispatchSummaryResponse)
def read_dashboard_dispatch(db_session: DBSession) -> DashboardDispatchSummaryResponse:
    read_model = DashboardReadModelService().build_dispatch_from_session(db_session)
    return DashboardDispatchSummaryResponse.model_validate(read_model)
