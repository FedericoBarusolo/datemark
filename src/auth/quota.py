import os
from typing import Optional, Dict, Any
from datetime import date

from utils import usage_db as udb
from utils import constants as cst

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def get_user_quota(user_id: str, usage_db: udb.UsageDB | None = None) -> Optional[Dict[str, Any]]:
    """
    Get user's quota information including tier limits and current usage.

    Args:
        user_id: Unique user identifier
        usage_db: Instance of usage db if already present

    Returns:
        Dict with monthly_limit, current_usage, remaining, tier_name
    """
    if usage_db is None:
        usage_db = udb.UsageDB(project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                               database_name=os.environ.get("USAGE_DB_NAME"))

    user = usage_db.get_user(user_id)
    if not user:
        return None

    tier = usage_db.get_subscription_tier(user.tier_name)
    if not tier:
        return None

    # Get today's usage
    current_month = date.today().strftime(cst.DATE_STANDARD_MONTH)
    usage_count = usage_db.get_monthly_usage(user_id, current_month)

    # Calculate remaining
    remaining = tier.monthly_limit - usage_count if tier.monthly_limit > 0 else -1

    return {
        'user_id': user_id,
        'tier_name': user.tier_name,
        'monthly_limit': tier.monthly_limit,
        'current_month': current_month,
        'usage_this_month': usage_count,
        'remaining': remaining,
        'is_unlimited': tier.monthly_limit == -1,
        'status': user.status
    }


def get_or_create_user_quota(user_id: str, user_email: Optional[str] = None):
    """
    Get user's quota information including tier limits and current usage, if the
    user_id associated to the passed oauth_token does not match any user_id in the
    database, insert a new user with a free subscription.

    Args:
        user_id: Unique user identifier
        user_email: Optional user email

    Returns:
        Dict with monthly_limit, current_usage, remaining, tier_name
    """
    usage_db = udb.UsageDB(project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                           database_name=os.environ.get("USAGE_DB_NAME"))

    logging.info(f"Authenticated user {user_id}")

    user = usage_db.get_user(user_id)
    if not user:
        usage_db.create_user(user_id=user_id,
                             tier_name="free",
                             user_email=user_email)
        logging.info(f"First access: user {user_id} created!")

    return get_user_quota(user_id, usage_db)


def increment_user_usage(user_id: str, increment: int = 1):
    """
    Increment user's monthly quota by an amount of units defined by argument increment.

    Args:
        user_id: Unique user identifier
        increment: Amount to increment (default: 1)

    Returns:
        New usage count
    """
    usage_db = udb.UsageDB(project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                           database_name=os.environ.get("USAGE_DB_NAME"))

    user = usage_db.get_user(user_id)
    if not user:
        return None

    current_month = date.today().strftime(cst.DATE_STANDARD_MONTH)
    usage_count = usage_db.increment_usage(user_id=user_id, increment=increment, month=current_month)

    return usage_count
