import re
import json
import requests
from datetime import datetime
from typing import List

from models.db_collections import UserSubscription, SubscriptionTier
from utils import constants as cst

class MockResponse(requests.Response):
    """Mock class representing a successful HTTP response (2xx status).

    Attributes:
        status_code: int
            The HTTP status code of the response.
        json_data: dict
            The primary JSON data to include in the response.
    """

    def __init__(self, status_code, json_data=None):
        super().__init__()
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        """Return a combined JSON payload including the status code.

        Returns:
            dict: Combined data with status_code and original json_data.
        """
        return {"status_code": self.status_code, **self.json_data}


def mock_requests(method, url, params=None, headers=None):
    """Mock HTTP request handler returning predefined responses based on URL patterns.

    Args:
        method: str
            The HTTP method (e.g., 'GET', 'POST') - unused in mock.
        url: str
            The URL path to match against predefined patterns.
        headers: dict
            Request headers - unused in mock.
        params: dict
            Request parameters.

    Returns:
        MockResponse: Configured mock response based on URL pattern:
            - 200 with 'get_dpm' for /systems/[id]/graph paths.
            - 200 with system info for /systems/[id] paths.
    """
    print("mocking function request")

    if re.match(r"https://www.googleapis.com/oauth2/v2/userinfo", url):
        if headers["Authorization"].split("Bearer ")[1] == cst.TEST_REQ_SUCC:
            return MockResponse(200, json_data={"message": cst.TEST_REQ_SUCC})
        elif headers["Authorization"].split("Bearer ")[1] == cst.TEST_REQ_INVALID:
            return MockResponse(401, json_data={"message": cst.TEST_REQ_INVALID})
        else:
            return MockResponse(400, json_data={"message": cst.TEST_REQ_ERR})
    else:
        raise Exception(f"URL {url} not mocked")


class MockDatabaseInfo:
    tier_name: str
    monthly_usage: int

    def __init__(self, tier_name, monthly_usage):
        self.tier_name = tier_name
        self.monthly_usage = monthly_usage


class MockUsageDB:
    project_id: str
    database_info: MockDatabaseInfo

    existing_users: List

    # use database_name to pass content for testing purposes
    def __init__(self, project_id, database_name: str | None = None):
        print("mocking class UsageDB")
        self.project_id = project_id
        db_info = json.loads(database_name)
        self.database_info = MockDatabaseInfo(tier_name=db_info.get("tier_name"),
                                              monthly_usage=db_info.get("monthly_usage"))

        self.existing_users = [cst.TEST_USR_EXIST]

    def get_user(self, user_id):
        print("mocking function get_user of class UsageDB")
        if user_id in self.existing_users:
            return UserSubscription(
                user_id=user_id,
                tier_name=self.database_info.tier_name,
                subscribed_at=datetime.strptime(cst.TEST_DATE, cst.DATE_STANDARD_FMT),
                expires_at=datetime.strptime(cst.TEST_DATE_2, cst.DATE_STANDARD_FMT),
                stripe_subscription_id="",
                status="active",
            )
        else:
            return None

    def get_subscription_tier(self, tier_name):
        print("mocking function get_subscription_tier of class UsageDB")
        tier = [t for t in cst.USG_DB_TIERS_INFO if t["tier_name"] == tier_name]

        if tier:
            return SubscriptionTier(
                tier_name=tier[0]["tier_name"],
                monthly_limit=tier[0]["monthly_limit"],
                price_usd=tier[0]["price_usd"]
            )
        else:
            return None

    def get_monthly_usage(self, user_id, current_month):
        print("mocking function get_monthly_usage of class UsageDB")
        return self.database_info.monthly_usage

    def create_user(self, user_id, tier_name="free"):
        self.existing_users.append(user_id)
        return

    def increment_usage(self, user_id, month, increment=1):
        return self.get_monthly_usage(user_id=user_id, current_month=month) + increment