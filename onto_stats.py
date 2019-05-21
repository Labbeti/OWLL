
from Ontology import Ontology
from time import time
from utils import *


def gen_name_base():
    dirpath = "../Onto_externes/"
    filenames = get_filenames(dirpath)[0:3]  # [6:] TODO TMP

    start = time()
    filepath_out = "data/object_properties_database.txt"
    out = open(filepath_out, "w", encoding='utf-8', errors='ignore')
    out.write("\n")
    out.write("%-30s %-30s %-30s %-30s\n\n" % ("Object property", "Domain", "Range", "File"))
    isloaded_owl = {}
    isloaded_rdf = {}
    nerrors = {}

    i = 1
    for filename in filenames:
        print("§ LOADING %s... (%d/%d)" % (filename, i, len(filenames)))
        filepath = join(dirpath, filename)
        ontology = Ontology(filepath)

        isloaded_owl[filename] = ontology.is_loaded_with_owlready2()
        isloaded_rdf[filename] = ontology.is_loaded_with_rdflib()
        nerrors[filename] = ontology.get_nb_errors()

        if ontology.is_loaded():
            print("§ Load of %s successfull" % filename)
            triples = ontology.get_triples()
            for s, p, o in triples:
                out.write("%-30s %-30s %-30s %-30s\n" % (p, s, o, filename))
        else:
            print("§ Load of %s has failed." % filename)

        i += 1
    out.close()
    end = time()

    print("§ File \"%s\" saved. " % filename)
    print("§ %-30s %-10s %-10s %-10s" % ("File", "Owlready2?", "Rdflib?", "NbErrors"))
    for filename in filenames:
        print("§ %-30s %-10s %-10s %-10d" % (filename, isloaded_owl[filename], isloaded_rdf[filename], nerrors[filename]))
    print("§ Time: %.2f" % (end - start))


def main():
    gen_name_base()


if __name__ == "__main__":
    main()
