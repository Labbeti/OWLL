import numpy as np
import owlready2 as owl


def sq_dist(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return np.sum(np.subtract(v1, v2)**2)


def get_obj_prop_names(onto: owl.Ontology) -> list:
    obj_prop = list(onto.object_properties())
    obj_prop_names = [str(name)[len(onto.name)+1:] for name in obj_prop]
    return obj_prop_names


# 'a list list -> 'a list
def reshape(l: list) -> list:
    res = []
    for sublist in l:
        res += sublist
    return res