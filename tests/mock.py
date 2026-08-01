import re
import json
import requests
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from models.io_models import Event
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
    def __init__(self, project_id, database_name: Optional[str] = None):
        print("mocking class UsageDB")
        self.project_id = project_id
        db_info = json.loads(database_name)
        self.database_info = MockDatabaseInfo(tier_name=db_info.get("tier_name"),
                                              monthly_usage=db_info.get("monthly_usage"))

        self.existing_users = [cst.TEST_USR_EXIST]

    def get_user(self, user_id, user_email: Optional[str] = None):
        print("mocking function get_user of class UsageDB")
        if user_id in self.existing_users:
            return UserSubscription(
                user_id=user_id,
                tier_name=self.database_info.tier_name,
                user_email=user_email,
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

    def create_user(self, user_id, user_email: Optional[str] = None, tier_name:str ="free"):
        self.existing_users.append(user_id)
        return

    def increment_usage(self, user_id, month, increment=1):
        return self.get_monthly_usage(user_id=user_id, current_month=month) + increment


def mock_init_chat_model(model, model_provider, temperature):
    print("mocking function init_chat_model")
    return None


class MockCollection:
    class MockDoc:
        class Content:
            content: list
            exists: bool

            def __init__(self, content):
                self.content = content
                self.exists = bool(len(self.content))
            def to_dict(self):
                if self.content:
                    return self.content[0]
                else:
                    return {}

        content: Content
        def __init__(self, content):
            self.content = content
            self.reference = self.Reference(self)
        def set(self, content, merge=False):
            self.content.content.append(content)
            self.content.exists = bool(len(self.content.content))
        def get(self):
            return self.content
        class Reference:
            def __init__(self, parent_doc):
                self.doc = parent_doc
            def delete(self):
                self.doc.content.content = []

    docs = [{"name": "a", "content": MockDoc(MockDoc.Content([]))}]

    def stream(self):
        return [doc["content"] for doc in self.docs]

    def document(self, doc_name):
        try:
            return [doc for doc in self.docs if doc["name"] == doc_name][0]["content"]
        except IndexError:
            new_doc = self.MockDoc(self.MockDoc.Content([]))
            self.docs += [{"name": doc_name, "content": new_doc}]
            return new_doc


class MockDb:
    def __init__(self, project, database):
        self.project = project
        self.database = database
        self.collections = [{"name": cst.USG_DB_TIERS, "content": MockCollection()},
                            {"name": cst.USG_DB_USERS, "content": MockCollection()},
                            {"name": cst.USG_DB_USAGE, "content": MockCollection()}]

    def collection(self, collection_name):
        return [coll for coll in self.collections if coll["name"] == collection_name][0]["content"]


def mock_firestore_client(project, database):
    print("mocking class firestore.Client")
    return MockDb(project=project, database=database)


class MockAgentModel:
    output_model: BaseModel

    def get(self, arg):
        return

    def with_structured_output(self, schema, method=None):
        self.output_model = schema
        return self

    async def ainvoke(self, _input):
        events = json.loads(_input[0].content)
        try:
            for ev in events:
                ev["start_time"] = datetime.strptime(ev["start_time"], cst.DATE_TIME_STANDARD_FMT)
                if ev.get("end_time"):
                    ev["end_time"] = datetime.strptime(ev["end_time"], cst.DATE_TIME_STANDARD_FMT)

            return self.output_model.model_construct(events=[Event.model_construct(**ev) for ev in events])
        except:
            return {}