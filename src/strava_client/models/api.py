from datetime import datetime
from strava_client.enums.api import StravaSportType
from strava_client.models.base import StravaBaseModel


# Information about the Strava API can be found here:
# https://developers.strava.com/docs/reference/


class MetaAthlete(StravaBaseModel):
    """
    Strava athlete model, containing only the ID.
    """

    id: int


class StravaActivity(StravaBaseModel):
    """
    Model holding information about a Strava activity.
    In Strava it's actually called "SummaryActivity"
    (https://developers.strava.com/docs/reference/#api-models-SummaryActivity)
    """

    id: int
    external_id: str | None = None
    name: str  # The name of the activity
    athlete: MetaAthlete
    distance: float
    moving_time: int  # in seconds
    elapsed_time: int  # in seconds
    total_elevation_gain: float
    elev_high: float | None = None  # sometimes missing
    elev_low: float | None = None  # sometimes missing
    sport_type: StravaSportType
    start_date: datetime
    start_date_local: datetime
    timezone: str
    average_speed: float
    max_speed: float
    start_latlng: list[float]
    end_latlng: list[float]
