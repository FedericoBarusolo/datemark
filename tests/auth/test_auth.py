import pytest
import requests

from utils import constants as cst
from auth.auth import validate_access_token

from tests.mock import mock_requests

@pytest.mark.unit
@pytest.mark.parametrize("authorization,expected",
                         [(f"Bearer {cst.TEST_REQ_SUCC}",
                           {"status_code": 200, "message": cst.TEST_REQ_SUCC}),
                          (f"Bearer {cst.TEST_REQ_INVALID}",
                           {"status_code": 401, "message": "401 Client Error"}),
                          (f"Bearer Foo",
                           {"status_code": 400, "message": "400 Client Error"})
                          ])
def test_validate_access_token(authorization, expected, monkeypatch):
    monkeypatch.setattr(requests, "request", mock_requests)

    if expected["status_code"] in [400, 401]:
        with pytest.raises(requests.exceptions.HTTPError, match=expected["message"]):
            validate_access_token(authorization)
    else:
        response = validate_access_token(authorization)
        assert response == expected