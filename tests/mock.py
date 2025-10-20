import re
import requests

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


def mock_requests(method, url, params, headers=None):
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

    if re.match(r"https://oauth2.googleapis.com/tokeninfo", url):
        if params["access_token"] == cst.TEST_REQ_SUCC:
            return MockResponse(200, json_data={"message": cst.TEST_REQ_SUCC})
        elif params["access_token"] == cst.TEST_REQ_INVALID:
            return MockResponse(401, json_data={"message": cst.TEST_REQ_INVALID})
        else:
            return MockResponse(400, json_data={"message": cst.TEST_REQ_ERR})
    else:
        raise Exception(f"URL {url} not mocked")