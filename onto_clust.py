
from csv_fcts import *
from onto_classes.Ontology import Ontology


def get_dataset(filepath_onto):
    onto = Ontology(filepath_onto)
    op_names = onto.getObjectProperties()

    dataset = []
    for name in op_names:
        pass
    # TODO : get the code for clust


def clust_object_properties_on_names():
    filepath_onto = "data/ontologies/dbpedia_2016-10.owl"
    filepath_ft = "data/fasttext/wiki-news-300d-1M.vec"
    limit = 30_000

    data, _, dim = load_vectors(filepath_ft, limit)

    nb_clusters = 10  # NOTE: max is currently 10 because we have only 10 differents colors


if __name__ == "__main__":
    clust_object_properties_on_names()
