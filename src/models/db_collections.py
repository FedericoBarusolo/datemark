from datetime import datetime
from typing import Optional
from enum import Enum

from dataclasses import dataclass

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


@dataclass
class SubscriptionTier:
    tier_name: str
    monthly_limit: int  # -1 for unlimited
    price_usd: float


@dataclass
class UserSubscription:
    user_id: str
    tier_name: str
    subscribed_at: datetime
    expires_at: Optional[datetime]
    stripe_subscription_id: Optional[str]
    status: str