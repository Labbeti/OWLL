from PyQt5.QtWidgets import QWidget, QGridLayout, QSlider, QLabel, QGroupBox, QHBoxLayout
from PyQt5.QtCore import Qt
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.models.ClusteringObserver import ClusteringObserver


class SlidersView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        self.parent = parent
        self.controller = controller

        self.slidersWidget = QGroupBox()
        self.slidersLayout = QGridLayout()

        self.slidersAndLabels = {}
        self.slidersConfig = {
            "NbClusters": {
                "min": 1, "max": 100, "format": "%d",
                "factor": 1, "line": 0, "column": 0
            },
            "WeightFctWords": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "line": 1, "column": 0
            },
            "WeightMathProps": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "line": 2, "column": 0
            },
            "WeightOPWithDR": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "line": 0, "column": 1
            },
            "WeightCW": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "line": 0, "column": 2
            },
            "WeightDR": {
                "min": 0, "max": CST.GUI.SLIDER_PRECISION, "format": CST.GUI.SLIDER_LABEL_FORMAT,
                "factor": CST.GUI.SLIDER_PRECISION, "line": 0, "column": 3
            },
            "DimOPWithDR": {
                "min": 0, "max": 300, "format": "%d",
                "factor": 1, "line": 1, "column": 1
            },
            "DimCW": {
                "min": 0, "max": 300, "format": "%d",
                "factor": 1, "line": 1, "column": 2
            },
            "DimDR": {
                "min": 0, "max": 300, "format": "%d",
                "factor": 1, "line": 1, "column": 3
            },
        }

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.slidersWidget)
        self.slidersWidget.setLayout(self.slidersLayout)

        for name, config in self.slidersConfig.items():
            slider = QSlider(Qt.Horizontal)
            valueLabel = QLabel()

            group = QGroupBox(name)
            layout = QHBoxLayout(group)
            layout.addWidget(valueLabel)
            layout.addWidget(slider)

            self.slidersAndLabels[name] = (slider, valueLabel)
            self.slidersLayout.addWidget(group, config["line"], config["column"])

            slider.setMinimum(config["min"])
            slider.setMaximum(config["max"])
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.onSliderValueChanged)
            slider.setToolTip(name)

        self.updateAllSliders()
        self.updateAllLabels()

    def setEnabled(self, enable: bool):
        self.slidersWidget.setEnabled(enable)

    def onSliderValueChanged(self, _):
        # TODO : how to known which slider has been moved ?
        self.updateAllLabels()

    def onClusteringBegan(self):
        self.setEnabled(False)

    def onClusteringEnded(self):
        self.setEnabled(True)
        self.updateAllSliders()
        self.updateAllLabels()

    def onModelLoaded(self):
        self.updateAllSliders()
        self.updateAllLabels()

    def updateAllSliders(self):
        # Update all sliders with model parameters
        params = self.controller.getModelParams()
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            config = self.slidersConfig[name]
            slider.setValue(params[name] * config["factor"])

    def updateAllLabels(self):
        # Update all labels with sliders values
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            config = self.slidersConfig[name]
            valueLabel.setText(config["format"] % (slider.value() / config["factor"]))

    def getSlidersValues(self):
        return {name: (slider.value() / self.slidersConfig[name]["factor"])
                for name, (slider, _) in self.slidersAndLabels.items()}
