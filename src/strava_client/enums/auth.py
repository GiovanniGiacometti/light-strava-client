from __future__ import annotations

from strava_client.enums.base import BaseEnum


class StravaScope(BaseEnum):
    """
    Enum class containing all the possible
    Strava scopes.

    List comes from here: https://developers.strava.com/docs/authentication/

    Notice that we include all possible scopes but
    only support read operations in the client.
    """

    READ = "read"
    READ_ALL = "read_all"
    PROFILE_READ_ALL = "profile:read_all"
    PROFILE_WRITE = "profile:write"
    ACTIVITY_READ = "activity:read"
    ACTIVITY_READ_ALL = "activity:read_all"
    ACTIVITY_WRITE = "activity:write"

    def to_query_string(self) -> str:
        """
        Convert the enum to a query string.
        """
        return self.value

    @staticmethod
    def to_query_string_list(scopes: list[StravaScope]) -> str:
        """
        Convert the enum to a query string.
        """
        return ",".join([scope.to_query_string() for scope in scopes])
