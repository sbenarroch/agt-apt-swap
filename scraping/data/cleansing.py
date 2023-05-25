import pandas as pd
import sys
from logzero import logger


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Performs cleansing of a dataset in the format given by the scraper.

    Args:
        df: the dataset to clean
    Returns:
        clean_df: the dataset after cleansing
    """

    def preprocess_point_price(s: str) -> str:
        if "." in s:
            s_split = s.split(".")
            return str(s_split[0] + s_split[1][:3])
        if "€" in s:
            return s[:3]

        return s

    def preprocess_weird_surface(s: str) -> str:
        sb = ""
        i = 0
        while i < len(s) and s[i].isdigit():
            sb += s[i]
            i += 1

        return sb

    # Cities as str
    g_city = df["g-city"].astype(str)
    t_city = df["t-city"].astype(str)

    # Rents as float
    g_rent_str = df["g-rent"].astype(str).apply(lambda s: s.split(" ")[0])
    g_rent = pd.to_numeric(g_rent_str, errors="coerce")
    t_max_rent_str = df["t-max-rent"].astype(str).apply(preprocess_point_price)
    t_max_rent = pd.to_numeric(t_max_rent_str, errors="coerce")

    # Surfaces as float
    g_surf_str = df["g-surf"].astype(str).apply(lambda s: s.split(" ")[0])
    g_surf = pd.to_numeric(g_surf_str, errors="coerce")
    t_surf_min_str = df["t-surf-min"].astype(str).apply(preprocess_weird_surface)
    t_surf_min = pd.to_numeric(t_surf_min_str, errors="coerce")

    # Rooms as float
    g_rooms = pd.to_numeric(df["g-rooms"], errors="coerce")
    t_rooms = pd.to_numeric(df["t-rooms"], errors="coerce")

    clean_df = pd.DataFrame(
        {
            "g-city": g_city,
            "g-rent": g_rent,
            "g-surf": g_surf,
            "g-rooms": g_rooms,
            "t-city": t_city,
            "t-max-rent": t_max_rent,
            "t-surf-min": t_surf_min,
            "t-rooms": t_rooms,
        }
    )

    return clean_df


if __name__ == "__main__":
    path = sys.argv[1]
    df = pd.read_csv(path)
    clean_df = clean_dataset(df)
    clean_df.to_csv("./clean_data_tauschwohnung.csv")
