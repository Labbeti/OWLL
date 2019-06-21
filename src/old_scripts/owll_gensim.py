from src.Csts import Csts
from src.old_scripts.ClustersManager import ClustersManager

import matplotlib.pyplot as plt


def gen_gensim_clust(_: list = None) -> int:
    clust = ClustersManager(Csts.Paths.OPD)
    clust.clusterize("results/gensim/clusters_2.json")
    clust.updateDraw()
    plt.close()
    return 0


if __name__ == "__main__":
    gen_gensim_clust()
