from src.models.ClusteringModel import ClusteringObserver
from src.util import dbg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy, QWidget
from src.controllers.IController import IController
from src.views.PieEventObserver import PieEventObserver


class PieEventHandler:
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
        self.obs.onClick(label)


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


class ViewPie(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IController):
        self.parent = parent
        self.controller = controller
        self.canvas = PieCanvas()
        self.handler = PieEventHandler()
        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.canvas)
        self.canvas.updatePie([[1]], ["Initialized"])
        self.handler.connect(self.canvas.getPie(), self.controller)

    def onClusteringEnded(self, clustersNames, centersNames):
        dbg("On Clustering ended")
        self.canvas.updatePie(clustersNames, centersNames)
        # Connect the pie each time
        self.handler.connect(self.canvas.getPie(), self.controller)
