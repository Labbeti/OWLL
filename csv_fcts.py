from time import time


DEBUG_MODE: bool = True


def load_vectors(filename: str, limit: int = 1_000_000) -> (map, int, int):
    start = time()
    file = open(filename, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, file.readline().split())
    data = {}
    i = 1
    for line in file:
        if DEBUG_MODE and i % 10000 == 0:
            print("§ DEBUG: Line: %7d / %7d" % (i, min(n, limit)))  # TODO: delete
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = list(map(float, tokens[1:]))
        i += 1
        if i >= limit:
            break
    file.close()
    end = time()
    print("§ Loading time for %s: %.2f" % (filename, end - start))
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
