class ClusteringParameters(dict):
    def __init__(self):
        """
            Constructor of ClusteringParameters.
        """
        super().__init__()
        self["Algorithm"] = "KMeans"
        self["FilterENWords"] = False
        self["Deterministic"] = False

        self["NbClusters"] = 13
        self["WeightFctWords"] = 0
        self["WeightMathProps"] = 0

        self["WeightOPWithDR"] = 1
        self["WeightCW"] = 0
        self["WeightDR"] = 0
        self["DimOPWithDR"] = 10
        self["DimCW"] = 10
        self["DimDR"] = 10
