from strava_client.enums.auth import StravaScope


SETTINGS_FILE_NAME = ".strava.secrets"
DEFAULT_SCOPES = [
    StravaScope.READ,
    StravaScope.ACTIVITY_READ,
]
