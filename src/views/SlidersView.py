from PyQt5.QtWidgets import QWidget, QGridLayout, QSlider, QLabel, QGroupBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.models.ClusteringObserver import ClusteringObserver


class SlidersView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        """
            Constructor of SlidersView.
            :param parent: Parent widget of slider view. Must have set his layout.
            :param controller: Clustering controller of the application.
        """
        self.parent = parent
        self.controller = controller

        self.slidersWidget = QGroupBox()
        self.slidersLayout = QVBoxLayout()

        self.slidersAndLabels = {}
        self.slidersConfig = {
            "NbClusters": {
                "min": 1, "max": 100, "format": "%d",
                "factor": 1, "label": "Number of clusters",
                "tooltip": "Number of clusters used for clustering algorithm.",
            },
            "WeightFctWords": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "label": "Weight of the function words vector",
                "tooltip": "Weight of the function words vector.\n This vector is a binary vector of length %d.\n "
                           "It contains 3 values by function word for each position (prefix, suffix, infix) and 3 "
                           "values at the end for indicate if the vector contains a prefix, suffix or "
                           "infix.\n Function words are \"%s\"." %
                           (len(CST.WORDS.getWordsSearched()) * 3 + 3, ", ".join(CST.WORDS.getWordsSearched()))
            },
            "WeightMathProps": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "label": "Weight of the mathematical properties vector",
                "tooltip": "Weight of the mathematical properties vector.\n This vector is a binary vector of length "
                           "%d.\n Mathematical properties are \"%s\"." %
                           (len(CST.MATH_PROPERTIES), ", ".join(CST.MATH_PROPERTIES))
            },
            "WeightCW": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "label": "Weight of the content words vector",
                "tooltip": "Weight of the content words vector.\n This vector is inferred with content words. They "
                           "are a part of object property name without domain, range and function words.\n Ex: OP "
                           "\"isFatherOf\" has content word \"Father\"."
            },
            "DimCW": {
                "min": 0, "max": 300, "format": "%d",
                "factor": 1, "label": "Dimension of the content words vector",
                "tooltip": "Dimension of the content words vector.\n This vector is inferred with content words. They "
                           "are a part of object property name without domain, range and function words.\n Ex: OP "
                           "\"isFatherOf\" has content word \"Father\"."
            },
            "WeightOPWithDR": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "label": "Weight of the OP name with domain and range vector",
                "tooltip": "Weight of the OP name with domain and range vector.\n This vector is inferred with the "
                           "sentence structure \"domain op range\".\n Ex: OP \"isFatherOf\" between \"Person\" and "
                           "\"Person\" create the sentence \"Person is father of person\". "
            },
            "DimOPWithDR": {
                "min": 0, "max": 300, "format": "%d",
                "factor": 1, "label": "Dimension of the OP name with domain and range vector",
                "tooltip": "Dimension of the OP name with domain and range vector.\n This vector is inferred with the "
                           "sentence structure \"domain op range\".\n Ex: OP \"isFatherOf\" between \"Person\" and "
                           "\"Person\" create the sentence \"Person is father of person\". "
            },
            "WeightDR": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "label": "Weight of the domain and range vector",
                "tooltip": "Weight of the domain and range vector.\n This vector is inferred with the sentence "
                           "\"domain range\".\n Ex: OP \"isFatherOf\" between \"Person\" and \"Person\" create the "
                           "sentence \"person person\". "
            },
            "DimDR": {
                "min": 0, "max": 300, "format": "%d",
                "factor": 1, "label": "Dimension of the domain and range vector",
                "tooltip": "Dimension of the domain and range vector.\n This vector is inferred with the sentence "
                           "\"domain range\".\n Ex: OP \"isFatherOf\" between \"Person\" and \"Person\" create the "
                           "sentence \"person person\". "
            },
        }

        self.initUI()

    def initUI(self):
        """
            Private method for initialize the sliders.
        """
        self.parent.layout().addWidget(self.slidersWidget)
        self.slidersWidget.setLayout(self.slidersLayout)

        for name, config in self.slidersConfig.items():
            slider = QSlider(Qt.Horizontal)
            valueLabel = QLabel()

            group = QGroupBox(config["label"])
            layout = QHBoxLayout(group)
            layout.addWidget(slider)
            layout.addWidget(valueLabel)

            self.slidersAndLabels[name] = (slider, valueLabel)
            self.slidersLayout.addWidget(group)

            slider.setMinimum(config["min"])
            slider.setMaximum(config["max"])
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.onSliderValueChanged)
            group.setToolTip(config["tooltip"])

        self.updateAllSliders()
        self.updateAllLabels()

    def setEnabled(self, enable: bool):
        """
            Activate or deactivate the sliders.
            :param enable: True if you want to active the sliders.
        """
        self.slidersWidget.setEnabled(enable)

    def onSliderValueChanged(self, _):
        """
            Private method called when a slider is moved.
            :param _: new value of the slider, but we dont known which one.
        """
        # TODO : Find a way to update only the slider moded.
        # TODO : how to known which slider has been moved ?
        self.updateAllLabels()

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
        self.updateAllSliders()
        self.updateAllLabels()

    def onModelLoaded(self):
        """
            Override
        """
        self.updateAllSliders()
        self.updateAllLabels()

    def updateAllSliders(self):
        """
            Private method for update all sliders with model parameters
        """
        params = self.controller.getModelParams()
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            config = self.slidersConfig[name]
            slider.setValue(params[name] * config["factor"])

    def updateAllLabels(self):
        """
            Private method for update all sliders labels.
        """
        # Update all labels with sliders values
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            config = self.slidersConfig[name]
            valueLabel.setText(config["format"] % (slider.value() / config["factor"]))

    def getSlidersValues(self) -> dict:
        """
            Return the current sliders values in view.
            :return: a dict of sliders names (parameter names) and current slider value.
        """
        return {name: (slider.value() / self.slidersConfig[name]["factor"])
                for name, (slider, _) in self.slidersAndLabels.items()}
