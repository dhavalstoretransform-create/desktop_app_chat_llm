"""
Dashboard service.
"""

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from datetime import timezone

from app.models.user import User
from app.models.department import Department
from app.models.session import ChatSession
from app.models.prompt_log import PromptLog
from app.models.usage import TokenUsage
from app.models.ai_model import AIModel
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    UsersStats,
    DepartmentsStats,
    ConversationStats,
    AIRequestStats,
    TokenStats,
    CostStats,
    ModelStats,
    TimeSeriesData,
    ModelDistributionData,
    DepartmentUserData,
    ActivityLogData,
    SystemHealth,
)

class DashboardService:
    @staticmethod
    async def get_overview(db: AsyncSession, current_user: User, period: str = "7d") -> DashboardOverviewResponse:
        role_code = current_user.role.code if current_user.role else "VIEWER"
        
        scope = "READONLY"
        
        # Period parsing
        days = 7
        if period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        cutoff_date = datetime.datetime.now(timezone.utc).date() - datetime.timedelta(days=days)
        
        # Base queries for scalar metrics
        users_query = select(func.count(User.id), func.count(User.id).filter(User.is_active == True), func.count(User.id).filter(User.is_active == False))
        deps_query = select(func.count(Department.id), func.count(Department.id).filter(Department.is_active == True), func.count(Department.id).filter(Department.is_active == False))
        conv_query = select(func.count(ChatSession.id))
        ai_req_query = select(func.count(PromptLog.id))
        usage_query = select(func.sum(TokenUsage.total_tokens), func.sum(TokenUsage.total_cost))
        model_query = select(func.count(AIModel.id))

        # Base queries for analytics
        ts_usage_query = select(
            TokenUsage.usage_date, 
            func.count(TokenUsage.id),
            func.sum(TokenUsage.input_tokens),
            func.sum(TokenUsage.output_tokens),
            func.sum(TokenUsage.total_tokens)
        ).where(TokenUsage.usage_date >= cutoff_date).group_by(TokenUsage.usage_date).order_by(TokenUsage.usage_date)
        
        model_dist_query = select(
            AIModel.name,
            func.count(TokenUsage.id),
            func.sum(TokenUsage.total_tokens)
        ).join(AIModel, TokenUsage.model_id == AIModel.id).group_by(AIModel.name)
        
        dept_users_query = select(
            Department.name,
            func.count(User.id)
        ).join(Department, User.department_id == Department.id).group_by(Department.name)
        
        recent_activity_query = select(
            PromptLog.id,
            PromptLog.created_at,
            User.full_name,
            AIModel.name
        ).join(User, PromptLog.user_id == User.id).join(AIModel, PromptLog.model_id == AIModel.id).order_by(desc(PromptLog.created_at)).limit(10)
        
        # System Health (Basic check)
        try:
            await db.execute(select(1))
            db_status = "Healthy"
        except Exception:
            db_status = "Unavailable"
        
        system_health = SystemHealth(api_status="Healthy", database=db_status, ai_providers="Healthy")
        
        res_data = {
            "role": role_code,
            "scope": "READONLY",
            "users": None,
            "departments": None,
            "conversations": None,
            "ai_requests": None,
            "tokens": None,
            "cost": None,
            "models": None,
            "ai_usage": [],
            "model_distribution": [],
            "department_users": [],
            "recent_activity": [],
            "system_health": system_health
        }

        if role_code in ["SUPER_ADMIN", "ADMIN"]:
            res_data["scope"] = "PLATFORM" if role_code == "SUPER_ADMIN" else "ORGANIZATION"
            
            # Scalars
            users_res = (await db.execute(users_query)).first()
            if users_res:
                res_data["users"] = UsersStats(total=users_res[0] or 0, active=users_res[1] or 0, inactive=users_res[2] or 0)
            
            deps_res = (await db.execute(deps_query)).first()
            if deps_res:
                res_data["departments"] = DepartmentsStats(total=deps_res[0] or 0, active=deps_res[1] or 0, inactive=deps_res[2] or 0)
            
            res_data["conversations"] = ConversationStats(total=(await db.execute(conv_query)).scalar() or 0)
            res_data["ai_requests"] = AIRequestStats(total=(await db.execute(ai_req_query)).scalar() or 0)
            
            usage_res = (await db.execute(usage_query)).first()
            if usage_res:
                res_data["tokens"] = TokenStats(total=usage_res[0] or 0)
                res_data["cost"] = CostStats(estimated_total=float(usage_res[1] or 0.0))
            
            res_data["models"] = ModelStats(total=(await db.execute(model_query)).scalar() or 0)
            
            # Analytics
            ts_res = (await db.execute(ts_usage_query)).all()
            res_data["ai_usage"] = [TimeSeriesData(date=str(r[0]), requests=r[1] or 0, input_tokens=r[2] or 0, output_tokens=r[3] or 0, total_tokens=r[4] or 0) for r in ts_res]
            
            md_res = (await db.execute(model_dist_query)).all()
            res_data["model_distribution"] = [ModelDistributionData(model=r[0], requests=r[1] or 0, tokens=r[2] or 0) for r in md_res]
            
            du_res = (await db.execute(dept_users_query)).all()
            res_data["department_users"] = [DepartmentUserData(department=r[0], users=r[1] or 0) for r in du_res]
            
            ra_res = (await db.execute(recent_activity_query)).all()
            res_data["recent_activity"] = [ActivityLogData(id=str(r[0]), type="AI_REQUEST", user=r[2], model=r[3], timestamp=r[1], description=f"AI Request by {r[2]} using {r[3]}") for r in ra_res]

        elif role_code == "MANAGER":
            res_data["scope"] = "DEPARTMENT"
            dept_id = current_user.department_id
            
            # Filters
            users_query = select(func.count(User.id), func.count(User.id).filter(User.is_active == True)).where(User.department_id == dept_id)
            conv_query = conv_query.join(User, ChatSession.user_id == User.id).where(User.department_id == dept_id)
            ai_req_query = ai_req_query.join(User, PromptLog.user_id == User.id).where(User.department_id == dept_id)
            usage_query = usage_query.join(User, TokenUsage.user_id == User.id).where(User.department_id == dept_id)
            ts_usage_query = ts_usage_query.join(User, TokenUsage.user_id == User.id).where(User.department_id == dept_id)
            model_dist_query = model_dist_query.join(User, TokenUsage.user_id == User.id).where(User.department_id == dept_id)
            recent_activity_query = recent_activity_query.where(User.department_id == dept_id)
            
            team_res = (await db.execute(users_query)).first()
            if team_res:
                res_data["users"] = UsersStats(total=team_res[0] or 0, active=team_res[1] or 0, inactive=(team_res[0] or 0) - (team_res[1] or 0))
            
            res_data["conversations"] = ConversationStats(total=(await db.execute(conv_query)).scalar() or 0)
            res_data["ai_requests"] = AIRequestStats(total=(await db.execute(ai_req_query)).scalar() or 0)
            
            usage_res = (await db.execute(usage_query)).first()
            if usage_res:
                res_data["tokens"] = TokenStats(total=usage_res[0] or 0)
                res_data["cost"] = CostStats(estimated_total=float(usage_res[1] or 0.0))
                
            ts_res = (await db.execute(ts_usage_query)).all()
            res_data["ai_usage"] = [TimeSeriesData(date=str(r[0]), requests=r[1] or 0, input_tokens=r[2] or 0, output_tokens=r[3] or 0, total_tokens=r[4] or 0) for r in ts_res]
            
            md_res = (await db.execute(model_dist_query)).all()
            res_data["model_distribution"] = [ModelDistributionData(model=r[0], requests=r[1] or 0, tokens=r[2] or 0) for r in md_res]
            
            ra_res = (await db.execute(recent_activity_query)).all()
            res_data["recent_activity"] = [ActivityLogData(id=str(r[0]), type="AI_REQUEST", user=r[2], model=r[3], timestamp=r[1], description=f"AI Request by {r[2]} using {r[3]}") for r in ra_res]

        elif role_code == "EMPLOYEE":
            res_data["scope"] = "PERSONAL"
            user_id = current_user.id
            
            conv_query = conv_query.where(ChatSession.user_id == user_id)
            ai_req_query = ai_req_query.where(PromptLog.user_id == user_id)
            usage_query = usage_query.where(TokenUsage.user_id == user_id)
            ts_usage_query = ts_usage_query.where(TokenUsage.user_id == user_id)
            model_dist_query = model_dist_query.where(TokenUsage.user_id == user_id)
            recent_activity_query = recent_activity_query.where(PromptLog.user_id == user_id)
            
            res_data["conversations"] = ConversationStats(total=(await db.execute(conv_query)).scalar() or 0)
            res_data["ai_requests"] = AIRequestStats(total=(await db.execute(ai_req_query)).scalar() or 0)
            
            usage_res = (await db.execute(usage_query)).first()
            if usage_res:
                res_data["tokens"] = TokenStats(total=usage_res[0] or 0)
                res_data["cost"] = CostStats(estimated_total=float(usage_res[1] or 0.0))
                
            ts_res = (await db.execute(ts_usage_query)).all()
            res_data["ai_usage"] = [TimeSeriesData(date=str(r[0]), requests=r[1] or 0, input_tokens=r[2] or 0, output_tokens=r[3] or 0, total_tokens=r[4] or 0) for r in ts_res]
            
            md_res = (await db.execute(model_dist_query)).all()
            res_data["model_distribution"] = [ModelDistributionData(model=r[0], requests=r[1] or 0, tokens=r[2] or 0) for r in md_res]
            
            ra_res = (await db.execute(recent_activity_query)).all()
            res_data["recent_activity"] = [ActivityLogData(id=str(r[0]), type="AI_REQUEST", user=r[2], model=r[3], timestamp=r[1], description=f"AI Request by {r[2]} using {r[3]}") for r in ra_res]

        return DashboardOverviewResponse(**res_data)
