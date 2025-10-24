from typing import Optional, Dict, Any
from datetime import date, datetime

from utils import constants as cst
from models.db_collections import SubscriptionTier, UserSubscription, SubscriptionStatus

from google.cloud import firestore

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class UsageDB:
    """
    Handles all Firestore operations for user subscriptions and usage tracking.

    Collections:
    - subscription_tiers: Available subscription plans
    - user_subscriptions: User subscription information
    - daily_usage: Daily usage counts per user
    """

    def __init__(self, project_id: str, database_name: str, credentials_path: Optional[str] = None):
        """
        Initialize Firestore client.

        Args:
            project_id: GCP project ID
            database_name: Database name
            credentials_path: Optional path to service account JSON
        """
        if credentials_path:
            self.db = firestore.Client.from_service_account_json(
                credentials_path,
                project=project_id
            )
        else:
            # Uses application default credentials
            self.db = firestore.Client(project=project_id, database=database_name)

    def _clear_all_collections(self):
        """Delete all documents in all collections (use with caution!)"""
        collections = [
            cst.USG_DB_TIERS,
            cst.USG_DB_USERS,
            cst.USG_DB_USAGE
        ]

        for collection_name in collections:
            docs = self.db.collection(collection_name).stream()
            for doc in docs:
                doc.reference.delete()

        logger.info("All collections cleared")

    def create_subscription_tier(self, tier: SubscriptionTier):
        """Create or update a subscription tier."""
        self.db.collection(cst.USG_DB_TIERS).document(tier.tier_name).set({
            'monthly_limit': tier.monthly_limit,
            'price_usd': tier.price_usd
        })

    def setup(self, reset: bool = False):
        """
        Initialize database with default subscription tiers.
        Used for testing and initial project setup.

        Args:
            reset: If True, deletes existing data before setup
        """
        if reset:
            self._clear_all_collections()

        # Default subscription tiers
        default_tiers = [
            SubscriptionTier(
                tier_name="free",
                monthly_limit=3,
                price_usd=0.00
            ),
            SubscriptionTier(
                tier_name="basic",
                monthly_limit=50,
                price_usd=9.99
            ),
            SubscriptionTier(
                tier_name="pro",
                monthly_limit=200,
                price_usd=29.99
            ),
            SubscriptionTier(
                tier_name="unlimited",
                monthly_limit=-1,
                price_usd=99.99
            )
        ]

        for tier in default_tiers:
            self.create_subscription_tier(tier)

        logger.info(f"Setup complete: {len(default_tiers)} tiers created")

    def get_subscription_tier(self, tier_name: str) -> Optional[SubscriptionTier]:
        """Get subscription tier details."""
        doc = self.db.collection(cst.USG_DB_TIERS).document(tier_name).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        return SubscriptionTier(
            tier_name=tier_name,
            monthly_limit=data['monthly_limit'],
            price_usd=data['price_usd']
        )

    def create_user(
            self,
            user_id: str,
            tier_name: str = "free",
            stripe_subscription_id: Optional[str] = None,
            expires_at: Optional[datetime] = None
    ) -> UserSubscription:
        """
        Create a new user subscription document.

        Args:
            user_id: Unique user identifier
            tier_name: Subscription tier (default: "free")
            stripe_subscription_id: Optional Stripe subscription ID
            expires_at: Optional expiration datetime

        Returns:
            UserSubscription object
        """
        # Verify tier exists
        tier = self.get_subscription_tier(tier_name)
        if not tier:
            raise ValueError(f"Subscription tier '{tier_name}' does not exist")

        user_data = {
            'tier_name': tier_name,
            'subscribed_at': firestore.SERVER_TIMESTAMP,
            'status': SubscriptionStatus.ACTIVE.value
        }

        if stripe_subscription_id:
            user_data['stripe_subscription_id'] = stripe_subscription_id

        if expires_at:
            user_data['expires_at'] = expires_at

        self.db.collection(cst.USG_DB_USERS).document(user_id).set(user_data)

        return UserSubscription(
            user_id=user_id,
            tier_name=tier_name,
            subscribed_at=datetime.now(),
            expires_at=expires_at,
            stripe_subscription_id=stripe_subscription_id,
            status=SubscriptionStatus.ACTIVE.value
        )

    def get_user(self, user_id: str) -> Optional[UserSubscription]:
        """Get user subscription details."""
        doc = self.db.collection(cst.USG_DB_USERS).document(user_id).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        return UserSubscription(
            user_id=user_id,
            tier_name=data['tier_name'],
            subscribed_at=data['subscribed_at'],
            expires_at=data.get('expires_at'),
            stripe_subscription_id=data.get('stripe_subscription_id'),
            status=data['status']
        )

    def get_monthly_usage(self, user_id: str, month: Optional[str] = None) -> int:
        """
        Get user's usage count for a specific month.

        Args:
            user_id: User identifier
            month: Month in YYYY-MM format (defaults to current month)

        Returns:
            Usage count for the month
        """
        if not month:
            month = date.today().strftime("%Y-%m")

        doc = self.db.collection(cst.USG_DB_USAGE).document(
            f"{user_id}_{month}"
        ).get()

        if not doc.exists:
            return 0

        return doc.to_dict().get('count', 0)

    def increment_usage(self, user_id: str, increment: int = 1, month: Optional[str] = None) -> int:
        """
        Increment user's monthly usage count atomically.

        Args:
            user_id: User identifier
            increment: Amount to increment (default: 1)
            month: Month in YYYY-MM format (defaults to current month)

        Returns:
            New usage count
        """
        if not month:
            month = date.today().strftime("%Y-%m")

        usage_ref = self.db.collection(cst.USG_DB_USAGE).document(
            f"{user_id}_{month}"
        )

        # Atomic increment
        usage_ref.set({
            'user_id': user_id,
            'month': month,
            'count': firestore.Increment(increment),
            'last_updated': firestore.SERVER_TIMESTAMP
        }, merge=True)

        # Get updated count
        doc = usage_ref.get()
        return doc.to_dict()['count'] if doc.exists else increment