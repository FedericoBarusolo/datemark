import pytest

import utils.usage_db
from utils.usage_db import UsageDB
from utils import constants as cst
from models.db_collections import SubscriptionTier, UserSubscription, SubscriptionStatus

from tests import mock


@pytest.mark.unit
@pytest.mark.parametrize("project_id,database_name,output",
                         [("project00", "database_name",
                           {"project": "project00", "database": "database_name"})])
def test_init(project_id, database_name, output, monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB(project_id, database_name)
    assert usage_db.db.project == output["project"]
    assert usage_db.db.database == output["database"]


@pytest.mark.unit
def test_clear_all_collections(monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db._clear_all_collections()

    assert usage_db.db.collection(cst.USG_DB_TIERS).document("xxx").content.content == []


@pytest.mark.unit
@pytest.mark.parametrize("tier",
                         [(SubscriptionTier(tier_name="new_tier", monthly_limit=1, price_usd=1))])
def test_create_subscription_tiers(monkeypatch, tier):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db.create_subscription_tier(tier)

    assert (usage_db.db.collection(cst.USG_DB_TIERS).document("new_tier").content.content ==
            [{"monthly_limit": tier.monthly_limit, "price_usd": tier.price_usd}])
    usage_db._clear_all_collections()


@pytest.mark.unit
def test_setup(monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db.setup(reset=True)

    for tier in cst.USG_DB_TIERS_INFO:
        assert (usage_db.db.collection(cst.USG_DB_TIERS).document(tier["tier_name"]).content.content ==
                [{"monthly_limit": tier["monthly_limit"], "price_usd": tier["price_usd"]}])


@pytest.mark.unit
@pytest.mark.parametrize("tier_name", ["free", "foo"])
def test_get_subscription_tier(tier_name, monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db.setup(reset=True)

    selected = [t for t in cst.USG_DB_TIERS_INFO if t["tier_name"] == tier_name]
    if selected:
        tier_info = selected[0]

        assert usage_db.get_subscription_tier(tier_name) == SubscriptionTier(tier_name=tier_name,
                                                                             monthly_limit=tier_info["monthly_limit"],
                                                                             price_usd=tier_info["price_usd"])
    else:
        assert usage_db.get_subscription_tier(tier_name) is None


@pytest.mark.unit
@pytest.mark.parametrize("user_id,tier_name,user_email,stripe_subscription_id,expires_at",
                         [("New User", "free", "newuser@gmail.com", None, None),
                          ("New User", "free", None, None, None),
                          ("New User", "fake_tier", None, None, None),
                          ("New User", "free", None, "bohboh", "2026-01-01")])
def test_create_user(user_id, tier_name, user_email, stripe_subscription_id, expires_at, monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db.setup(reset=True)

    if tier_name not in [tier["tier_name"] for tier in cst.USG_DB_TIERS_INFO]:
        with pytest.raises(ValueError):
            user = usage_db.create_user(user_id=user_id,
                                        tier_name=tier_name,
                                        user_email=user_email,
                                        stripe_subscription_id=stripe_subscription_id,
                                        expires_at=expires_at)
    else:
        user = usage_db.create_user(user_id=user_id,
                                    tier_name=tier_name,
                                    user_email=user_email,
                                    stripe_subscription_id=stripe_subscription_id,
                                    expires_at=expires_at)

        assert user == UserSubscription(user_id=user_id,
                                        tier_name=tier_name,
                                        subscribed_at=user.subscribed_at,
                                        user_email=user_email,
                                        stripe_subscription_id=stripe_subscription_id,
                                        expires_at=expires_at,
                                        status=SubscriptionStatus.ACTIVE.value)

        entry = usage_db.db.collection(cst.USG_DB_TIERS).document(user_id).content.content[0]

        assert entry.get("tier_name") == tier_name
        assert entry.get("user_email") == user_email


@pytest.mark.unit
@pytest.mark.parametrize("user_id", ["New User", "New Userrr"])
def test_get_user(user_id, monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db.setup(reset=True)

    usage_db.create_user(user_id="New User", tier_name="free")

    entry = usage_db.get_user(user_id)

    if entry is not None:
        assert entry.user_id == user_id
        assert entry.tier_name == "free"
    else:
        assert entry is None


@pytest.mark.unit
@pytest.mark.parametrize("user_id", ["New User", "New Userrr"])
def test_get_monthly_usage(user_id, monkeypatch):
    monkeypatch.setattr(utils.usage_db.firestore, "Client", mock.mock_firestore_client)

    usage_db = UsageDB("project00", "database00")
    usage_db.setup(reset=True)

    usage_db.create_user(user_id="New User", tier_name="free")
    usage_db.increment_usage(user_id="New User", increment=1)

    count = usage_db.get_monthly_usage(user_id)

    if isinstance(count, int):
        assert count == 0
    else:
        count.value == 1
