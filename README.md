# OWL Learning
The goal is to create clusters on object properties in order to simplify building of ontologies.

The project is currently in development and all data files and models **are not committed**.


## Get started
#### Installation

This project requires **Python 3.7** and the following list of packages : 

Package | Version | Used to | Download | Documentation
:--- | :---: | --- | :---: | :---:
gensim | 3.7.3 | Compare OP names | [Link](https://pypi.org/project/gensim/) | [Doc](https://www.pydoc.io/pypi/gensim-3.2.0/autoapi/models/word2vec/index.html)
pyrdfa3 | 3.5.3 | Make Rdflib work | [Link](https://pypi.org/project/pyRdfa/) | [Doc](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.parsers.pyRdfa.html)
matplotlib | 3.0.3 | Plot clusters | [Link](https://pypi.org/project/matplotlib/) | [Doc](https://matplotlib.org/3.1.0/contents.html)
numpy | 1.16.3 | Manipulate arrays | [Link](https://pypi.org/project/numpy/) | [Doc](https://docs.scipy.org/doc/numpy/)
owlready2 | 0.17 | Read ontologies | [Link](https://pypi.org/project/Owlready2/) | [Doc](https://pythonhosted.org/Owlready2/)
rdflib | 4.2.2 | Read ontologies | [Link](https://pypi.org/project/rdflib/) | [Doc](https://rdflib.readthedocs.io/en/stable/)
scikit-learn | 0.21.1 | Clusterize | [Link](https://pypi.org/project/scikit-learn/) | [Doc](https://scikit-learn.org/stable/documentation.html)

> Some others packages dependances will be installed if you are using pip.

Once everything is installed, run this command on a terminal in the project directory:
```python main.py``` (Mac, Linux) or ```py.exe main.py``` (Windows).

The **OWLL terminal** will start and allow you to generate results. 
Type ```help``` to display the list of available commands.

#### Main commands *(Indev 0.1.12)* :

Command | Description
--- | ---
```typo``` | Basic classification with relational words of "Typologie des mots de liaisons"
```clust``` | Test of some clusterisation algorithms on object properties names with FastText.
```genopd``` | Regenerate Object Property Database (OPD) with the ontologies
```genstats``` | Update all statistics from OPD.
```gengensim``` | Try Agglomerative clusterisation with distance matrix generated with gensim.

## Versions 
* Indev 0.1.12 (06/06/19)
  * Add arguments for OWLL command "genopd".
  * Remove redundant enum ```LoadType``` and file "LoadType.py"
  * Fix bug when reading an ontology with Rdflib and Owlready2.
  * Add ```nbInstances```, ```domainOf``` and ```rangeOf``` for ClsProperties.
  * Remove ```nbInstances``` from OpProperties.
  * Add Thing URI for class properties in ontologies classes.
  * Rename "fileIO.py" to "file_io.py".
  * Add "\_\_init\_\_.py" like in a standard python project.
  * Add small class diagram in "IOntology.py".
  * Test graphviz to show graphs, but we cannot modify it with a GUI.
  * Regenerate OPD and stats with 150 ontologies.
  * Fix gensim clusters generation with Tfidf and Doc2Vec.
  * Update "Get started" of README.
  * Generate gensim results in "results/gensim". The distance matrix is too big to be committed in github.

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
  * Rework `"main.py" with a new sub-terminal class for menu.
  * Change "opd.txt" format in order to be more readable.
  * Add ```label``` and ```subPropertyOf``` in OPCharacteristics for RdflibOntology.
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
