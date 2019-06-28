from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QRadioButton, QGroupBox
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.models.ClusteringObserver import ClusteringObserver


class ParamsView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        """
            Constructor of ParamsView.
            :param parent: Parent widget of parameters view. Must have set his layout.
            :param controller: Clustering controller of the application.
        """
        self.parent = parent
        self.controller = controller

        self.paramsWidget = QGroupBox()
        self.paramsLayout = QVBoxLayout()

        self.radiosWidget = QWidget()
        self.radiosLayout = QVBoxLayout(self.radiosWidget)
        self.radiosButtons = []
        self.deterBox = QCheckBox()
        self.filterWordBox = QCheckBox()

        self.initUI()

    def initUI(self):
        """
            Private method for initialize interface.
        """
        self.parent.layout().addWidget(self.paramsWidget)

        for name in CST.CLUSTERING_ALGORITHMS_NAMES:
            self.radiosButtons.append(QRadioButton(name))
        self.radiosButtons[3].setChecked(True)  # KMeans by default
        for radioButton in self.radiosButtons:
            self.radiosLayout.addWidget(radioButton)
        self.radiosLayout.setSpacing(0)

        self.paramsWidget.setLayout(self.paramsLayout)
        self.paramsLayout.addWidget(self.radiosWidget)
        self.paramsLayout.addWidget(self.deterBox)
        self.paramsLayout.addWidget(self.filterWordBox)

        self.deterBox.setText("Deterministic")
        self.filterWordBox.setText("Filter Non-English words")
        self.filterWordBox.setChecked(True)

        self.radiosWidget.setToolTip("Choose the clustering algorithm.")
        self.filterWordBox.setToolTip("Filter the object properties names with at least 1 non-english word.")

        # Note: This function is disabled by default, it does not provide a real determinic results,
        # It allow just a detemrinistic clusterisation but not a deterministic vector inference.
        self.deterBox.hide()

    def setEnabled(self, enable: bool):
        """
            Activate or deactivate the ParamsView.
            :param enable: True if you want to activate the view.
        """
        self.paramsWidget.setEnabled(enable)

    def onClusteringBegan(self):
        """
            Override
        """
        self.setEnabled(False)

    def onClusteringEnded(self):
        """
            Override
        """
        self.setEnabled(True)

    def onModelLoaded(self):
        """
            Override
        """
        params = self.controller.getModelParams()
        algoName = params["Algorithm"]
        for radioButton in self.radiosButtons:
            radioButton.setChecked(radioButton.text() == algoName)
        self.deterBox.setChecked(params["Deterministic"])
        self.filterWordBox.setChecked(params["FilterENWords"])

    def getParamAlgo(self) -> str:
        """
            Getter of current selected algorithm.
            :return: the name of the algorithm.
        """
        clustAlgo = "NoAlgoSelected"
        for radioButton in self.radiosButtons:
            if radioButton.isChecked():
                clustAlgo = radioButton.text()
        return clustAlgo

    def getParamDeterministic(self) -> bool:
        """
            Getter of deterministic boolean parameter.
            :return: True if the deterministic box is checked.
        """
        return self.deterBox.isChecked()

    def getParamFilterWords(self) -> bool:
        """
            Getter of filterENWords boolean parameter.
            :return: True if the filterENWords box is checked.
        """
        return self.filterWordBox.isChecked()
