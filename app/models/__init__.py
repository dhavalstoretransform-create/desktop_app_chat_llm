"""Database models package."""

from app.models.ai_model import AIModel
from app.models.ai_provider import AIProvider
from app.models.audit import AuditLog
from app.models.base import BaseModel, TimestampMixin, UUIDMixin
from app.models.department import Department
from app.models.message import ChatMessage
from app.models.permission import Permission
from app.models.prompt_log import PromptLog
from app.models.recommendation import ModelRecommendation
from app.models.request import TokenRequest
from app.models.reward import PromptReward
from app.models.role import Role
from app.models.role_permission import role_permissions
from app.models.session import ChatSession
from app.models.setting import SystemSetting
from app.models.suggestion import SuggestedPrompt
from app.models.usage import TokenUsage
from app.models.user import User
from app.models.wallet import EmployeeTokenWallet

__all__ = [
    "BaseModel",
    "UUIDMixin",
    "TimestampMixin",
    "AIModel",
    "AIProvider",
    "AuditLog",
    "Department",
    "ChatMessage",
    "PromptLog",
    "ModelRecommendation",
    "TokenRequest",
    "PromptReward",
    "Permission",
    "Role",
    "role_permissions",
    "ChatSession",
    "SystemSetting",
    "SuggestedPrompt",
    "TokenUsage",
    "User",
    "EmployeeTokenWallet",
]

