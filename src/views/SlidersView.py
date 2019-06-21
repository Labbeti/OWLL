from PyQt5.QtWidgets import QWidget, QGridLayout, QSlider, QLabel, QGroupBox, QHBoxLayout
from PyQt5.QtCore import Qt
from src.controllers.IController import IController
from src.util import dbg
from src.models.ClusteringModel import ClusteringObserver


SLIDER_FLOAT_PRECISION = 100
LABEL_FLOAT_FORMAT = "%.2f"


class SlidersView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IController):
        self.parent = parent
        self.controller = controller

        self.slidersWidget = QWidget(parent)
        self.slidersLayout = QGridLayout(self.slidersWidget)

        self.slidersConfig = {
            # "name": (def, min, max, format, denumerator)
            #          0    1    2    3       4
            "NbClusters": (10, 1, 100, "%d", 1),
            "WeightWordsWithDR": (1, 0, 1 * SLIDER_FLOAT_PRECISION, LABEL_FLOAT_FORMAT, SLIDER_FLOAT_PRECISION),
            "WeightContentWords": (0, 0, 1 * SLIDER_FLOAT_PRECISION, LABEL_FLOAT_FORMAT, SLIDER_FLOAT_PRECISION),
            "WeightFctWords": (0, 0, 1 * SLIDER_FLOAT_PRECISION, LABEL_FLOAT_FORMAT, SLIDER_FLOAT_PRECISION),
            "WeightMathProps": (0, 0, 1 * SLIDER_FLOAT_PRECISION, LABEL_FLOAT_FORMAT, SLIDER_FLOAT_PRECISION),
            "WeightDR": (0, 0, 1 * SLIDER_FLOAT_PRECISION, LABEL_FLOAT_FORMAT, SLIDER_FLOAT_PRECISION),
        }
        self.slidersAndLabels = {}
        for name in self.slidersConfig.keys():
            slider = QSlider(Qt.Horizontal)
            valueLabel = QLabel()
            self.slidersAndLabels[name] = (slider, valueLabel)

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.slidersWidget)

        i = 0
        j = 0
        sizeX = 4
        k = 0
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            dbg("Name = ", name)
            layout = QHBoxLayout()
            group = QGroupBox(name)
            group.setLayout(layout)
            layout.addWidget(valueLabel)
            layout.addWidget(slider)

            self.slidersLayout.addWidget(group, i, j)
            def_ = self.slidersConfig[name][0]
            min_ = self.slidersConfig[name][1]
            max_ = self.slidersConfig[name][2]
            format_ = self.slidersConfig[name][3]
            factor = self.slidersConfig[name][4]

            slider.setMinimum(min_)
            slider.setMaximum(max_)
            slider.setValue(def_ * factor)
            valueLabel.setText(format_ % (def_ / (max_ - min_)))
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.onSliderValueChanged)
            j += 1
            if j >= sizeX:
                j = 0
                i += 1
            k += 1
        self.updateAllLabels()

    def onSliderValueChanged(self, val):
        dbg("Slider released = ", val)
        # TODO : how to known which slider has been moved ?
        self.updateAllLabels()

    def onClusteringEnded(self, _, __):
        dbg("SlidersView: Clustering ended ")
        self.updateAllSliders()
        self.updateAllLabels()

    def updateAllSliders(self):
        # Update all sliders with model parameters
        params = self.controller.getModelParams()
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            factor = self.slidersConfig[name][4]
            slider.setValue(params[name] * factor)

    def updateAllLabels(self):
        # Update all labels with sliders values
        for name, (slider, valueLabel) in self.slidersAndLabels.items():
            format_ = self.slidersConfig[name][3]
            denum = self.slidersConfig[name][4]
            valueLabel.setText(format_ % (slider.value() / denum))

    def getSlidersValues(self):
        return {name: (slider.value() / self.slidersConfig[name][4])
                for name, (slider, _) in self.slidersAndLabels.items()}
