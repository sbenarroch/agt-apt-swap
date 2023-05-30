import os
import pandas as pd
import networkx as nx
import sys
from itertools import combinations
from compatibiliy import compatible_ads
from tqdm import tqdm
from logzero import logger
import pickle5 as pkl
from datetime import datetime

ROOT_DATA = "../scraping/data"


def generate_graph_from_dataset(df: pd.DataFrame, city: str = None) -> nx.Graph:
    """Generates a graph of compatibilities between ads gathered in a dataset.

    The computation of the graph can be restricted to one city.

    Args
        df: the `DataFrame` object gathering all ads
        city: the city to restrict the dataset to

    Returns
        graph: a NetworkX graph with all ads as nodes and edges between 2 ads if they are compatible
    """
    if city:
        df = df[(df["g-city"] == city) & (df["t-city"] == city)]

    graph = nx.Graph()

    nodes_list = []
    for idx, row in df.iterrows():
        nodes_list.append((idx, row.to_dict()))

    graph.add_nodes_from(nodes_list)

    for idx1, idx2 in tqdm(combinations(graph.nodes, r=2)):
        if compatible_ads(graph.nodes[idx1], graph.nodes[idx2]):
            graph.add_edge(idx1, idx2)

    return graph


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(ROOT_DATA, sys.argv[1]), index_col="Unnamed: 0")
    city = None

    restricted = False

    if len(sys.argv) > 2:
        restricted = True

    if restricted:
        city = sys.argv[2]

    graph = generate_graph_from_dataset(df, city)

    logger.info(
        "Graph successfully generated. Number of possible exchanges: {}".format(
            len(list(graph.edges))
        )
    )

    if city:
        filename = "./data/graph_{date}_{city}.pickle".format(
            date=datetime.today().strftime("%Y_%m_%d"), city=city
        )
    else:
        filename = "./data/graph_{date}_global.pickle".format(
            date=datetime.today().strftime("%Y_%m_%d")
        )

    with open(filename, "wb+") as f:
        pkl.dump(graph, f)

    logger.info("Graph successfully pickled.")
