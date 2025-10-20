import requests

def validate_access_token(authorization):

    oauth_token = authorization.split('Bearer ')[1]

    # Validate the OAuth token
    token_info = requests.request(
        method="GET",
        url='https://oauth2.googleapis.com/tokeninfo',
        params={'access_token': oauth_token}
    )
    token_info.raise_for_status()

    return token_info.json()