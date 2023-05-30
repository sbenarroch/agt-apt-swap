from typing import Dict


def compatible_ads(ad1: Dict, ad2: Dict) -> bool:
    """For 2 ads int the `tauschwohnung.de` format, tests if they would be suitable for exchange.

    Assumptions:
        The ads will be compatible if cities, rents, number of rooms and surfaces are compatible.
        For the number of rooms, equality is not required. Criterion is met if `(ad1["g-rooms"] >= ad2["t-rooms"]) and (ad2["g-rooms"] >= ad1["t-rooms"])`

    Args:
        ad1, ad2: two dicts providing the infos for the two ads to test

    Returns:
        a boolean saying whether the two ads are suitable for exchange or not

    """
    if (ad1["g-city"] == ad2["t-city"]) and (ad2["g-city"] == ad1["t-city"]):
        if (ad1["g-rent"] <= ad2["t-max-rent"]) and (
            ad2["g-rent"] <= ad1["t-max-rent"]
        ):
            if (ad1["g-surf"] >= ad2["t-surf-min"]) and (
                ad2["g-surf"] >= ad1["t-surf-min"]
            ):
                if (ad1["g-rooms"] >= ad2["t-rooms"]) and (
                    ad2["g-rooms"] >= ad1["t-rooms"]
                ):
                    return True

    return False
