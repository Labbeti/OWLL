# OWL Learning
The goal is to create clusters on object properties in order to simplify building of ontologies.

The project is currently in development and all data files and models **are not committed**.

### Get started
This project requires **Python 3.7** and the following list of packages : 

Package | Version | Download | Other Links 
--- | --- | --- | ---
gensim | 3.7.3 | [Link](https://pypi.org/project/gensim/) | [Site](https://radimrehurek.com/gensim/index.html)
html5lib | 1.0.1 | [Link](https://pypi.org/project/html5lib/) 
matplotlib | 3.0.3 | [Link](https://pypi.org/project/matplotlib/) 
numpy | 1.16.3 | [Link](https://pypi.org/project/numpy/) 
owlready2 | 0.17 | [Link](https://pypi.org/project/Owlready2/) | [Doc](https://pythonhosted.org/Owlready2/)
rdflib | 4.2.2 | [Link](https://pypi.org/project/rdflib/) | [Doc](https://rdflib.readthedocs.io/en/stable/)
scikit-learn | 0.21.1 | [Link](https://pypi.org/project/scikit-learn/) | [Site](https://scikit-learn.org/stable/documentation.html)

Once everything is installed, run this command on a terminal in the project directory:
```python3 main.py``` (Mac, Linux) or ```py.exe main.py``` (Windows).

The OWLL terminal will start and allow you to generate results. 
Type ```help``` to show commands.

### Versions 
* Indev 0.1.11 (04/06/19)
  * Add "subClassOf" for class properties.
  * Add separator to run a sequence of commands in OWLL terminal.
  * Refactoring ontology classes and add interface "IOntology".
  * Still working on gensim. Try a clusterisation with "Doc2Vec".

* Indev 0.1.10 (03/06/19)
  * Refactoring code and add some comments in ontology classes.
  * Add "Get started" to README.
  * Rename "clust_op_names.txt" to "clusters_stats.txt"
  * Add "owll_gensim.py" for testing clustering with gensim distances.
  * Add arguments to commands for future advanced versions of the owll terminal.
  * Regenerate OPD and stats with 150 ontologies.

* Indev 0.1.9 (29/05/19)
  * Regenerate OPD with 151 ontologies.
  * Regenerate statistics with the new OPD.
  * Rework main.py with a new sub-terminal class for menu.
  * Change "opd.txt" format in order to be more readable.
  * Add label and subPropertyOf in OPCharacteristics for RdflibOntology.
  * Create function to compute statistics about roots in "stats.txt".

* Indev 0.1.8 (29/05/19)
  * Regenerate OPD with 151 ontologies.
  
* Indev 0.1.7 (28/05/19)
  * Update format of results for "owll_clust.py" and "owll_stats.py".
  * Testing gensim in order to compare sentences.
  * Ontology loading is now done in first with Rdflib.
  * Remove some ontologies with unusable object properties names.
  * Add new ontologies.
  * Working on extending OPD with Characteristics of Object Properties (not finished).
  * Rename "meta_results.txt" to "opd_meta.txt" and "extracted_words.txt" to "root_words_meta.txt".
  * Add "root_words.txt".

* Indev 0.1.6 (24/05/19)
  * Fix ```getOWLTriples()``` methods of OwlreadyOntology and RdflibOntology.
  * Clear "classif.txt" file and add file version.
  * Adapt "onto_clust.py" in order to delete the old functions in "tests.py".
  * Add menu for main.
  * Regenerate all results with 140 ontologies.
  
* Indev 0.1.5 (23/05/19) 
  * Fix bug when loading with rdflib. 
  * Regenerate opd with more ontologies and without unreadable ones.
  * Reworking project files `"onto_clust.py", "onto_opd.py" and "onto_typoclass.py".

### Additional notes
This project has been developped with PyCharm on Windows 10.
