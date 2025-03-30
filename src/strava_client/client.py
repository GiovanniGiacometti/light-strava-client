from datetime import datetime
import re

from pydantic import TypeAdapter
from strava_client.constants import DEFAULT_SCOPES
from strava_client.enums.auth import StravaScope
from strava_client.models.api import StravaActivity
from strava_client.models.requests import (
    StravaGetActivitiesRequest,
    StravaGetTokenRequest,
    StravaGetTokenResponse,
    StravaRefreshTokenRequest,
)
from strava_client.models.settings import StravaSettings
import webbrowser
import requests


class StravaClient:
    """
    Tiny wrapper around the Strava API.
    """

    BASE_OAUTH_URL = "https://www.strava.com/oauth"
    BASE_SERVER_URL = "https://www.strava.com/api/v3"

    def __init__(self, scopes: list[StravaScope | str] | None = None):
        self.settings = StravaSettings()  # type: ignore

        if scopes is None:
            self.scopes = DEFAULT_SCOPES
        else:
            self.scopes = list(
                map(lambda x: StravaScope(x) if isinstance(x, str) else x, scopes)
            )

        self._verify_initialization()

    def get_activities(
        self,
        before: datetime | None = None,
        after: datetime | None = None,
        page: int = 1,
        per_page: int = 30,
    ) -> list[StravaActivity]:
        """
        Get the activities for the authenticated user.
        """

        self._verify_token()

        url = f"{self.BASE_SERVER_URL}/athlete/activities"

        # # Set the headers

        headers = {"Authorization": f"Bearer {self.settings.access_token}"}

        # Make the GET request
        response = requests.get(
            url,
            headers=headers,
            params=StravaGetActivitiesRequest(
                before=before,
                after=after,
                page=page,
                per_page=per_page,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to retrieve activities. Status code: {response.status_code}."
                f" Response: {response.text}"
            )

        list_act_adapter = TypeAdapter(list[StravaActivity])
        return list_act_adapter.validate_python(response.json())

    def _verify_token(self):
        """
        Verify whether the access token is still valid.
        If not, refresh it and update the settings.
        """

        if int(datetime.now().timestamp()) >= self.settings.expires_at:
            # Token expired

            strava_refresh_token_response = self._refresh_token()
            self._update_settings_and_dump(strava_refresh_token_response)

    def _update_settings_and_dump(self, response: StravaGetTokenResponse):
        """
        Update the settings after receiving a new access token
        and dump them to the file.
        """

        self.settings.access_token = response.access_token
        self.settings.refresh_token = response.refresh_token
        self.settings.expires_at = response.expires_at

        self.settings.dump()

    def _verify_initialization(self):
        """
        Verify whether the application was just created
        and needs to get authentication for the desired scopes.
        """

        if not self.settings.refresh_token:
            # Not initialized. Open the browser to let
            # the user grant scopes

            auth_code = self._request_auth_code()

            # Now get the access token, refresh token and expiration time
            strava_get_token_response = self._get_access_token(auth_code)

            self._update_settings_and_dump(strava_get_token_response)

    def _get_access_token(self, auth_code: str) -> StravaGetTokenResponse:
        """
        Get the access token, refresh token and expiration time
        by exchanging the authorization code.
        """

        response = requests.post(
            f"{self.BASE_OAUTH_URL}/token",
            data=StravaGetTokenRequest(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
                code=auth_code,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to get access token. Status code: {response.status_code}"
                f"Response: {response.text}"
            )

        return StravaGetTokenResponse.model_validate(response.json())

    def _request_auth_code(self) -> str:
        """
        Initialize the scopes for the application
        by requesting an authorization code.

        Returns:
            str:
                The authorization code.
        """

        # The composition of the URL is described here:
        # https://developers.strava.com/docs/getting-started/#oauth

        url = f"{self.BASE_OAUTH_URL}/authorize"  # base url for the OAuth process
        url += f"?client_id={self.settings.client_id}"  # add the client ID
        url += "&response_type=code"
        url += "&redirect_uri=http://localhost/exchange_token"  # redirect URI
        url += "&approval_prompt=force"
        url += f"&scope={StravaScope.to_query_string_list(self.scopes)}"

        # Open the browser to let the user grant the scopes
        webbrowser.open(url, new=0)

        # Get the url. The user might also skip this part,
        # obtain the code by themselves, paste it in the settings and
        # recreate the client.

        response_url = input(
            "Please paste the code obtained after granting the scopes: "
        )

        # Extract the code from the URL

        auth_code = re.search(r"code=(\w+)", response_url)

        if not auth_code:
            raise ValueError("Failed to extract the authorization code.")

        auth_code = auth_code.group(1)  # type: ignore

        return auth_code  # type: ignore

    def _refresh_token(self) -> StravaGetTokenResponse:
        """
        Refresh the access token.
        """

        if self.settings.refresh_token is None:
            raise ValueError("No refresh token provided")

        response = requests.post(
            f"{self.BASE_OAUTH_URL}/token",
            data=StravaRefreshTokenRequest(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
                refresh_token=self.settings.refresh_token,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to refresh token. Status code: {response.status_code}"
            )

        return StravaGetTokenResponse.model_validate(response.json())
