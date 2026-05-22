from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.dependencies import DBSession
from app.schemas.dashboard import (
    DashboardDispatchSummaryResponse,
    DashboardOverviewResponse,
    DispatchLifecycleSummaryResponse,
    ManualReviewQueueResponse,
    ManualReviewSummaryResponse,
    WaterEmergencyDashboardResponse,
    WaterEmergencyDetailResponse,
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


@router.get("/manual-review/queue", response_model=ManualReviewQueueResponse)
def read_dashboard_manual_review_queue(db_session: DBSession) -> ManualReviewQueueResponse:
    read_model = DashboardReadModelService().build_manual_review_queue_from_session(db_session)
    return ManualReviewQueueResponse.model_validate(read_model)


@router.get("/dispatch", response_model=DashboardDispatchSummaryResponse)
def read_dashboard_dispatch(db_session: DBSession) -> DashboardDispatchSummaryResponse:
    read_model = DashboardReadModelService().build_dispatch_from_session(db_session)
    return DashboardDispatchSummaryResponse.model_validate(read_model)


@router.get("/water-emergency", response_model=WaterEmergencyDashboardResponse)
def read_dashboard_water_emergency(db_session: DBSession) -> WaterEmergencyDashboardResponse:
    read_model = DashboardReadModelService().build_water_emergency_from_session(db_session)
    return WaterEmergencyDashboardResponse.model_validate(read_model)


@router.get("/water-emergency/{water_emergency_id}", response_model=WaterEmergencyDetailResponse)
def read_dashboard_water_emergency_detail(
    water_emergency_id: UUID,
    db_session: DBSession,
) -> WaterEmergencyDetailResponse:
    read_model = DashboardReadModelService().build_water_emergency_detail_from_session(
        db_session,
        water_emergency_id,
    )
    if read_model is None:
        raise HTTPException(status_code=404, detail="Water Emergency record not found")
    return WaterEmergencyDetailResponse.model_validate(read_model)
