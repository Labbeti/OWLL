from src.util import prt
import matplotlib.pyplot as plt


class PieEventHandler:
    def __init__(self, p, clusters, centersNames):
        self.pie = p
        self.fig = p[0].figure
        self.ax = p[0].axes
        self.fig.canvas.mpl_connect('button_press_event', self.onPress)
        self.clusters = clusters
        self.centersNames = centersNames
        self.text = None

    def onPress(self, event):
        if event.inaxes != self.ax:
            return

        label = ""
        for w in self.pie:
            (hit, _) = w.contains(event)
            if hit:
                label = w.get_label()
                break

        indCluster = -1
        for i, center in enumerate(self.centersNames):
            if center == label:
                indCluster = i
        if indCluster != -1:
            content = "\n".join(set(self.clusters[indCluster]))
            prt("Cluster: %s" % (", ".join(set(self.clusters[indCluster]))))

            if self.text is not None:
                self.text.set_visible(False)

            self.text = self.fig.text(0.01, 0.05, content, bbox=dict(facecolor='white', alpha=0.5, edgecolor='red'))
            self.text.set_fontsize(8)
            plt.show()
