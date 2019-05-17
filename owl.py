
import owlready2 as owl
import rdflib as rdf


# Return the list of object properties names.
def get_object_properties(filepath: str) -> list:
    try:
        return __owlready2_get_object_properties(filepath)
    except owl.base.OwlReadyOntologyParsingError:
        print("§ Loading \"%s\" with Owlready2 has failed. Trying with rdflib: " % filepath)
        return __rdflib_get_object_properties(filepath)


# Use OwlReady2 to read the ontology.
# Warning: Does not work with some OWL format like Turtle
def __owlready2_get_object_properties(filepath: str) -> list:
    onto = owl.get_ontology(filepath)
    onto.load()
    obj_prop = list(onto.object_properties())
    # Clean ontology name for each property
    obj_prop_names = [str(name)[len(onto.name)+1:] for name in obj_prop]
    return obj_prop_names


# Use Rdflib to read the ontology.
# Warning: Not verified for all types of object properties.
def __rdflib_get_object_properties(filepath: str) -> list:
    graph = rdf.Graph()
    graph.load(filepath)
    names = []
    for s, p, o in graph:
        # Patterns:
        # - s type ObjectProperty
        # TODO : search for anothers patterns ?
        # - s type http://www.w3.org/2002/07/owl#FunctionalProperty ? non car owlready2 ne considère pas pour dbpedia
        if p.toPython() == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" \
                and o.toPython() == "http://www.w3.org/2002/07/owl#ObjectProperty":
            name = s.toPython()
            index = max(name.rfind("#"), name.rfind("/"))
            name = name[index+1:]
            if name not in names:
                names.append(name)
    return names
