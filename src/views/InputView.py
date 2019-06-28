from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QGroupBox, QCheckBox, QPushButton, QLabel
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.models.ClusteringObserver import ClusteringObserver


class InputView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        """
            Constructor of InputView.
            :param parent: Parent widget of input view. Must have set his layout.
            :param controller: Clustering controller of the application.
        """
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
        """
            Private method for initialize interface.
        """
        self.parent.layout().addWidget(self.inputWidget)
        self.inputWidget.setLayout(self.inputLayout)

        self.inputLayout.addWidget(self.opLineEdit)
        self.inputLayout.addWidget(self.domainLineEdit)
        self.inputLayout.addWidget(self.rangeLineEdit)
        self.inputLayout.addWidget(self.checkBoxesWidget)
        self.inputLayout.addWidget(self.submitButton)
        self.inputLayout.addWidget(self.resultLabel)

        self.opLineEdit.setPlaceholderText("Object property name")
        self.domainLineEdit.setPlaceholderText("Domain")
        self.rangeLineEdit.setPlaceholderText("Range")

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
        """
            Method called when user want to submit an object property.
        """
        mathProps = {propName: checkBox.isChecked() for propName, checkBox in self.checkBoxes.items()}
        self.controller.submitOpToModel(
            self.opLineEdit.text(), self.domainLineEdit.text(), self.rangeLineEdit.text(), mathProps)

    def onClusteringBegan(self):
        """
            Override
        """
        self.setEnabled(False)
        self.resultLabel.setText("")

    def onClusteringEnded(self):
        """
            Override
        """
        self.setEnabled(True)

    def onModelLoaded(self):
        """
            Override
        """
        self.resultLabel.setText("")
        self.setEnabled(False)

    def onSubmitResult(self, centerName: str, nearest: str):
        """
            Override
        """
        self.resultLabel.setText("Cluster associated:\n\t" + centerName + "\nNearest name:\n\t" + nearest)

    def setEnabled(self, enable: bool):
        """
            Activate or deactivate the InputView.
            :param enable: True if you want to activate the view.
        """
        self.inputWidget.setEnabled(enable)
        if enable:
            self.inputWidget.setToolTip("Check in which cluster this object property is. It can be a object property "
                                        "not existant in the current model.")
        else:
            self.inputWidget.setToolTip("Model must be updated (NOT LOADED) for submit an object property.")
