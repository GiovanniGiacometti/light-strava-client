from pydantic import BaseModel, ConfigDict


class StravaBaseModel(BaseModel):
    """
    Base model for all Strava models.
    """

    model_config = ConfigDict(extra="allow")
