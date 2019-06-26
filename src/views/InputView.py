from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QGroupBox, QCheckBox, QPushButton, QLabel
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.models.ClusteringObserver import ClusteringObserver


class InputView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        self.parent = parent
        self.controller = controller

        self.inputWidget = QGroupBox()
        self.inputLayout = QVBoxLayout()

        self.opLineEdit = QLineEdit()
        self.domainLineEdit = QLineEdit()
        self.rangeLineEdit = QLineEdit()
        self.checkBoxesWidget = QWidget()
        self.checkBoxesLayout = QVBoxLayout()
        self.checkBoxes = {}
        self.submitButton = QPushButton()
        self.resultLabel = QLabel()

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.inputWidget)
        self.inputWidget.setLayout(self.inputLayout)

        self.inputLayout.addWidget(self.opLineEdit)
        self.inputLayout.addWidget(self.domainLineEdit)
        self.inputLayout.addWidget(self.rangeLineEdit)
        self.inputLayout.addWidget(self.checkBoxesWidget)
        self.inputLayout.addWidget(self.submitButton)
        self.inputLayout.addWidget(self.resultLabel)

        self.checkBoxesWidget.setLayout(self.checkBoxesLayout)
        for propName in CST.MATH_PROPERTIES:
            checkBox = QCheckBox()
            checkBox.setText(propName)
            self.checkBoxesLayout.addWidget(checkBox)
            self.checkBoxes[propName] = checkBox
        self.submitButton.setText("Submit OP")
        self.submitButton.setMinimumHeight(CST.GUI.BUTTON_MIN_HEIGHT)
        self.submitButton.clicked.connect(self.onSubmitButton)
        self.setEnabled(False)

    def onSubmitButton(self):
        mathProps = {propName: checkBox.isChecked() for propName, checkBox in self.checkBoxes.items()}
        self.controller.submitOpToModel(
            self.opLineEdit.text(), self.domainLineEdit.text(), self.rangeLineEdit.text(), mathProps)

    def onClusteringBegan(self):
        self.setEnabled(False)
        self.resultLabel.setText("")

    def onClusteringEnded(self):
        self.setEnabled(True)

    def onModelLoaded(self):
        self.resultLabel.setText("")
        self.setEnabled(False)

    def onSubmitResult(self, centerName: str, nearest: str):
        self.resultLabel.setText("Cluster associated:\n\t" + centerName + "\nNearest name:\n\t" + nearest)

    def setEnabled(self, enable: bool):
        self.inputWidget.setEnabled(enable)
