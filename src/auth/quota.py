import os
from typing import Optional, Dict, Any
from datetime import date

from utils import usage_db as udb
from utils import constants as cst

from fastapi import HTTPException, status

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


def verify_user_quota(user_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that user has sufficient quota remaining to perform the requested operation.

    Checks the user's remaining monthly quota and raises HTTPException if:
    - User has exceeded their quota (remaining < 1)
    - User has only 1 credit left but is making a filtering query (requires 2 credits)

    Users with unlimited plans (remaining == -1) always pass verification.

    Args:
        user_id: Unique user identifier
        body: Request body dictionary, checked for 'user_query' field to determine
              if this is a filtering query requiring 2 credits

    Raises:
        HTTPException: 429 status if quota is exceeded or insufficient for the operation

    Returns:
        Dict containing user quota information with keys: user_id, tier_name,
        monthly_limit, current_month, usage_this_month, remaining, is_unlimited, status
    """
    quota_info = get_or_create_user_quota(user_id=user_id)

    logger.info(quota_info)

    if quota_info["remaining"] == -1:
        logger.info(f"User {user_id} has unlimited plan: access granted!")

    elif quota_info['remaining'] < 1:
        logger.info(f"Exceeded quota for user {user_id}: raising HTTP Error")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Period quota exceeded. Please contact the developer at: infodatemark@gmail.com."
        )

    elif quota_info['remaining'] < 2 and body.get("user_query"):
        logger.info(f"Insufficient quota with user_query for user {user_id}: raising HTTP Error")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Only one left usage credit in the period quota (filtering query requires 2). Please either "
                   "delete the filtering query or contact the developer at: infodatemark@gmail.com."
        )

    logger.info(f"Remaining quota for user {user_id}: {quota_info['remaining']} "
                f"of {limit if (limit:=quota_info['monthly_limit'])!=-1 else '<unlimited>'}")

    return quota_info