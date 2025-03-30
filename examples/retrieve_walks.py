from strava_client.client import StravaClient
from strava_client.enums.api import StravaSportType
from collections import defaultdict
import polars as pl
from strava_client.models.api import StravaActivity


if __name__ == "__main__":
    client = StravaClient()

    walks: list[StravaActivity] = []
    page_cnt = 1

    while True:
        # 200 should be the max
        activities = client.get_activities(page=page_cnt, per_page=200)

        print(f"Fetching page {page_cnt}, found {len(activities)} activities")
        page_cnt += 1
        if not activities:
            break

        # Filter the activities to retain only those that are walks
        walks.extend(filter(lambda x: x.sport_type == StravaSportType.WALK, activities))

    print(f"Found {len(walks)} walks")

    walk_infos = defaultdict(list)

    for walk in walks:
        walk_infos["date"].append(walk.start_date.strftime("%d/%m/%Y"))
        walk_infos["strava_url"].append(f"https://www.strava.com/activities/{walk.id}")
        walk_infos["start_latlng"].append(
            ", ".join(list(map(lambda val: str(round(val, 2)), walk.start_latlng)))
        )
        walk_infos["end_latlng"].append(
            ", ".join(list(map(lambda val: str(round(val, 2)), walk.end_latlng)))
        )

    pl.DataFrame(walk_infos).write_csv("walks.csv")
