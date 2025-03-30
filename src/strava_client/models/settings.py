from pydantic_settings import BaseSettings, SettingsConfigDict
from strava_client.constants import SETTINGS_FILE_NAME
from pydantic import model_validator


class StravaSettings(BaseSettings):
    """
    Model holding all information needed to interact
    with Strava API.

    Attributes:
        client_id:
            The ID of the application.
        client_secret:
            The secret key of the application.
        access_token:
            The access token to authenticate the user.
            It's temporary, but can be refreshed.

        expires_at: int | None
            The time when the access token expires.
            Expressed as a Unix timestamp.
        refresh_token: str | None
            The token necessary to refresh the access token
            when it expires.
    """

    client_id: int
    access_token: str
    client_secret: str

    # These parameters are optional because this
    # settings model might be created before
    # the refresh token is available.

    refresh_token: str | None = None
    expires_at: int | None = None

    model_config = SettingsConfigDict(env_file=SETTINGS_FILE_NAME)

    @model_validator(mode="after")
    def check_expiration_params(self):
        """
        Ensure that both expires_at and refresh_token
        are either None or not None.
        """

        if (self.expires_at is None) != (self.refresh_token is None):
            raise ValueError(
                "Both expires_at and refresh_token must be either None or not None."
                f"Received expires_at: {self.expires_at}, refresh_token: {self.refresh_token}"
            )

        return self

    def dump(self) -> None:
        """
        Dump the settings to the secret file, as
        key-value pairs.
        """

        with open(SETTINGS_FILE_NAME, "w") as f:
            f.write(f"CLIENT_ID={self.client_id}\n")
            f.write(f"ACCESS_TOKEN={self.access_token}\n")
            f.write(f"CLIENT_SECRET={self.client_secret}\n")

            if self.refresh_token is not None:
                f.write(f"REFRESH_TOKEN={self.refresh_token}\n")

            if self.expires_at is not None:
                f.write(f"EXPIRES_AT={self.expires_at}\n")
