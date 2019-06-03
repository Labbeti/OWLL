from Config import *
from time import time
from util import prt
from util import split_name


# Note: quelques mots non trouvé dans FastText :
# ['copilote', 'primogenitor', 'sheading', 'coemperor', 'bourgmestre']
def load_vectors(filename: str, limit: int = 1_000_000) -> (map, int, int):
    start = time()
    file = open(filename, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, file.readline().split())
    data = {}
    i = 1
    for line in file:
        if i % 10000 == 0:
            prt("Reading FastText... (line %7d / %7d)" % (i, min(n, limit)))
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = list(map(float, tokens[1:]))
        i += 1
        if i >= limit:
            break
    file.close()
    end = time()
    prt("Loading time for %s: %.2f" % (filename, end - start))
    return data, n, d


def save_vectors(data, filename):
    file = open(filename, "w")
    n = len(data)
    d = len(list(data.values())[0])  # dim
    file.write("%s %s\n" % (n, d))

    for word, vector in data.items():
        tmp = str(list(vector))
        tmp = tmp[1:len(tmp) - 1]
        tmp = tmp.replace(",", "")
        file.write(word + " " + tmp + "\n")
    file.close()


def get_vec(name, data, dim):
    words = split_name(name)
    vecs = [(word.lower(), data.get(word.lower())) for word in words]
    vec_res = np.zeros(dim)
    nb_vecs_added = 0
    for word, vec in vecs:
        if vec is not None and (word not in Config.CONNECT_WORDS or len(vecs) == 1):
            vec_res += vec
            nb_vecs_added += 1

    if nb_vecs_added > 0:
        return vec_res / nb_vecs_added
    else:
        return None


def get_vecs(names, data, dim) -> (list, list):
    names_with_vec = []
    vecs = []
    for name in names:
        vec = get_vec(name, data, dim)
        if vec is not None:
            names_with_vec.append(name)
            vecs.append(vec)
    return names_with_vec, vecs
