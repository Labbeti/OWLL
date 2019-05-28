# OWL Learning
The goal is to create clusters on object properties in order to simplify building of ontologies.

The project is currently in development and all data files and models <b>are not committed</b>.

### Versions 
* Indev 0.1.7 (28/05/19)
  * Update format of results for "owll_clust.py" and "owll_stats.py".
  * Testing gensim in order to compare sentences.
  * Ontology loading is now done in first with Rdflib.
  * Remove some ontologies with unusable object properties names.
  * Add new ontologies.
  * Working on extending OPD with Characteristics of Object Properties (not finished).
  * Rename "meta_results.txt" -> "opd_meta.txt", "extracted_words.txt" -> "root_words_meta.txt".
  * Add "root_words.txt".

* Indev 0.1.6 (24/05/19)
  * Fix getOWLTriples() methods of OwlreadyOntology and RdflibOntology.
  * Clear classif.txt file and add file version.
  * Adapt onto_clust.py in order to delete the old functions in tests.py.
  * Add menu for main.
  * Regenerate all results with 140 ontologies.
  
* Indev 0.1.5 (23/05/19) 
  * Fix bug when loading with rdflib. 
  * Regenerate opd with more ontologies and without unreadable ones.
  * Reworking project files onto_clust, onto_opd and onto_typoclass.
