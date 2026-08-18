"""
Dashboard Pydantic schemas for response serialization.
"""

from __future__ import annotations

from datetime import datetime, date
from pydantic import BaseModel, Field

class UsersStats(BaseModel):
    total: int = Field(default=0)
    active: int = Field(default=0)
    inactive: int = Field(default=0)

class DepartmentsStats(BaseModel):
    total: int = Field(default=0)
    active: int = Field(default=0)
    inactive: int = Field(default=0)

class ConversationStats(BaseModel):
    total: int = Field(default=0)

class AIRequestStats(BaseModel):
    total: int = Field(default=0)

class TokenStats(BaseModel):
    total: int = Field(default=0)

class CostStats(BaseModel):
    estimated_total: float = Field(default=0.0)

class ModelStats(BaseModel):
    total: int = Field(default=0)

class TimeSeriesData(BaseModel):
    date: str
    requests: int = Field(default=0)
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)

class ModelDistributionData(BaseModel):
    model: str
    requests: int = Field(default=0)
    tokens: int = Field(default=0)

class DepartmentUserData(BaseModel):
    department: str
    users: int = Field(default=0)

class ActivityLogData(BaseModel):
    id: str | None = None
    type: str
    user: str
    model: str | None = None
    timestamp: datetime
    description: str

class SystemHealth(BaseModel):
    api_status: str
    database: str
    ai_providers: str

class DashboardOverviewResponse(BaseModel):
    role: str
    scope: str
    
    users: UsersStats | None = None
    departments: DepartmentsStats | None = None
    conversations: ConversationStats | None = None
    ai_requests: AIRequestStats | None = None
    tokens: TokenStats | None = None
    cost: CostStats | None = None
    models: ModelStats | None = None
    
    ai_usage: list[TimeSeriesData] = Field(default_factory=list)
    model_distribution: list[ModelDistributionData] = Field(default_factory=list)
    department_users: list[DepartmentUserData] = Field(default_factory=list)
    recent_activity: list[ActivityLogData] = Field(default_factory=list)
    system_health: SystemHealth | None = None
