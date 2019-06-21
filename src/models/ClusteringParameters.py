class ClusteringParameters(dict):
    def __init__(self):
        super().__init__()
        self["NbClusters"] = 13
        self["WeightFctWords"] = 0
        self["WeightMathProps"] = 0
        self["WeightContentWords"] = 0
        self["WeightWordsWithDR"] = 1
        self["WeightDR"] = 0
        self["Algorithm"] = "KMeans"
        self["FilterENWords"] = False
        self["DimD2VModel"] = 100
