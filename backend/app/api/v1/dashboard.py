"""
Dashboard API router.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUserDep, DatabaseDep
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard import DashboardService

router = APIRouter()

@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Get dashboard overview statistics",
    description="Returns dashboard statistics based on the authenticated user's role and scope."
)
async def get_dashboard_overview(
    db: DatabaseDep,
    current_user: CurrentUserDep,
    period: str = "7d",
):
    """
    Get dashboard overview statistics based on the authenticated user's role and scope.
    """
    return await DashboardService.get_overview(db, current_user, period)
