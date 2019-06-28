from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from src.controllers.IClusteringController import IClusteringController
from src.controllers.PieEventObserver import PieEventObserver
from src.models.ClusteringObserver import ClusteringObserver


class PieEventHandler:
    """
        Note: Original code come from https://pythonspot.com/pyqt5-matplotlib/
    """
    def __init__(self):
        self.obs = None
        self.pie = None
        self.ax = None

    def connect(self, pie, obs: PieEventObserver):
        self.obs = obs
        self.pie = pie
        self.ax = pie[0].axes
        fig = pie[0].figure
        fig.canvas.mpl_connect('button_press_event', self.onClick)

    def onClick(self, event):
        if event.inaxes != self.ax:
            return

        label = "ERROR"
        for w in self.pie:
            (hit, _) = w.contains(event)
            if hit:
                label = w.get_label()
                break
        self.obs.onClusterClick(label)


class PieCanvas(FigureCanvas):
    def __init__(self):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        self.elements = None

        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.show()

    def updatePie(self, clustersNames: list, centersNames: list):
        total = sum([len(cluster) for cluster in clustersNames])
        proportions = [len(cluster) / total for cluster in clustersNames]
        labels = centersNames

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.elements = ax.pie(proportions, labels=labels, explode=[0.1 for _ in range(len(proportions))],
                               autopct='%1.1f%%', startangle=0, shadow=False)
        self.draw()

    def getPie(self):
        return self.elements[0]


class PieView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        """
            Constructor of PieView.
            :param parent: Parent widget of pie chart view. Must have set his layout.
            :param controller: Clustering controller of the application.
        """
        self.parent = parent
        self.controller = controller

        self.canvasWidget = QWidget()
        self.canvasLayout = QVBoxLayout()
        self.canvas = PieCanvas()
        self.handler = PieEventHandler()
        self.initUI()

    def initUI(self):
        """
            Private method for initialize interface.
        """
        self.parent.layout().addWidget(self.canvasWidget)
        self.canvasWidget.setLayout(self.canvasLayout)
        self.canvasLayout.addWidget(self.canvas)
        self.canvas.updatePie([[1]], ["uninitialized"])
        self.handler.connect(self.canvas.getPie(), self.controller)

    def update(self):
        """
            Private method for update the pie chart.
        """
        self.canvas.updatePie(self.controller.getModelClusters(), self.controller.getModelCenters())
        self.handler.connect(self.canvas.getPie(), self.controller)

    def onClusteringBegan(self):
        """
            Override
        """
        pass

    def onClusteringEnded(self):
        """
            Override
        """
        self.update()

    def onModelLoaded(self):
        """
            Override
        """
        self.update()
