import requests
from typing import Dict, Any, Optional

def validate_access_token(authorization: str) -> Dict[str, Any]:
    """
    Validates a Google OAuth access token.

    Extracts the OAuth token from the authorization header and validates it
    by calling Google's tokeninfo endpoint.

    Args:
        authorization: The authorization header value in the format
            'Bearer <token>'.

    Returns:
        Token information from Google's tokeninfo endpoint, including
        fields like 'azp', 'aud', 'scope', 'exp', and 'email'.

    Raises:
        IndexError: If the authorization header is not in the expected format.
        requests.HTTPError: If the token is invalid or the API request fails.
    """
    oauth_token = authorization.split('Bearer ')[1]

    # Validate the OAuth token
    token_info = requests.request(
        method="GET",
        url='https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {oauth_token}'}
    )
    token_info.raise_for_status()

    return token_info.json()