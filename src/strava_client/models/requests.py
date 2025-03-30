from datetime import datetime

from pydantic import model_validator
from strava_client.models.base import StravaBaseModel


class StravaGetTokenRequest(StravaBaseModel):
    """
    Model with the request parameters to get
    an access token from Strava API.

    Attributes:
        client_id:
            The ID of the application.
        client_secret:
            The secret key of the application.
        code:
            The code received from the authorization
            server.
        grant_type:
            The type of grant. This is always
            "authorization_code" for this application
    """

    client_id: int
    client_secret: str
    code: str
    grant_type: str = "authorization_code"  # This is the default value


class StravaGetTokenResponse(StravaBaseModel):
    """
    Model with the request parameters needed
    when getting an access token from Strava API.
    It is used also when refreshing the token.

    The response contains more information
    than this model, but we're only interested
    in the access token, refresh token and
    expiration time.
    """

    access_token: str
    refresh_token: str
    expires_at: int


class StravaRefreshTokenRequest(StravaBaseModel):
    """
    Model with the request parameters to refresh
    an access token from Strava API.

    Attributes:
        client_id:
            The ID of the application.
        client_secret:
            The secret key of the application.
        refresh_token:
            The refresh token received from the
            authorization server.
        grant_type:
            The type of grant. This is always
            "refresh_token" for this application
    """

    client_id: int
    client_secret: str
    refresh_token: str
    grant_type: str = "refresh_token"  # This is the default value


class StravaGetActivitiesRequest(StravaBaseModel):
    """
    Model with the request parameters to get
    a list of activities from the Strava API.

    Attributes:
        before:
            An epoch timestamp to get activities
            before this time.
        after:
            An epoch timestamp to get activities
            after this time.
        page:
            The page number to get.
        per_page:
            The number of activities to get per page.
    """

    before: datetime | int | None
    after: datetime | int | None
    page: int
    per_page: int

    @model_validator(mode="after")
    def validate_before_after(self):
        """
        Cast before and after to epoch timestamps
        """

        if isinstance(self.before, datetime):
            self.before = int(self.before.timestamp())

        if isinstance(self.after, datetime):
            self.after = int(self.after.timestamp())

        return self
