from strava_client.enums.base import BaseEnum


class StravaSportType(BaseEnum):
    """
    Sport types supported by Strava.
    There are much more than what
    we have here.
    See https://developers.strava.com/docs/reference/#api-models-SportType
    """

    RUN = "Run"
    WALK = "Walk"
    SWIM = "Swim"
    RIDE = "Ride"
    SOCCER = "Soccer"
    TABLE_TENNIS = "TableTennis"
    WORKOUT = "Workout"
    WEIGHT_TRAINING = "WeightTraining"
