import sys
import pandas as pd
from logzero import logger


def check_data(df: pd.DataFrame) -> None:
    """Performs some unitary tests on the dataset to check the proportion of missing data

    Args
        df: the dataframe tu check
    Returns
        None: only prints
    """

    count_any, count_all = 0, 0
    n = len(df)

    for i, row in df.iterrows():
        if (row == "N/A").any():
            count_any += 1
        if (row == "N/A").all():
            count_all += 1

    logger.info(
        "Unitary tests on dataset:/n Partially empty rows: {any}, {any_prop:2f}%\n Empty rows: {all}, {all_prop:2f}%".format(
            any=count_any,
            any_prop=count_any / n * 100,
            all=count_all,
            all_prop=count_all / n * 100,
        )
    )


if __name__ == "__main__":
    path = sys.argv[1]
    df = pd.read_csv(path)
    check_data(df)
