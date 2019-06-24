# OWL Learning
The goal is to create clusters on object properties in order to simplify building of ontologies.

The project is currently in development and all data files and models **are not committed**.


## Get started
### Installation

This project requires **Python 3.7** and the following list of packages : 

Package | Version | Used to | Download | Documentation
:--- | :---: | --- | :---: | :---:
Cython | 0.29.10 | Optimize packages | [Link](https://pypi.org/project/Cython/) | [Doc](https://cython.readthedocs.io/en/latest/)
gensim | 3.7.3 | Compare OP names | [Link](https://pypi.org/project/gensim/) | [Doc](https://www.pydoc.io/pypi/gensim-3.2.0/autoapi/models/word2vec/index.html)
pyrdfa3 | 3.5.3 | Make Rdflib work | [Link](https://pypi.org/project/pyRdfa/) | [Doc](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.parsers.pyRdfa.html)
matplotlib | 3.0.3 | Plot clusters | [Link](https://pypi.org/project/matplotlib/) | [Doc](https://matplotlib.org/3.1.0/contents.html)
numpy | 1.16.3 | Manipulate arrays | [Link](https://pypi.org/project/numpy/) | [Doc](https://docs.scipy.org/doc/numpy/)
owlready2 | 0.18 | Read ontologies | [Link](https://pypi.org/project/Owlready2/) | [Doc](https://pythonhosted.org/Owlready2/)
rdflib | 4.2.2 | Read ontologies | [Link](https://pypi.org/project/rdflib/) | [Doc](https://rdflib.readthedocs.io/en/stable/)
scikit-learn | 0.21.1 | Clusterisation algorithms | [Link](https://pypi.org/project/scikit-learn/) | [Doc](https://scikit-learn.org/stable/documentation.html)
PyQt5 | 5.12.2 | User interface | [Link](https://pypi.org/project/PyQt5/) | [Doc](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

> Some others packages dependances will be installed if you are using pip.

Once everything is installed, run this command on a terminal in the project directory:
```python main.py```.

*This section will be updated when the new interface will be finished.*

## Indev versions notes
* Indev 0.2.2 (24/06/19)
  * Closing main window now close the ClusterView window.
  * Add clusters in file model.
  * Fix crash when loading a file model.
  * Add file menu bar to open and save model.
  * Remove second window, add text area on bottom of sliders.
  * Add scroll area for text.
  * Add filter english words option.
  * Refactoring OptionView in ParamsView and ButtonsView.
  * Add sliders configurations.
  * Refactoring inferVecs function in ClusteringModel.
  * Fix crash when loading.
  * Working on progression bar when updating model (not implemented yet).

* Indev 0.2.1 (21/06/19) --- BIG UPDATE ---
  * Rework interface with **PyQt5**.
  * Create an MVC pattern for interface.
  * Reworking project scripts and refactoring code.

* Indev 0.2.0 (19/06/19)
  * Testing histogram and pie chart in order to display gensim clusters results.
  * Save clusters in JSON format.
  * Running main now leads to GUI.
  * Create a new GUI for testing clusterisations.
  * Add Slider to modify weight for clusterisation vectors.
  * Add checkbox to test multiple clusterisations algorithms.
  * Show list of OP in clusters in GUI.
  * Add checkbox to filter non-english words.
  * Add text input for submit a word, but this feature is unstable and not finished yet.
  * Add Cython to dependances for increase speed of packages scikit-learn, gensim and owlready2.

* Indev 0.1.15 (14/06/19)
  * Add IRI columns for OPD.txt, merge domains and ranges for an OP in 1 line instead of create multiple lines for each domain / range.
  * Add fct words pairs statistics in "results/stats/pairs_sw.txt".
  * Regenerate OPD with 178 ontologies and 5585 OPs.
  * Regerate stats and gensim results.
  * Rename TenseVerb to TenseDetector.
  * Add test for TenseDetector.
  * Add generation of non-english words of OPD.
  * Add new test with gensim and a new classification with link words.
  * Add more docstrings in OPD.py.
  * Unify "OpProperties" class and "values" dict of OPD in "OpData" class.
  
* Indev 0.1.14 (12/06/19)
  * Add ```TenseVerb```, a class used to recognize the tense of a verb with the file "verb_conj.txt".
  * Move a part of "main.py" code in "OwllTerminal.py".
  * Working on a new clusterisation with domain, range and OP properties (functional, symmetric, etc...), temporary results are in file "clusters_extended.txt".
  * Add ```OPD```, a class created for manipulating the Object Property Database.
  * Rename ```Consts``` to ```Csts``` and "roots.txt" to "content_words.txt".
  * Add docstrings for documentation.
  * Remove "EDAM.owl" from OPD (contains unreadable domain and range).
  * Regenerate OPD with 178 ontologies and 5485 triples.
  * Regenerate stats and gensim results.
  
* Indev 0.1.13 (07/06/19)
  * Remove constant ```CONNECT_WORDS```, add function ```getWordsSearched()```.
  * Rename Config class and file to Consts.
  * Add default paths for all results and input files.
  * Extend ```split_input``` algorithm for allow spaces for paths betweens quotes and double quotes.
  * Add automatic test for ```split_input```.
  * Get more statistics and values for roots words in "owll_stats.py".
  * Remove some ontologies :
    * Non-english ontologies "IT_study1.owl" and "leo.owl" from OPD.
    * Ontology with unreadable object properties "protege.owl". 
  * Regenerate OPD with 147 ontologies and 4551 triples.
  * Up Owlready2 version 0.17 to 0.18.

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
