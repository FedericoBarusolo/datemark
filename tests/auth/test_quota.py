import os
import json

import pytest
from datetime import date

from utils import constants as cst
from auth import quota as qt

from tests.mock import MockUsageDB
from utils import usage_db


@pytest.mark.unit
@pytest.mark.parametrize("user_id,tier_name,monthly_usage,output",
                         [("New User", "free", 2, None),

                          (cst.TEST_USR_EXIST, "Fake Tier", 2, None),

                          (cst.TEST_USR_EXIST, "free", 2,
                           {'user_id': cst.TEST_USR_EXIST,
                            'tier_name': "free",
                            'current_month': date.today().strftime(cst.DATE_STANDARD_MONTH),
                            'usage_this_month': 2,
                            'status': "active"}),

                          (cst.TEST_USR_EXIST, "pro", 2,
                           {'user_id': cst.TEST_USR_EXIST,
                            'tier_name': "pro",
                            'current_month': date.today().strftime(cst.DATE_STANDARD_MONTH),
                            'usage_this_month': 2,
                            'status': "active"}),

                          (cst.TEST_USR_EXIST, "basic", 2,
                           {'user_id': cst.TEST_USR_EXIST,
                            'tier_name': "pro",
                            'current_month': date.today().strftime(cst.DATE_STANDARD_MONTH),
                            'usage_this_month': 2,
                            'status': "active"}),

                          (cst.TEST_USR_EXIST, "unlimited", 1,
                           {'user_id': cst.TEST_USR_EXIST,
                            'tier_name': "pro",
                            'current_month': date.today().strftime(cst.DATE_STANDARD_MONTH),
                            'usage_this_month': 1,
                            'status': "active"})

                          ])
def test_get_user_quota(user_id, tier_name, monthly_usage, output, monkeypatch):
    monkeypatch.setattr(usage_db, 'UsageDB', MockUsageDB)

    os.environ["USAGE_DB_NAME"] = json.dumps({"tier_name": tier_name, "monthly_usage": monthly_usage})

    if output is not None:
        tier = MockUsageDB("foo", "{}").get_subscription_tier(tier_name)
        is_unlimited = tier.monthly_limit == -1

        output.update({'tier_name': tier_name,
                       'usage_this_month': monthly_usage,
                       'status': 'active',
                       'monthly_limit': tier.monthly_limit,
                       'remaining': tier.monthly_limit - monthly_usage if not is_unlimited else -1,
                       'is_unlimited': is_unlimited,
                       })

    assert qt.get_user_quota(user_id) == output



@pytest.mark.unit
@pytest.mark.parametrize("user_id,tier_name,monthly_usage,output",
                         [("New User", "free", 0,
                           {'user_id': "New User",
                            'tier_name': "free",
                            'current_month': date.today().strftime(cst.DATE_STANDARD_MONTH),
                            'usage_this_month': 0,
                            'status': "active"}),

                          (cst.TEST_USR_EXIST, "Fake Tier", 2, None),

                          (cst.TEST_USR_EXIST, "free", 2,
                           {'user_id': cst.TEST_USR_EXIST,
                            'tier_name': "free",
                            'current_month': date.today().strftime(cst.DATE_STANDARD_MONTH),
                            'usage_this_month': 2,
                            'status': "active"})

                          ])
def test_get_or_create_user_quota(user_id, tier_name, monthly_usage, output, monkeypatch):
    monkeypatch.setattr(usage_db, 'UsageDB', MockUsageDB)

    os.environ["USAGE_DB_NAME"] = json.dumps({"tier_name": tier_name, "monthly_usage": monthly_usage})

    if output is not None:
        tier = MockUsageDB("foo", "{}").get_subscription_tier(tier_name)
        is_unlimited = tier.monthly_limit == -1

        output.update({'tier_name': tier_name,
                       'usage_this_month': monthly_usage,
                       'status': 'active',
                       'monthly_limit': tier.monthly_limit,
                       'remaining': tier.monthly_limit - monthly_usage if not is_unlimited else -1,
                       'is_unlimited': is_unlimited,
                       })

    assert qt.get_or_create_user_quota(user_id) == output



@pytest.mark.unit
@pytest.mark.parametrize("user_id,tier_name,monthly_usage,increment,output",
                         [("Unknown User", "free", 0, None, None),
                          (cst.TEST_USR_EXIST, "free", 2, None, 3),
                          (cst.TEST_USR_EXIST, "unlimited", 100, None, 101),

                          # same tests but with increment=2
                          ("Unknown User", "free", 0, 2, None),
                          (cst.TEST_USR_EXIST, "free", 2, 2, 4),
                          (cst.TEST_USR_EXIST, "unlimited", 100, 2, 102)
                          ])
def test_increment_user_usage(user_id, tier_name, monthly_usage, increment, output, monkeypatch):
    monkeypatch.setattr(usage_db, 'UsageDB', MockUsageDB)
    os.environ["USAGE_DB_NAME"] = json.dumps({"tier_name": tier_name, "monthly_usage": monthly_usage})

    args = dict(user_id=user_id)
    if increment is not None:
        args.update(dict(increment=increment))

    assert qt.increment_user_usage(**args) == output
